# Gold set — stratified selection and blind export

## Summary

The final gold set is **179 frames** (149 Roboflow UAV + 30 VisDrone) for blind manual annotation in CVAT (Computer Vision Annotation Tool), with a subsequent IoU (intersection over union — a metric for the overlap of two boxes) computation against the source annotation. I selected 180 frames (150 Roboflow + 30 VisDrone), then excluded one Roboflow frame after annotation as not subject to annotation under the guideline (see the "Exclusions" section). The export contains only images, without annotations or provenance data. The correspondence manifest is kept separately from the images handed to the annotator.

- **Random seed:** `20260725` (fixed by the constant `RANDOM_SEED`).
- The final mapping of names to identifiers — [gold_set/gold_set_manifest.csv](../gold_set/gold_set_manifest.csv).

## Divergence between the expected and actual count of multi-object frames

At first I estimated the number of Roboflow frames with more than one target object at about 25 across the whole dataset and planned to include all such frames in the quota of 150. An actual check of the active Roboflow rows showed **133 such frames** (128 after excluding the pilot sample) — almost 5.3 times more than expected.

**Decision made:** I capped the quota on multi-object frames at **~25** (the constant `ROBOFLOW_MULTI_OBJECT_QUOTA = 25`), rather than "all." The procedure fills the rest (125 frames) randomly from the entire remaining Roboflow pool, including single-object and unused multi-object frames. This keeps multi-box frames from suppressing the sample's random component.

## Step 1 — Selection

### Exclusion of the pilot sample

Before assembling the gold set, I did a pilot review — 40 frames (20 VisDrone, 20 Roboflow) with the source annotation displayed. I did not create annotation at this stage.

The purpose of the review is to test the guideline rules — largely written speculatively — on real data and to close open questions: the confident-recognition threshold for small objects; the treatment of spinning rotor disks in the source annotation; cases not covered by the guideline; craft states outside flight.

The selection is deliberately non-random, but by the edges of the distributions: the goal of the review is to see difficult cases, not typical ones.

- VisDrone: 5 frames each with the highest and lowest nonzero density of target objects, 5 with the smallest median box size, 5 from the `artificial_light` category.
- Roboflow: 5 each with the smallest and largest box size, 5 with more than one object in the frame, 5 random.

The results of the review entered the final revision of [docs/annotation_guidelines.md](../docs/annotation_guidelines-en.md).

I excluded the frames of this review from both bases before selecting the gold set — **40 unique `sample_id`**.

**Blindness limitation.** The pilot review was not blind: the source annotation was shown to the annotator.

The exclusion of the pilot frames is built into the selection procedure itself: I formed both bases (VisDrone and Roboflow) with the pilot sample subtracted before stratification. The fact that the filter was applied is confirmed by the base numbers in the report itself: the number of available Roboflow multi-object frames after exclusion is 128 against 133 in the full active set (the "Roboflow UAV" section below). So the intersection of the pilot sample with the gold set is zero by construction.

The limitation is elsewhere: the pilot's composition cannot be independently re-verified by name, by `sample_id`. I did not keep an artifact with the exact list of 40 pilot-selection sample_id values, and the selection itself was built from object annotations in FiftyOne, which are also not saved as repository files. It is impossible, with the available materials, to check row by row that exactly these 40 sample_id values match those subtracted from the bases. One can rely only on the fact that the exclusion procedure was applied (confirmed by the base numbers above), not on a by-name list.

**Process conclusion.** Intermediate samples (here — the composition of the pilot review) should be saved to a file at the moment of assembly, not only used in place: without a saved artifact, the procedure cannot be verified after the fact.

### Roboflow UAV — 150 frames selected, 149 in the final set

| Stratum / criterion | Selected |
|---|---|
| more than one object in the frame | 25 |
| random | 125 |
| **Total selected** | **150** |
| excluded after annotation (see "Exclusions") | −1 |
| **Total in the set** | **149** |

- Base: active Roboflow rows with the pilot sample subtracted.
- Multi-object frames available after excluding the pilot sample — 128 (of 133 in the full active set; the figure 133 is computed over the active base, not the full one).
- The multi-object quota is capped at 25 (see the divergence section above).
- I did not apply additional stratification by illumination and viewpoint. There is no illumination cut in the source: the `day` category is assigned to all 2,529 active rows wholesale, without applying the threshold (see [illumination_classification-en.md](../docs/illumination_classification-en.md)), so there is nothing to stratify by. Viewpoint is not annotated in the manifest, so it could not serve as a selection axis.

### VisDrone — 30 frames, stratified

The base is active VisDrone frames with ≥1 target object (car, van, truck, bus): **8,262** frames before excluding the pilot sample. The figure is reconciled with [class_distribution-en.md](class_distribution-en.md) — the same value, computed over the active base. Unlike Roboflow, where both values are given — 133 before and 128 after — the report does not separately record the base figure after excluding the pilot sample (see the section below).

The stratification axis is the density of target objects per frame: terciles by the number of target boxes (rank-based division into three equal groups), 10 frames per tercile.

| Density tercile | Selected (after all adjustments) |
|---|---|
| low | 10 (of which 3 are a replacement at step 2, see below) |
| medium | 10 |
| high | 10 |
| **Total** | **30** |

**Illumination control.** Random selection within the terciles initially gave only **2** `artificial_light` frames (the threshold is at least 4). So I made 2 replacements `day` → `artificial_light` within the "low" tercile — the only tercile where random selection came up short on AL frames (`artificial_light`) — preserving the 10/10/10 balance:

| Tercile | Removed (day) | Added (artificial_light) |
|---|---|---|
| low | `71254c28…f6cab` | `4c26b3ef…a03` |
| low | `77fa9bb9…fcba2` | `b06b2af0…b06` |

The actual number of `artificial_light` frames in the final VisDrone gold set is **5**: one of the step-2 replacements happened to land on an artificial_light frame.

## Step 2 — Size-coverage check (post-hoc)

Object size was not a selection axis. After selection, I checked that the distribution of the target boxes' shorter side (min-side) in the gold set is not shifted relative to the general population (by the active dataset, cut by source).

| Source | Percentile | Gold set, px | General population, px |
|---|---|---|---|
| VisDrone | p5 | 8.0 | 8.0 |
| VisDrone | p25 | 16.0 | 16.0 |
| VisDrone | p50 | 28.0 | 27.0 |
| VisDrone | p75 | 49.0 | 46.0 |
| VisDrone | p95 | 96.0 | 96.0 |
| Roboflow | p5 | 37.9 | 33.0 |
| Roboflow | p25 | 65.0 | 69.0 |
| Roboflow | p50 | 124.0 | 150.0 |
| Roboflow | p75 | 293.0 | 278.5 |
| Roboflow | p95 | 589.2 | 610.0 |

**Share of boxes < 20 px (small objects):**

| Source | Gold set | General population |
|---|---|---|
| VisDrone (before replacements) | 27.72% | 33.14% |
| VisDrone (after replacements) | **29.93%** | 33.14% |
| Roboflow | 1.12% | 0.92% |

### Replacements made at step 2

The initial share of small objects (< 20px) in the VisDrone gold set is 27.72% against 33.14% in the general population (a relative lag of ~16.3%). I judged the lag to require correction. This is an expert decision: no threshold for the acceptable divergence is formally set. I made **3 replacements** — the upper bound set in advance (`VISDRONE_SMALL_OBJECT_MAX_SWAPS = 3`): I replaced the "low" tercile frames with the largest median box size with frames of the same tercile with a median box size < 20 px. The frames added at step 1 for illumination control (`artificial_light`) are protected from being replaced again at this step.

| Tercile | Removed (median min-side, px) | Added (median min-side, px) |
|---|---|---|
| low | `f7483e11…878c` (206.0) | `7df6a98d…caeb5` (17.5) |
| low | `bdbf9536…4164d` (168.0) | `3700d56c…7dad` (14.0) |
| low | `de3047e1…77db5` (102.0) | `876e930d…678e` (13.0) |

After the replacements, the share of small objects rose to **29.93%** — substantially closer to the population share (33.14%). The 10/10/10 tercile balance is preserved, and the illumination control (5 artificial_light) is not violated.

**Roboflow.** Small objects are rare in the source, both in the gold set (1.12%) and in the general population (0.92%). The shares are comparable, so no special measures were needed. The fact is recorded without corrective actions.

## Step 3 — Blind export

- Exported **180 images** (outside `data/`), of which 179 are in the final set.
- The file names are a neutral sequential index (`gold_0001.jpg` … `gold_0180.jpg`), with no reference to the source, split, `sample_id`, or original file name. The index was assigned at the moment of export, and I did not renumber after excluding a frame, so the number `gold_0173` is absent from the set of 179 files.
- The images are re-encoded through Pillow rather than copied byte for byte, so the original's EXIF and metadata (potentially containing the source file path) are cleared. Check: `Image.getexif()` is empty.
- Annotations, GT boxes (GT — ground truth, the source's original annotation), and any of their traces are not part of the export.
- **The correspondence manifest** — `gold_set/gold_set_manifest.csv`: `sample_id → exported_filename → source → split`. It is kept separately from the images, **not handed to the annotator**, and is used only to match the results of the manual annotation with GT when computing IoU.

**Confirmation:**

- The number of exported images — **180** (150 Roboflow + 30 VisDrone). ✅
- The file names are unique — **180 unique**. ✅
- GT is present nowhere: not in the files, not in the names, not in EXIF or metadata. ✅
- The final composition of the set after exclusion — **179 files**, matching the number of rows in the correspondence manifest (149 `roboflow-uav` + 30 `visdrone`). ✅

### Structure of the set in the repository

The set is laid out by source:

| Path | Content |
|---|---|
| `gold_set/visdrone/` | 30 VisDrone images + `NOTICE.md` |
| `gold_set/roboflow/` | 149 Roboflow UAV images + `LICENSE.txt` |
| `gold_set/annotations/` | Project annotation, exported from CVAT in COCO format, in separate tasks by class |
| `gold_set/gold_set_manifest.csv` | Correspondence manifest |

The set is laid out by source because of the difference in license regimes: Roboflow UAV is distributed under CC BY 4.0, whereas VisDrone-DET declares no formal license and its distribution terms are not defined. The regimes are incompatible in one directory, so each source carries its own license file or NOTICE next to its images. The provenance and full decision text for each source are in [docs/sources_and_licenses.md](../docs/sources_and_licenses-en.md).

## Exclusions

- **`gold_0173.jpg`** (Roboflow, `sample_id` `9f6548588ffe2d6ecc0319a669b10a82d22c276036817bfdae638354cc99969a`) I excluded from the gold set: the frame contains an unrealistic image of a drone (a pictogram or non-photographic graphic), which is not subject to annotation under the guideline. In CVAT the frame contained no annotated objects — confirmed before exclusion.
- The frame is removed from `gold_set/gold_set_manifest.csv`, and the image is not part of the set. I did not change the numbering of the remaining files, to preserve the link with the annotation already done in CVAT, so the number `gold_0173` is absent from the set.
- The COCO export from CVAT was done before excluding the frame, so it retains a record of `gold_0173.jpg` with zero annotations: the Roboflow annotation file lists 150 images against 149 in the directory and in the correspondence manifest. I did not edit the export file: a manual edit would break its correspondence to the CVAT export.
- I did **not** make a replacement with another frame.
- **The final gold-set size is 179 frames (30 VisDrone + 149 Roboflow).**

## Final distribution by split (for reference, not a selection axis)

By the final composition of the set (179 frames), per the correspondence manifest:

| Source | train | val | test | Total |
|---|---|---|---|---|
| VisDrone | 23 | 4 | 3 | 30 |
| Roboflow | 117 | 20 | 12 | 149 |

The excluded frame belonged to the `test` split of the Roboflow source: before the exclusion, this split had 13 frames.

## Parameters used (for reproducibility)

```python
RANDOM_SEED = 20260725
ROBOFLOW_QUOTA = 150
ROBOFLOW_MULTI_OBJECT_QUOTA = 25
VISDRONE_QUOTA = 30
VISDRONE_PER_TERCILE = 10
VISDRONE_MIN_ARTIFICIAL_LIGHT = 4
VISDRONE_SMALL_OBJECT_PX = 20
VISDRONE_SMALL_OBJECT_POPULATION_SHARE = 0.33
VISDRONE_SMALL_OBJECT_MAX_SWAPS = 3
```

## Purpose of the selection constants

- **`ROBOFLOW_MULTI_OBJECT_QUOTA = 25`** — the upper bound on the number of Roboflow multi-object frames in the sample. It closes the risk that multi-box frames (128 available against the initially expected ~25) crowd out the sample's random component and make it unrepresentative of the source's typical, mostly single-object profile. The value 25 is an expert decision in reaction to the discovered divergence from the expectation (see the section above), not an independently recomputed quantity. There is no formal justification for this specific number.
- **`VISDRONE_PER_TERCILE = 10`** — the number of frames per object-density tercile. It ensures equal representation of low, medium, and high density in the sample of 30 VisDrone frames (30 / 3 = 10). The basis — `VISDRONE_QUOTA = 30` — is an expert decision dictated by the needed gold-set size, without a formal statistical justification.
- **`VISDRONE_MIN_ARTIFICIAL_LIGHT = 4`** — the minimum guaranteed number of artificial_light frames in the sample. It closes the risk that purely random selection within the terciles gives 0–1 frame of this illumination class and leaves the guideline rule about nighttime glare untested on the sample. The value 4 is an expert decision given the needed sample size, without a formal justification (why 4 rather than 3 or 5).
- **`VISDRONE_SMALL_OBJECT_PX = 20`** — the threshold for classifying an object as "small" in the size-coverage check (step 2). An expert decision, without a formal justification for choosing 20 px rather than 15 or 25.
- **`VISDRONE_SMALL_OBJECT_MAX_SWAPS = 3`** — the upper bound on the number of frame replacements at step 2. It limits the intervention into the already-formed stratified sample (terciles, artificial_light), so that correcting the small-object share does not blur the other control axes. An expert decision, without a formal justification for this specific value.
