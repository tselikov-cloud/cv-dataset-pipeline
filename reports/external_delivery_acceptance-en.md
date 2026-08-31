# DUT Anti-UAV acceptance check — criteria 6.1–6.6

**Status:** delivery in acceptance. Not added to `manifest.parquet`, not tracked in DVC, not placed in `data/`.
**Specification:** [docs/data_request_spec_lowlight_drone.md](../docs/data_request_spec_lowlight_drone-en.md).

## Overview

**Checked in this report:** 6.2 (technical annotation validity), 6.3 (illumination conformance), 6.5 (duplication and novelty), 6.6 (domain gap, non-threshold).

**Checked in adjacent reports:** 6.1 (formal completeness) — by the inventory facts, [external_delivery_inventory-en.md](external_delivery_inventory-en.md); 6.4 (annotation-policy compatibility, non-threshold) — by visual review of a sample, [external_delivery_annotation_review-en.md](external_delivery_annotation_review-en.md). Sections 6.1 and 6.4 are not in this document.

Acceptance checked all six criteria. The summary verdict table below covers all criteria, including those checked in the adjacent reports. The final verdict is in the "Verdict" section at the end of the document.

## Intermediate data

For acceptance, I computed a set of intermediate tables. Each one is a separate pass over the corresponding delivery array:

| Computation | Content | Granularity |
|---|---|---|
| Annotation defects | Defect flags per annotation object | 1 row = 1 object (10,109 rows) |
| Illumination | `brightness_median_v`, `brightness_p5_v` | 1 row = 1 image (10,000 rows) |
| Perceptual hash (phash) | phash (hex) and its integer representation | 1 row = 1 image (10,000 rows) |
| Sample for visual check — darkest | 20 darkest images of the delivery | for later visual check, see [data/visual_review_darkest_20.csv](data/visual_review_darkest_20.csv) |
| Sample for visual check — around the threshold | 20 images closest to the 49.0 threshold | for later visual check, see [data/visual_review_around_threshold_20.csv](data/visual_review_around_threshold_20.csv) |
| Boxes for the domain-gap assessment | DUT boxes (class UAV) and Roboflow UAV (class drone, active rows) with frame dimensions | 1 row = 1 object (12,840 rows) |

I performed the check for each criterion (6.2, 6.3, 6.5, 6.6) as a separate pass over the corresponding computation.

## 6.2 Technical annotation validity

**Threshold:** the share of defective objects is no more than 0.5% (specification, section 6.2).
**Method:** acceptance parses all 10,109 objects (`<object>`) in all 10,000 Pascal VOC (Visual Object Classes) XML files and matches the box coordinates against the image size declared in the same file and against the actual file dimensions.

### Summary

Numeric table (shared for both revisions, given once):

| Metric | Value |
|---|---|
| Total objects | 10,109 |
| Defective objects (any type) | 33 |
| Share of defective objects | **0.33%** |
| Threshold | 0.5% |
| **Verdict** | **Met** (0.33% < 0.5%) |

### Breakdown by defect type

| Defect type | Object count | Share of all objects |
|---|---|---|
| Coordinates beyond the declared image size | 32 | 0.3165% |
| Zero or negative box area | 1 | 0.0099% |
| `xmin >= xmax` or `ymin >= ymax` | 1 | 0.0099% |
| Class outside the vocabulary (only `UAV` declared) | 0 | 0.0000% |
| Mismatch between the XML-declared and actual image size | 0 | 0.0000% |

One object falls into both "zero or negative area" and "`xmin>=xmax` or `ymin>=ymax`." This is the same defect counted in both categories: the second category clarifies the geometric cause of the first. So the row sum of the table exceeds 33.

**Magnitude of the out-of-bounds (only the "beyond the image" category, 32 objects):**

| Metric | Value, px |
|---|---|
| Median excess | 1 |
| Maximum excess | 1 |

In all 32 cases, the excess is exactly 1 px: the `xmax` or `ymax` coordinate equals `width + 1` or `height + 1` respectively. This is an off-by-one in the vendor's source annotation.

### Distribution by split

| Split | Total objects | Defective | Share | Out of bounds | Zero area | `xmin>=xmax`/`ymin>=ymax` | Class out of vocab | Size mismatch |
|---|---|---|---|---|---|---|---|---|
| train | 5,243 | 16 | 0.3052% | 16 | 0 | 0 | 0 | 0 |
| val | 2,621 | 8 | 0.3052% | 7 | 1 | 1 | 0 | 0 |
| test | 2,245 | 9 | 0.4009% | 9 | 0 | 0 | 0 | 0 |

### Examples (10 of 33)

| Split | File | xmin | ymin | xmax | ymax | Declared (W×H) | Actual (W×H) | Defect type |
|---|---|---|---|---|---|---|---|---|
| train | `train/xml/00155.xml` | 1124 | 425 | 1245 | 513 | 1280×512 | 1280×512 | ymax > height (+1px) |
| train | `train/xml/00470.xml` | 376 | 367 | 1236 | 721 | 1280×720 | 1280×720 | ymax > height (+1px) |
| train | `train/xml/00505.xml` | 529 | 510 | 905 | 721 | 1280×720 | 1280×720 | ymax > height (+1px) |
| train | `train/xml/00526.xml` | 659 | 579 | 832 | 721 | 1280×720 | 1280×720 | ymax > height (+1px) |
| train | `train/xml/00605.xml` | 1155 | 499 | 1281 | 592 | 1280×720 | 1280×720 | xmax > width (+1px) |
| train | `train/xml/00606.xml` | 1178 | 624 | 1281 | 696 | 1280×720 | 1280×720 | xmax > width (+1px) |
| train | `train/xml/00827.xml` | 1817 | 277 | 1921 | 340 | 1920×1080 | 1920×1080 | xmax > width (+1px) |
| train | `train/xml/00841.xml` | 1760 | 265 | 1921 | 333 | 1920×1080 | 1920×1080 | xmax > width (+1px) |
| train | `train/xml/02708.xml` | 1877 | 611 | 1921 | 638 | 1920×1080 | 1920×1080 | xmax > width (+1px) |
| train | `train/xml/03333.xml` | 1876 | 285 | 1921 | 319 | 1920×1080 | 1920×1080 | xmax > width (+1px) |

The object with zero or negative area and `xmin>=xmax`/`ymin>=ymax` (`val/xml/00991.xml`) is not in the top 10 by file order. It is recorded separately in [annotation_defects.parquet](annotation_defects.parquet) (the row with `defect_nonpositive_area=True`).

## 6.3 Illumination conformance

**Threshold:** at least 30% of the delivery's images satisfy the low-light criterion (specification, section 6.3).
**Low-light criterion:** `brightness_median_v < 49.0`.
**Method and threshold:** `cv2.cvtColor(BGR2HSV)`, the V channel of the HSV (hue-saturation-value) color space, `brightness_median_v = median(V)`, `brightness_p5_v = percentile(V, 5)`. The 49.0 threshold is fixed by visual calibration on VisDrone (methodology — [docs/illumination_classification.md](../docs/illumination_classification-en.md)). Acceptance did **not** recompute it.

### Summary

| Metric | Value |
|---|---|
| Total images | 10,000 |
| Images with `brightness_median_v < 49.0` | 465 |
| Share | **4.65%** |
| Required threshold | 30% |
| **Verdict** | **Not met** (4.65% < 30%) |

### Descriptive statistics of `brightness_median_v` (whole delivery, 0-255)

| min | p5 | p25 | median | p75 | max |
|---|---|---|---|---|---|
| 0.0 | 49.0 | 99.0 | 145.0 | 173.0 | 255.0 |

### Histogram of `brightness_median_v` (bins of 10, whole delivery)

| Range | Image count |
|---|---|
| 0–10 | 1 |
| 10–20 | 0 |
| 20–30 | 1 |
| 30–40 | 102 |
| 40–50 | 399 |
| 50–60 | 280 |
| 60–70 | 251 |
| 70–80 | 339 |
| 80–90 | 573 |
| 90–100 | 644 |
| 100–110 | 659 |
| 110–120 | 415 |
| 120–130 | 352 |
| 130–140 | 649 |
| 140–150 | 667 |
| 150–160 | 744 |
| 160–170 | 1,025 |
| 170–180 | 1,141 |
| 180–190 | 722 |
| 190–200 | 368 |
| 200–210 | 252 |
| 210–220 | 109 |
| 220–230 | 64 |
| 230–240 | 74 |
| 240–250 | 60 |
| 250–260 | 109 |

The distribution has a pronounced peak in the 160–190 range (day, good lighting) and a small left tail below the 49 threshold.

### By split

| Split | Total images | Below threshold | Share | median (p25/median/p75) |
|---|---|---|---|---|
| train | 5,200 | 254 | 4.88% | 97 / 145 / 172 |
| val | 2,600 | 130 | 5.00% | 97 / 145 / 172 |
| test | 2,200 | 81 | 3.68% | 108 / 151 / 177 |

### Comparison with the current dataset

| Source | N | min | p5 | p25 | median | p75 | max | Share below the 49.0 threshold |
|---|---|---|---|---|---|---|---|---|
| VisDrone (current) | 8,616 | 0.0 | 22.0 | 76.0 | 107.0 | 128.0 | 251.0 | 14.25% |
| Roboflow UAV (current) | 2,529 | 0.0 | 76.4 | 133.0 | 166.0 | 215.0 | 255.0 | 2.69% |
| **DUT Anti-UAV (delivery)** | 10,000 | 0.0 | 49.0 | 99.0 | 145.0 | 173.0 | 255.0 | **4.65%** |

By the share below the threshold, the delivery is closer to Roboflow UAV (2.69%) than to VisDrone (14.25%), and several times below the 30% required to close the gap.

### Selection for visual check (genuine low-light versus artificial lighting)

The lists are saved separately, for later visual classification:

- **20 darkest images of the delivery:** [data/visual_review_darkest_20.csv](data/visual_review_darkest_20.csv). The `brightness_median_v` range in this sample is 0.0–33.0; `brightness_p5_v` in most cases is 8–12 (a significant part of the frame is dark, not just the median).
- **20 images around the threshold (`brightness_median_v` closest to 49.0):** [data/visual_review_around_threshold_20.csv](data/visual_review_around_threshold_20.csv). In all 20, `brightness_median_v = 49.0`, `brightness_p5_v` in the range 13–18.

### Visual classification result

I reviewed all 40 images from both lists.

The predominant lighting type in the dark part of the delivery is dusk under natural lighting, with no artificial light sources in the frame. Isolated exceptions: one frame where the light source is the craft's own running lights; one frame with running lights and a street lamp.

The vast majority of the reviewed frames are frame-by-frame splits of two video scenes, not independent scenes. This is consistent with the criterion 6.5 result: the delivery's redundancy is 78.71%.

By lighting type, the dark part of the delivery is closer to the target condition than the current dataset's artificial-lighting scenes. But its volume is incomparable with the requirement — 4.65% of frames. I reviewed the 20 darkest frames and 20 frames at the threshold; in this sample, derivatives of two scenes predominate. The conclusion does not extend to the whole 4.65% share: I did not review the remaining frames below the threshold. The specification's requirement on the share of low-light frames is not met.

**Methodological limitation.** The category corresponding to dusk under natural lighting without artificial sources is absent from the project's classification: the current scheme distinguishes `day` and `artificial_light`, and the `low_light` category is declared and not populated (see [docs/illumination_classification.md](../docs/illumination_classification-en.md)). Frames of this type have no unambiguous correspondence to any category.

## 6.5 Duplication and novelty

**Thresholds:** the share of internal duplicates (Hamming distance ≤ 6) is no more than 5%; overlap with the current dataset — zero matches (specification, section 6.5).
**Method:** phash (perceptual hash) in the same way as at the data-structuring stage (`imagehash.phash`, PIL, default values — a 64-bit hash). Hamming distance is the number of bits that differ between hashes; acceptance computes it by a full pairwise enumeration (10,000×10,000 within the delivery; 10,000×11,145 against the active rows of `manifest.parquet`).

### Internal duplicates

| Metric | Value |
|---|---|
| Total images | 10,000 |
| Exact phash matches (groups) | 878 |
| Redundant copies at exact match | 6,140 |
| Duplicate groups at Hamming ≤ 6 | 312 |
| Images in duplicate groups | 8,183 |
| Redundant images (beyond one "canonical" per group) at Hamming ≤ 6 | 7,871 |
| **Share of redundant images** | **78.71%** |
| Threshold | 5% |
| **Verdict** | **Not met** (78.71% ≫ 5%) |

### Overlap of duplicate groups with train/val/test split boundaries

| Metric | Value |
|---|---|
| Duplicate groups spanning ≥2 splits | 289 of 312 (92.6%) |

The vast majority of duplicate groups are not confined to one split: the same frame (or a near-identical one, Hamming ≤ 6) occurs in several vendor splits at once.

**Examples of cross-split groups:**

| Splits in the group | Files |
|---|---|
| test, train | `train/img/00126.jpg`, `test/img/01020.jpg` |
| train, val | `train/img/00150.jpg`, `val/img/00030.jpg` |
| train, val | `train/img/00209.jpg`, `train/img/00210.jpg`, `val/img/00105.jpg` |
| test, train | `train/img/00223.jpg`, `test/img/00114.jpg` |
| test, train | `train/img/00224.jpg`, `test/img/01070.jpg` |

### Check for hidden video structure (proxy)

The share of images within their own split that have at least one neighbor with Hamming ≤ 6:

| Split | Total images | With a neighbor (Hamming ≤ 6) | Share |
|---|---|---|---|
| train | 5,200 | 4,471 | 85.98% |
| val | 2,600 | 2,219 | 85.35% |
| test | 2,200 | 1,493 | 67.86% |

More than 85% of images in train and val and about 68% in test have a visually near-identical neighbor within their own split. This is consistent with the assumption of frame-by-frame extraction from video sequences. I raised the assumption from signs recorded during inventory and verified it during the duplication analysis: the dominance of the 1920×1080 and 1280×720 resolutions and the end-to-end renumbering without indication of the source sequence ([external_delivery_inventory-en.md](external_delivery_inventory-en.md), section 10).

### Cross-source against the current dataset (`manifest.parquet`)

| Metric | Value |
|---|---|
| Active `manifest.parquet` rows the delivery was compared against | 11,145 |
| Minimum Hamming distance found | **0** (exact perceptual-hash match) |
| Number of pairs with Hamming ≤ 6 | **27** |
| Threshold | 0 overlaps |
| **Verdict** | **Not met** (27 > 0, including exact matches) |

**Examples of overlaps (10 of 27):**

| Delivery file | `sample_id` in the manifest | File in the current dataset (Roboflow UAV) | Hamming |
|---|---|---|---|
| `train/img/00021.jpg` | `337e52e3af4...eef550` | `pic_517_jpg.rf.3ed484cb0972c8257e6d1996cf432867.jpg` | 4 |
| `train/img/00037.jpg` | `446e5365afb...93c19974` | `pic_576_jpg.rf.f6008c3a438d3cbe33c0c1e1eed5d506.jpg` | 0 |
| `train/img/00062.jpg` | `95279b5d89e...b4d7ad4` | `pic_638_jpg.rf.64a39e1253c8f277b1a9abb6af8640c4.jpg` | 0 |
| `train/img/00080.jpg` | `773848bdde1...8af63680a` | `54_JPEG.rf.6c7716b3071b7601d9bc4cf3959bddab.jpg` | 0 |
| `train/img/00092.jpg` | `5c9ff6277cb...c130e66f9` | `0228_jpg.rf.7a72b6cbaff0fde06e6ed024189fdd5f.jpg` | 0 |
| `train/img/00578.jpg` | `f40189f224e...7db229646` | `video18_253_JPEG.rf.a9b3a9bbf2c615097485dfa4b8f8e345.jpg` | 6 |
| `train/img/00580.jpg` | `4726c989bbc...78e944f8` | `foto07483_jpg.rf.ad6898d34473bbab7318a616a6367b0c.jpg` | 6 |
| `train/img/00651.jpg` | `e83b5db55c2...c0b4864c6` | `video10253_JPEG.rf.de9a8086d1481391c8e448c4c8be9a56.jpg` | 6 |
| `train/img/00713.jpg` | `250e5c53071...447127a53f` | `foto05453_jpg.rf.96cf1c6eda736e58974251abdccf2586.jpg` | 4 |
| `val/img/00009.jpg` | `7e2e33f81b4...a61fce5` | `0259_jpg.rf.24f951902ac93dabfb99f8c00d740607.jpg` | 6 |

All matches are found with the `roboflow-uav` source. A spot check of one pair with Hamming = 0 (`train/img/00037.jpg` against `pic_576_jpg.rf...`) showed different file resolutions (630×420 versus 620×410). This is consistent with the same source frame at a different scale and compression, rather than a random hash collision.

## 6.6 Domain gap

**Status:** a non-threshold criterion (specification, section 6.6). It does not affect the acceptance verdict. The goal is to record along which axes the delivery expands the current dataset's coverage and along which it reproduces the existing profile.

**Comparison sets:**

- **DUT Anti-UAV (delivery)** — all 10,000 images, objects of class `UAV` (10,109 boxes).
- **Roboflow UAV (current)** — active rows of `manifest.parquet` with `source == "roboflow-uav"` (2,529 images). The boxes are class `drone` from `_annotations.coco.json`, filtered to active images (2,731 boxes). This is the only source of class `Drone` in the current dataset and the main comparison reference for the task.
- **VisDrone (current)** — active rows of `manifest.parquet` with `source == "visdrone"` (8,616 images). Class `Drone` is absent, so this source is not used for the "object size" axis. For the "objects per frame" axis, all real classes are counted (`ignore_regions` excluded as a mask, not an object).

Below, for each axis, the actual magnitude of the divergence is given — a comparison of the delivery with Roboflow UAV as the main reference, without assigning it to categories: the criterion is non-threshold, and categorization does not affect the acceptance verdict.

### 1. Image resolution

| Metric | DUT Anti-UAV (n=10,000) | Roboflow UAV (n=2,529) | VisDrone (n=8,616) |
|---|---|---|---|
| Width min / p5 / median / p95 / max | 240 / 1280 / 1920 / 1920 / 5616 | 150 / 360 / 1280 / 1920 / 6000 | 480 / 1360 / 1400 / 2000 / 2000 |
| Height min / p5 / median / p95 / max | 160 / 720 / 1080 / 1080 / 3744 | 159 / 300 / 720 / 1088 / 4000 | 360 / 765 / 1050 / 1500 / 1500 |
| Aspect ratio, median (p25–p75) | 1.78 (1.78–1.78) | 1.78 (1.5–1.78) | 1.78 (1.33–1.78) |

The top 10 resolutions for each set — tables in the original, unchanged (numeric data).

**Divergence (DUT versus Roboflow UAV):** the DUT median resolution (1920×1080) is 1.5 times higher than the Roboflow median (1280×720) on each side. Roboflow has a long tail of non-standard "square" resolutions (1000×1000, 800×800, 500×500), characteristic of datasets assembled from individual photos rather than video; DUT has almost none of it. The aspect ratio in both is around 1.78 (16:9).

### 2. Object size (boxes: DUT class `UAV` versus Roboflow class `drone`)

| Metric | DUT Anti-UAV (n=10,109) | Roboflow UAV, active (n=2,731) | Roboflow UAV, whole COCO, reference (n=4,805) |
|---|---|---|---|
| Shorter side, px: min/p5/p25/median/p75/p95/max | 0/10/17/24/42/165/2144 | 11/33/69/150/278.5/610/2303 | 10/24/41/79/208/485/2303 |
| Longer side, px: min/p5/p25/median/p75/p95/max | 3/21/32/44/79/311.6/3570 | 14/50/122/284/561/1121.5/4974 | 14/37.2/66/140/404/959.6/4974 |
| Box area share of frame: p5/p25/median/p75/p95 | 0.011% / 0.027% / 0.051% / 0.20% / 5.93% | 0.19% / 1.08% / 9.27% / 35.48% / 66.79% | 0.10% / 0.30% / 1.37% / 18.02% / 56.62% |
| Area share, log10: median | −3.29 | −1.03 | −1.86 |
| Box aspect ratio: p25/median/p75 | 1.55 / 1.89 / 2.28 | 1.45 / 1.78 / 2.20 | 1.44 / 1.71 / 2.05 |
| **Share of objects with shorter side < 50px** | **78.23%** | **13.15%** | 32.63% |
| Specification section 3 requirement | ≥ 25% | (reference, not the target set) | — |

**Divergence (DUT versus Roboflow UAV, active rows).** The median box shorter side in DUT (24px) is more than 6 times smaller than the Roboflow median (150px). The median frame-area share differs by one and a half orders of magnitude (0.051% versus 9.27%). The box aspect ratio in both sets is close (median 1.89 versus 1.78): the object's shape in the frame is comparable, the scale differs.

This divergence works in favor of closing the gap stated in the specification (section 3). The delivery overfulfills the requirement "at least 25% of objects with a box shorter side smaller than 50px" (78.23% against the required 25%), whereas the active rows of Roboflow UAV (13.15%) do not satisfy this requirement themselves. That is, by object size the delivery **expands the coverage** of the current dataset rather than duplicating its profile. The value over the whole Roboflow COCO (32.63%, without the active-rows filter) is closer to the threshold, but the corresponding images mostly do not enter the active, non-deduplicated dataset.

### 3. Brightness (`brightness_median_v` / `brightness_p5_v`, HSV V channel, 0–255)

| Metric | DUT Anti-UAV (n=10,000) | Roboflow UAV (n=2,529) | VisDrone (n=8,616) |
|---|---|---|---|
| `brightness_median_v`: p5/p25/median/p75/p95 | 49 / 99 / 145 / 173 / 206 | 76.4 / 133 / 166 / 215 / 255 | 22 / 76 / 107 / 128 / 153 |
| `brightness_p5_v`: p5/p25/median/p75/p95 | 9 / 20 / 30 / 42 / 114 | 7 / 34 / 60 / 98 / 171.6 | 9 / 22 / 33 / 49 / 79 |

**Divergence (DUT versus Roboflow UAV).** The DUT median `brightness_median_v` (145) is lower than the Roboflow median (166) — a difference of less than 1.2 times. At the same time, DUT is noticeably brighter than VisDrone's lower tail (median 107): between VisDrone and Roboflow, DUT takes an intermediate position, closer to Roboflow. This is consistent with the criterion 6.3 result — the delivery is not shifted toward low light relative to the already-existing data.

### 4. Objects per frame

| Metric | DUT Anti-UAV, class `UAV` (n=10,000) | Roboflow UAV, class `drone` (n=2,529) | VisDrone, all classes except `ignore_regions` (n=8,616) |
|---|---|---|---|
| Share of frames with 0 objects | 0.03% (3 frames) | 0.00% | 0.00% |
| Share of frames with 1 object | 99.22% | 94.74% | 0.10% |
| Share of frames with 2 objects | 0.48% | 4.27% | 0.30% |
| Share of frames with 3+ objects | 0.27% | 0.99% | 99.59% |
| Median objects per frame | 1 | 1 | 42 |
| Maximum objects per frame | 6 | 13 | 902 |

In the delivery, 3 images have no annotated objects of class `UAV` (0.03% of 10,000).

**Divergence (DUT versus Roboflow UAV).** The median number of objects per frame is the same (1); almost all frames in both sets are single-object. The share of frames with 2 objects in Roboflow is higher (4.27% versus 0.48%), and the maximum is higher (13 versus 6). But both sets are several orders of magnitude below VisDrone (median 42 objects per frame — scenes with dense vehicle traffic, a fundamentally different task). The comparison with VisDrone on this axis is not indicative, since VisDrone does not concern the `Drone` detection task.

### 5. Summary of divergences (delivery relative to Roboflow UAV)

| Axis | Divergence direction | Magnitude |
|---|---|---|
| Image resolution | DUT higher (median 1920×1080 versus 1280×720) | ×1.5 on each side |
| Image aspect ratio | Coincides (both ~1.78) | — |
| Object size (box shorter side) | DUT drastically smaller (median 24px versus 150px) | ×6.25 — **expands coverage** toward small objects, required by the specification |
| Share of objects < 50px by shorter side | DUT drastically higher (78.2% versus 13.1%) | — **closes** the specification section 3 requirement, which Roboflow itself does not satisfy |
| Box aspect ratio | Coincides (medians 1.89 and 1.78) | ×1.06 |
| Brightness (`brightness_median_v`) | DUT slightly darker (median 145 versus 166) | ×1.14 — **does not close** the stated low-light gap (see 6.3) |
| Objects per frame | Coincides by median (1 versus 1) | — |

**Fact by axes.** The delivery expands the current dataset's coverage by object size: substantially more small targets than in Roboflow UAV, and it closes the specification section 3 requirement with a margin. By frame resolution, image and box aspect ratio, brightness, and objects per frame, the delivery reproduces a profile close to what already exists in Roboflow UAV, without introducing a new domain along these axes. In particular, by brightness it does not expand coverage toward low light — this is already established as a failure of the threshold criterion 6.3.

No acceptance verdict is issued for this section: criterion 6.6 is non-threshold.

## Summary verdict table

The table covers all six criteria. Criteria 6.1 and 6.4 are checked in the adjacent reports — links in the rows.

| Criterion | Threshold/type | Actual value | Verdict |
|---|---|---|---|
| 6.1 Formal completeness ([inventory](external_delivery_inventory-en.md)) | threshold, binary | volume 10,000 = declared, orphans 0, corrupted files 0, structure matches the description; license text absent from the delivery, Apache-2.0 confirmed by the source repository's description | **Met** |
| 6.2 Technical annotation validity | ≤ 0.5% defective objects | 0.33% | **Met** |
| 6.3 Illumination conformance | ≥ 30% of images below the 49.0 threshold | 4.65% | **Not met** |
| 6.4 Annotation-policy compatibility ([visual review](external_delivery_annotation_review-en.md)) | non-threshold | on a sample of 64 images, the policy is compatible with the project guideline by box composition; the fit assessment is subjective, without measurements | **Verdict not applicable** |
| 6.5 Duplication and novelty (internal) | ≤ 5% redundant images | 78.71% | **Not met** |
| 6.5 Duplication and novelty (cross-source) | 0 overlaps with Hamming ≤ 6 | 27 pairs, min distance 0 | **Not met** |
| 6.6 Domain gap | non-threshold | expands coverage by object size; comparable on the rest of the axes | **Verdict not applicable** |

For criterion 6.1 there is a single deviation: the requirement "license confirmed by documentation" is not met by the delivery's contents. There is no license file in the archives, and the Apache-2.0 license is established from the source repository's description ([inventory](external_delivery_inventory-en.md), sections 1 and 6). This did not affect the 6.1 verdict: the license is documentarily traceable to the source.

## Verdict

**REJECTED.**

The grounds are the violation of two threshold criteria (6.3, 6.5). By the rule in section 7 of the specification, the violation of at least one threshold criterion entails rejection of the delivery.

### Violations table

| Criterion | Threshold | Actual value |
|---|---|---|
| 6.3 Illumination conformance | ≥ 30% of images below the low-light threshold | 4.65% |
| 6.5 Internal duplicates | ≤ 5% redundant images | 78.71% |
| 6.5 Cross-source overlap | 0 pairs with Hamming ≤ 6 | 27 pairs |

### Rationale for 6.3

The stated gap is not closed: the share of images that satisfy the low-light criterion is 4.65% against the required 30%.

Separately: the published source description claims capture under day, night, dawn, and dusk conditions. Measurement by the calibrated threshold does not confirm this: the share of frames below the threshold (4.65%) is comparable to the already-existing Roboflow UAV (2.69%) and far from the claimed coverage of night conditions. The divergence between the source's declared description and the measured characteristic of the delivery is a standalone acceptance result.

### Rationale for 6.5

The redundancy of 78.71% means that out of the nominal 10,000 images, after grouping by phash (Hamming ≤ 6), 2,129 group representatives remain. There are no video or sequence metadata in the delivery ([external_delivery_inventory-en.md](external_delivery_inventory-en.md), section 10), so the number of independent scenes was not measured. The vendor split boundaries cross 92.6% of duplicate groups, so the splits are unusable without reconstruction at the sequence level. 27 pairs at a Hamming distance of no more than 6 against the current dataset mean partial duplication of the already-existing data.

The redundancy is concentrated in 1920×1080 frames: they make up 79.37% of the full delivery and only 12.54% of the deduplicated base ([external_delivery_annotation_review-en.md](external_delivery_annotation_review-en.md), the stratification section).

### Suitability for a different request

The delivery expands coverage along one axis — object size: the share of boxes with a shorter side smaller than 50px is 78.2% against 13.1% in Roboflow UAV. By box composition, the delivery's annotation policy is compatible with the project guideline (landing supports and rotor disks are included).

I recorded the source as a candidate for a request targeting the small-object gap, on condition of prior deduplication and split reconstruction. The rejection concerns conformance to the current specification, not the quality of the source.

### Decision on the delivery

I placed the delivery in acceptance separately from the dataset, in a staging directory: before the verdict is issued, it is not entered into the sample registry and not versioned, and on rejection it does not enter the version history as accepted. The data remains in the staging directory, is not included in the dataset, and is not added to `manifest.parquet` or DVC.

| Split | File | SHA-256 | Uploaded (UTC) |
|---|---|---|---|
| train | `train.zip` | `14f927290556df60e23cedfa80dffc10dc21e4a3b6843e150cfc49644376eece` | 2026-08-03T22:02:30.747073+00:00 |
| val | `val.zip` | `238be0ceb3e7c5be6711ee3247e49df2750d52f91f54f5366c68bebac112ebf8` | 2026-08-03T22:03:10.310950+00:00 |
| test | `test.zip` | `a671989a01cff98c684aeb084e59b86f4152c50499d86152eb970a9fc7fb1cbe` | 2026-08-03T22:03:50.245966+00:00 |

**Verdict date:** 2026-08-10.
