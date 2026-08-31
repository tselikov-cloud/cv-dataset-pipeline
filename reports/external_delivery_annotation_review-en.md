# Visual review of annotation-policy compatibility — DUT Anti-UAV (criterion 6.4)

## Overview

**Status:** a non-threshold criterion (specification [docs/data_request_spec_lowlight_drone.md](../docs/data_request_spec_lowlight_drone-en.md), section 6.4). It does not affect the acceptance verdict: the delivery is already rejected on the threshold criteria 6.3 (4.65% low-light against the required 30%) and 6.5 (78.71% internal duplicates, 27 cross-source overlaps; see [external_delivery_acceptance-en.md](external_delivery_acceptance-en.md)). The check is performed for completeness of the delivery's characterization.

I did the visual review of 64 selected images by hand. The results are in the "Visual review results" section.

## Selection method

### Volume and seed

- **Sample volume:** 64 images.
- **Random seed:** `20260808`, fixed by a selection constant.
- Selection table: [data/review_sample_6_4.csv](data/review_sample_6_4.csv).

### Step 1 — deduplication of the selection base

The delivery is 78.71% near-duplicates (Hamming ≤ 6 by phash — perceptual hash, see criterion 6.5). So a random selection from all 10,000 images would give mostly adjacent frames of one clip. Before stratification, I built a deduplicated base:

- Grouping all 10,000 images by phash (`imagehash.phash`, the same method as at the data-structuring stage and in criterion 6.5) with a Hamming ≤ 6 threshold, union-find algorithm.
- One representative per group — the lexicographically first `filepath` (a deterministic, reproducible choice).
- **Result: 2,129 representatives** out of 10,000. This is consistent with the 78.71% redundancy found in criterion 6.5: 10,000 × (1 − 0.7871) ≈ 2,129.
- Of these, 2,126 images with ≥1 annotated object, 3 without objects (the same 3 frames without objects as in criterion 6.6).

I perform all further stratification on this base of 2,129 images, not on the full 10,000.

### Step 2 — stratification

Three independent axes. Selection proceeds sequentially (axis 1 → axis 2 → guarantees on axis 3 and additional conditions), with checking and restoration of priorities after each step.

**Axis 1 — object size.** Terciles (rank-based division into 3 equal groups) by the minimum shorter box side per frame; for multi-object frames — the minimum over all objects in the frame. Computed on the deduplicated base. The target division is 21–22 images per tercile. 64 is not divisible by 3 without a remainder, so I added the remainder to the lower tercile as the most diagnostically important for the specification section 3 requirement on the share of small objects.

**Axis 2 — brightness.** Terciles by `brightness_median_v` (the same brightness computation as in criterion 6.3), computed on the deduplicated base. The lower brightness tercile is required to include at least one image below the calibrated low-light threshold (49.0, see criterion 6.3), if any exist in the deduplicated base. There are 20 such images in the base out of 2,129.

**Axis 3 — resolution.** Proportional to the distribution in the deduplicated base — not a separate equal tercile split, but a natural result of random selection within axes 1–2, with a guarantee of at least 3 images of atypical resolution (not 1920×1080 and not 1280×720).

The distribution of resolutions in the deduplicated base (2,129 representatives) differs from the distribution over the full delivery (10,000 images, see [external_delivery_inventory-en.md](external_delivery_inventory-en.md)). In the full delivery, 1920×1080 is 79.37%, 1280×720 is 17.85%. In the deduplicated base the proportion is reversed: 1280×720 makes up the majority, and the 1920×1080 share drops by a factor of 6.3.

| Resolution | In the full delivery (10,000) | In the deduplicated base (2,129) |
|---|---|---|
| 1920×1080 | 79.37% | 12.54% (267) |
| 1280×720 | 17.85% | 74.82% (1,593) |
| other (atypical) | 2.78% | 12.64% (269) |

So the delivery's redundancy (near-duplicates, Hamming ≤ 6, see criterion 6.5) is concentrated mostly in 1920×1080 frames: in deduplication they collapse far more than 1280×720 frames. The proportions in the final sample (47 of 64 — 1280×720, 73.4%; 10 of 64 — 1920×1080, 15.6%) match the distribution of the deduplicated base, not the full delivery.

**Additional guarantees** (a post-hoc check and top-up, if the random selection over axes 1–2 did not satisfy the condition):

- at least 5 images with more than 1 object per frame;
- at least 3 images out of the 33 with a recorded coordinate defect (criterion 6.2);
- all three vendor splits (train/val/test) represented by at least one image.

If, after applying all guarantees, the volume exceeds the target, the excess images are removed randomly **only** from the pool not protected by any guarantee (not multi-object, not atypical-resolution, not coordinate-defect, not low-light).

### Actual sample composition

| Axis | Category | Image count |
|---|---|---|
| Split | train | 26 |
| Split | val | 6 |
| Split | test | 32 |
| Object size | T1 (small) | 23 |
| Object size | T2 (medium) | 20 |
| Object size | T3 (large) | 21 |
| Brightness | T1 (dark) | 25 |
| Brightness | T2 (medium) | 17 |
| Brightness | T3 (light) | 22 |

The distribution over vendor splits (train 26 / val 6 / test 32) is disproportionate to their shares in the full delivery (52% / 26% / 22% for train/val/test respectively). This is a consequence of stratification by object size and brightness: the requirement on splits was limited to representation of all three, not proportionality.

| Additional feature | Image count | Requirement |
|---|---|---|
| Atypical resolution (not 1920×1080, not 1280×720) | 7 | ≥ 3 |
| Multi-object frame (> 1 object) | 6 | ≥ 5 |
| Coordinate defect (criterion 6.2) | 3 | ≥ 3 |
| Below the low-light threshold (< 49.0) | 1 | ≥ 1, if present in the base (20 of 2,129 present) |
| All three splits represented | train/val/test — all three | mandatory |

**Resolutions in the sample:** 1280×720 — 47 images, 1920×1080 — 10, and one image each of the atypical resolutions 573×360, 580×387, 590×332, 634×392, 926×617, 960×635, 1000×667 (7 atypical in total).

All guarantees are met. The full sample composition with all stratification features, object counts, and box coordinates is in [data/review_sample_6_4.csv](data/review_sample_6_4.csv).

### Step 3 — preparation for review

From the 64 selected images, I assembled a dataset for visual review in FiftyOne, with the delivery annotation overlaid (boxes from the source XML, the `ground_truth` field).

**FiftyOne sample dataset fields:**

| Field | Content |
|---|---|
| `delivery_relpath` | The file's relative path in the delivery — a stable sample identifier (the FiftyOne sample/label ID is not used, because it is recreated on every dataset rebuild) |
| `delivery_filename` | The file name (for example, `00031.jpg`) |
| `split` | The delivery's vendor split (train/val/test) |
| `resolution` | Image resolution, a `WxH` string |
| `width`, `height` | Image resolution, as numbers |
| `brightness_median_v` | Median of the HSV V channel (the same computation as in criterion 6.3) |
| `n_objects` | Number of annotated objects in the frame |
| `min_minor_side` | Minimum shorter box side in the frame, px |
| `object_size_tercile` | Tercile by object size (`T1_low`/`T2_mid`/`T3_high`) |
| `brightness_tercile` | Tercile by brightness (`T1_low`/`T2_mid`/`T3_high`) |
| `is_atypical_resolution` | An atypical-resolution flag |
| `is_low_light_below_threshold` | A flag: `brightness_median_v` below the calibrated threshold 49.0 |
| `is_multi_object` | A flag: more than one object in the frame |
| `has_defect` | A flag: the frame is among the 33 objects with a coordinate defect (criterion 6.2) |
| `ground_truth` | The delivery annotation (class `UAV` boxes, overlaid for visual review) |

The FiftyOne dataset itself is not part of the portfolio. A subset of these fields, plus `filepath` and `bboxes_json`, is exported to the CSV `review_sample_6_4.csv` (the export composition is in "Step 4").

### Step 4 — export of the list

The full sample composition is saved in [data/review_sample_6_4.csv](data/review_sample_6_4.csv): file path, split, resolution, `brightness_median_v`, object count, all stratification features, box coordinates (`bboxes_json` — a list of `{xmin, ymin, xmax, ymax}` per frame).

## Visual review results

I did the review in FiftyOne on all 64 selected images. The criteria are per section 6.4 of the specification: box composition (whether landing supports and the disks of spinning rotors, along the border of the visible disk, are included); tightness of the box's fit to the object; the presence of target-class objects left without annotation; the treatment of ambiguous objects.

### 1. Box composition

On the reviewed sample, the delivery annotation includes landing supports and the disks of spinning rotors. This is compatible with section 4 of the project guideline, class `Drone` ([docs/annotation_guidelines.md](../docs/annotation_guidelines-en.md)).

For comparison: for class `Drone` in Roboflow UAV — the only current source of this class — the annotation-agreement report records the reverse. On large objects (≥100px), GT (ground truth — the source's original annotation) is, in 43.3% of pairs (42 of 97), nested inside the project annotation (`gt_inside_gold`), that is, limited to the body without protruding elements. In these pairs, GT covers a median of 74.8% of the project box's area (`median inter_over_gold`) — about a quarter of the area (supports, rotors) is not annotated in GT (see [annotation_agreement-en.md](annotation_agreement-en.md), section 5). So by box composition, the delivery on the reviewed sample is closer to the project guideline than the current source of class `Drone` is.

### 2. Fit tightness

The boxes fit with a gap. The gap is subjectively smaller than in VisDrone and Roboflow UAV. I found no systematic shift depending on object size or capture conditions. The assessment is subjective; I did not measure the gap.

### 3. Missed objects

I did not find any on the sample.

Caveat: the sample is 64 images out of the 2,129 representatives of phash groups that remained after deduplicating the delivery (see "Step 1" above). The absence of misses on the sample does not mean their absence in the delivery.

### 4. Capture viewpoint

The sample contains only capture from the ground and from buildings. I found no frames from the craft's camera in flight. Roboflow UAV does contain such frames.

The same caveat: this is an observation on the sample, not a characterization of the whole delivery.
