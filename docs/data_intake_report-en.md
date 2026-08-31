# Data Intake Report — cv-dataset-pipeline

**Scope:** ingesting VisDrone-DET and Roboflow UAV through to the final deduplicated manifest; structuring and deduplication.

## 1. Data sources

The dataset combines two sources:

| Source | Rows | Format | Notes |
|---|---|---|---|
| VisDrone-DET (HuggingFace) | 8,629 | COCO annotations | Structured by sequences (video frames) |
| Roboflow UAV (`aicup-5yzqf/uav-ajf13`) | 4,202 | COCO annotations | train 2,944 / valid 842 / test 416, vendor splits |
| **Total** | **12,831** | | |

Image resolution varies across both sources — for example, 960×540 and 1360×765. This is a real property of the input data, and it affects bounding box (bbox) normalization.

## 2. Manifest structure

The single registry `manifest.parquet` stores one row per sample. A Pydantic schema validates each row; see [manifest_schema.py](../manifest_schema.py). The core columns: `sample_id` (SHA-256 of the file contents), `source`, `filepath`, `split`, `format`, `annotation_format`, `width`, `height`, `annotation_status`, `condition_tags`, `phash`, `ingested_at`.

`sample_id` is a content-addressable identifier (SHA-256 of the file bytes), not a row's primary key. The manifest contains 12,831 rows and 12,828 unique `sample_id` values: three pairs of rows share the same `sample_id`. Row uniqueness is provided by the `sample_id` + `filepath` pair — 12,831 unique pairs, with no collisions.

A shared `sample_id` between two rows follows directly from how the hash is built. It occurs exactly when two files are byte-identical, and it serves as a diagnostic sign of a duplicate. All three pairs that produce the 12,831-versus-12,828 divergence are the same 3 byte-identical files that the `exact_sha256` method found in Section 4. In each pair, one row is marked `dedup_status=duplicate`, `dedup_method=exact_sha256`, and the other remains canonical.

The two hashes serve different purposes:

- **SHA-256** catches byte-identical files.
- **`phash`** (perceptual hash) catches visually near-identical frames that differ at the byte level — re-encoding, adjacent video frames.

The pipeline builds the manifest by passing over the FiftyOne datasets for metadata and computes both hashes directly from the image bytes.

Deduplication (Section 4) extended the schema with the columns `dedup_status`, `duplicate_of`, `dedup_method`, `dedup_hamming_distance`, `dedup_decided_at`, as well as `sequence_id`, `split_before_resplit`, `split_reassigned`, `resplit_reason` (Section 3). The pipeline does not delete rows physically. Each exclusion is a flag with a documented reason, so the full history is available for audit.

## 3. Structural finding: split leakage

An early duplicate check (exact `phash` matches, Hamming distance 0) found 186 groups of visually identical frames — **1,064 rows**. The next check determined whether these groups crossed train/val/test boundaries and revealed the real problem: **111 of 186 groups (60%) spanned more than one split.**

Hamming distance here is the number of positions at which two perceptual hashes differ; zero means identical hashes.

The cause is not in duplicate handling but in split construction. Both source datasets assign train/val/test at the frame level, not the video level. So adjacent frames of one clip can land in different splits before the data ever reaches this pipeline.

**Investigation.** To recover `sequence_id`, the pipeline parsed filename patterns per source:

| Source | Pattern match rate | Sequences recovered |
|---|---|---|
| VisDrone | 100% (8,629/8,629) | 321 |
| Roboflow UAV | 60.8% (2,556/4,202) | 6 (video14–19) |

The remaining 1,646 Roboflow rows are standalone photos with no video or frame structure in their filenames (`pic_NNN`, `sceneNNN`, `yotoNNN`, bare `videoNNN`). The pipeline did not assign them a `sequence_id`, so as not to invent a structure that doesn't exist.

**Sequence-level leakage.** Multiple splits were spanned by:

- all 6 Roboflow sequences (100%) — 2,556 rows;
- 24 of 321 VisDrone sequences (7.5%) — 325 rows.

In total, the leakage affected 2,881 rows — almost three times the 1,064 rows the duplicate check initially found by `phash` (2,881 / 1,064 = 2.71). This confirms that the leakage was structural, not confined to duplicates.

**Resolution.** The pipeline reassigned each split-spanning sequence to the split holding the majority of its rows. The tie-break rule — test > val > train — was never needed, because no exact ties arose. Relocated: **802 rows: 774 Roboflow and 28 VisDrone**.

| Split | Before resplit, all ingested rows | After resplit, all ingested rows |
|---|---|---|
| train | 9,415 | 10,197 |
| val | 1,390 | 858 |
| test | 2,026 | 1,776 |

`phash`-group leakage dropped from 111 to 10 groups. These 10 are the unresolved rows among the 1,646 standalone Roboflow rows; the pipeline handled them individually by the same split-priority rule.

**Cross-source check.** A full pairwise comparison by Hamming distance between VisDrone and Roboflow UAV found no close duplicates: the nearest cross-source pair was at distance 10. This confirms that the sources are independent and there is no hidden content overlap.

## 4. Deduplication

Deduplication proceeded in stages. The pipeline checked each stage for split leakage before moving to the next.

**Stage A — exact matches (Hamming distance 0)**

| Method | Rows marked duplicate |
|---|---|
| `exact_sha256` (byte-identical files) | 3 |
| `phash_exact` (identical perceptual hash) | 875 |
| **Subtotal** | **878** |

The pipeline selects the canonical row by the alphabetically first `filepath` within each duplicate group.

**Stage B — near-duplicates (Hamming distance > 0)**

There is no natural distance threshold in the data: both populations showed smooth, continuous distributions rather than a clear break between "duplicate" and "different frames." Distances are always even — a property of the `phash` algorithm, not the data. I set the threshold (Hamming distance ≤ 6) by direct visual review of sampled pairs at candidate distances (2, 4, 6, 8, 10, 12) in FiftyOne.

The pipeline applied the threshold with two methods to two structurally different row populations:

- **Sequence rows** (11,185 rows, 327 sequences from both sources). The method is sequential thinning: each frame is compared to the last *kept* frame of its sequence, not the immediately preceding one. That keeps drift bounded relative to what actually remains.
- **Standalone rows** (1,646 rows, no sequence order). The method is full pairwise clustering with a chain-merge guard: a component is resolved automatically only if every pair within it is within the threshold. Components connected only through an intermediate row (A–B close, B–C close, A–C far) were held out by the pipeline rather than merged by force.

| Method | Rows marked duplicate |
|---|---|
| `phash_hamming_sequence` (sequence thinning) | 729 |
| `phash_hamming_pairwise` (clean clusters) | 40 |
| `phash_hamming_complete_linkage` (chain-merge resolution) | 39 |
| **Subtotal** | **808** |

The chain-merge guard flagged 18 components (87 rows). The pipeline re-clustered them with complete-linkage: a cluster forms only if *all* internal pairwise distances are within the threshold. The result: 25 valid clusters (39 duplicates + 25 canonical) and 23 singleton rows. The singletons did not share full mutual similarity with any other row, so they remained active and unresolved as duplicates.

**Residual pairs at the threshold.** The chain-merge guard leaves active the pairs that sit exactly at the threshold. Among the active rows, 7 such pairs remained at Hamming distance 6 (all Roboflow UAV; train↔val 4, train↔test 1, val↔test 2). Both rows of each pair belong to one of the 18 components sent for re-clustering, but to different sub-clusters. The minimum inter-cluster distance equals 6, the maximum exceeds the threshold, so the complete-linkage rule blocks the merge. This is a consequence of the rule itself, not a skipped procedure. The pipeline did not move these rows to duplicate.

## 5. Final dataset composition

| Status | Rows | % |
|---|---|---|
| Active | 11,145 | 86.9% |
| Duplicates (all methods) | 1,686 | 13.1% |
| **Total** | **12,831** | |

The deduplication subtotals reconcile: 878 (Stage A) + 808 (Stage B) = 1,686 duplicates.

Active rows by split:

| Split | Active rows |
|---|---|
| train | 8,558 |
| val | 817 |
| test | 1,770 |
| **Total** | **11,145** |

Downstream documents report all dataset-state counters over active rows. Breakdowns over all ingested rows refer to the state before deduplication.

Split-leakage checks (grouping `sample_id` and `phash` by split) returned zero at every stage, with no regressions after any step. I re-ran each deduplication script to confirm idempotency: a repeated pass marks nothing new.

**Check scope.** The check groups rows by exact `phash` match and by `sample_id`. By construction, it does not detect pairs within the near-duplicate threshold radius: the zero refers to exact matches, not to the entire Hamming-distance ≤ 6 zone. The residual of such pairs is described in Section 4 ("Residual pairs at the threshold").


## 6. Known limitations

- The `condition_tags` column (capture conditions: day/night, altitude, density) is not populated. Populating it is not part of structuring and deduplication.
- The 1,646 standalone Roboflow rows have no sequence-level leakage-protection guarantee. They are protected only by `phash` clustering, which catches visual near-duplicates. This is not the structural guarantee that sequence-based resplitting provides for the rest of the dataset.
- The pipeline marks duplicates, it does not remove them. Any downstream use of the dataset must filter explicitly on `dedup_status == "active"`. A naive `split == "test"` filter without this condition will still include rows marked as duplicates.
- The Hamming-distance ≤ 6 threshold is a documented decision, not a statistically obvious boundary. Revisit it if a later annotation review surfaces missed near-duplicates or overly aggressive merges.
- Cross-source overlap was checked once, on the current dataset snapshot. The check was not repeated when either source was later expanded.


## 7. State after structuring

- DVC (Data Version Control) versions the source data by source, and git versions the manifest. Data and manifest are synchronized by commit.
