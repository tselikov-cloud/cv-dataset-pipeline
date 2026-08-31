# Request Spec — closing the low-light gap for class `Drone`

**Document:** data request specification and delivery acceptance criteria.
**Status:** the thresholds are derived from the measured coverage gap of the project's own dataset; they were not revised based on the delivery outcome.
**Target class:** `Drone`.

## 1. Rationale

The current dataset (11,145 active samples, two sources) contains no images of class `Drone` under low-light conditions.

Illumination profiling by the V channel of the HSV (hue-saturation-value) color space showed three facts:

- all of Roboflow UAV is classified as `day`;
- night frames exist only in VisDrone. They belong to class `vehicle` and show scenes with artificial (street) lighting, not genuine low-light;
- the classification rule does not assign the `low_light` category, so it is empty across the whole dataset.

The rationale is the conclusion of a visual review of the darkest tail of both sources: I found no frames shot without an artificial light source. The empty category records that the absence was verified, not skipped. An empty counter is not proof on its own; see [illumination_classification-en.md](illumination_classification-en.md).

Additional rationale: class `Drone` is quantitatively underrepresented — 2,731 objects across 2,529 images against 244,708 objects of class `vehicle` across 8,262 images. The imbalance is 89.60x by objects and 3.27x by images; for the calculation, see [reports/class_distribution.md](../reports/class_distribution-en.md).

## 2. Subject of the request

The subject of the request is a delivery of images of class `Drone` under low-light conditions, suitable for inclusion in a detection dataset without re-annotation.

## 3. Content requirements

| Parameter | Requirement |
|---|---|
| Target class | `Drone` — the aircraft as an object in the frame |
| Volume | at least 1,000 images with a target-class object |
| Illumination conditions | at least 30% of images meet the low-light criterion (definition — section 6.3) |
| Model diversity | at least 10 different craft types |
| Background diversity | at least 3 scene types: open sky, built-up area, natural landscape |
| Object size | at least 25% of objects have a box shorter side smaller than 50 px |
| Viewpoint | both ground-level and aerial capture present |

## 4. Annotation requirements

- Bounding boxes aligned to the frame axes (axis-aligned), a single target class.
- **Box composition:** the entire craft, including landing supports and the disks of spinning rotors (along the border of the visible disk). Acceptance records annotation of only the body without protruding elements as a policy divergence (section 6.4).
- The box fits tightly to the object, with no gap.
- All target-class objects in the frame must be annotated. Frames without objects are allowed, but the vendor must mark them explicitly as empty rather than skip them in the annotations.

## 5. Format and accompanying-data requirements

- **Images:** JPEG or PNG, without reducing the original resolution.
- **Annotations:** COCO 1.0 or another format with full documentation of the fields and the coordinate system.
- **Image-level metadata** (if the vendor has it): source, date and conditions of capture, craft type.
- **A license** permitting use for the stated purposes, with documentary confirmation.
- **Provenance description:** how the material was obtained, whether there are video-derived frames and a sequence structure.

## 6. Acceptance criteria

Threshold criteria are 6.1, 6.2, 6.3, 6.5. Non-threshold ones are 6.4, 6.6.

#### 6.1 Formal completeness — threshold, binary

Acceptance checks five conditions:

- the actual volume matches the stated volume;
- each image has a corresponding record in the annotations and vice versa, with no orphan files;
- all files are readable, with none corrupted;
- the delivery structure matches the description;
- the license is confirmed by documentation.

If a delivery fails any point, acceptance rejects it and performs no further checks.

#### 6.2 Technical annotation validity — threshold

The share of defective objects is no more than **0.5%**.

An object is considered defective under any of these signs: coordinates outside the image bounds; zero or negative box area; a class outside the declared vocabulary; a mismatch between the declared and actual image dimensions.

#### 6.3 Illumination conformance — threshold

At least **30%** of the delivery's images satisfy the low-light criterion.

The criterion is a value of `brightness_median_v < 49.0`. The threshold is calibrated on the current dataset; for the methodology, see [docs/illumination_classification.md](illumination_classification-en.md). Acceptance applies the same code and the same threshold. Recalibrating the threshold to fit the delivery is not allowed — otherwise the criterion loses its meaning.

Acceptance separately records the illumination distribution within the delivery: the share of genuine low-light against scenes with artificial lighting. A claimed "night capture" consisting mostly of scenes with artificial lighting does not close the gap. Acceptance treats it as a non-conformance with section 3.

#### 6.4 Annotation-policy compatibility — non-threshold

Acceptance does not compute a quantitative agreement metric: a repeated blind annotation of the delivery at the scale of the stage is not provided for. Instead, acceptance applies two verification methods.

**Automatically, across the full delivery volume** — box statistics compared with the current dataset:

- the distribution of box aspect ratios;
- the distribution of box area and shorter side;
- the number of objects per frame;
- the share of boxes touching the frame border.

Acceptance treats a systematic shift in aspect ratio relative to the current dataset as an indirect sign of a different definition of box composition — for example, annotation of the body without rotors and supports.

**Visually, on a sample of at least 30 frames**, stratified by object size and illumination. Acceptance records:

- the definition of box composition — whether landing supports and rotor disks are included;
- how tightly the box fits;
- the presence of target-class objects left without annotation;
- the treatment of ambiguous objects.

The result is a list of divergences with anchors to specific frames. The annotation-policy divergence determines the amount of rework needed to bring the delivery to the current guideline. Acceptance factors it into the verdict.

#### 6.5 Duplication and novelty — threshold

- The share of internal duplicates (perceptual hash, Hamming distance ≤ 6) is no more than **5%**.
- Overlap with the current dataset — **zero** matches.
- If video-derived frames are present, acceptance additionally records the sequence structure. A delivery split into train/val/test at the frame level rather than the sequence level is accepted only with an explicit note that the splits need to be reconstructed.

#### 6.6 Domain gap — non-threshold

Acceptance compares the distributions of resolution, object size, and brightness with the current dataset.

The goal is twofold: to confirm that the stated gap is actually closed, and to assess whether the delivery differs from the existing data enough to be considered a separate domain. Acceptance records the result as a characteristic of the delivery and a basis for the decision on joint or separate use.

## 7. Acceptance outcomes

| Outcome | Condition |
|---|---|
| **Accepted** | all threshold criteria met, no material divergences on the non-threshold ones |
| **Accepted with remarks** | threshold criteria met; there are divergences on the non-threshold ones. Inclusion in the dataset is accompanied by documented limitations and an amount of rework |
| **Rejected** | at least one threshold criterion is violated. Acceptance adds a list of violations and required rework |

The thresholds are derived from the measured coverage gap of the project's own dataset; they were not revised based on the delivery outcome.

## 8. Versioning an accepted delivery

An accepted delivery enters the dataset as a separate source. This preserves the ability to separate it from the source data.

Acceptance records the provenance: source, the version of this specification, the acceptance date, the verdict, a link to the acceptance report. The dataset state before and after including the delivery is recoverable by commit.

## 9. Caveats

- The delivery simulates a public dataset; there was no vendor interaction. The object of evaluation is the acceptance process and its criteria, not a specific vendor.
- At the time the specification was fixed, only the published description of the candidate source is known; I did not measure the actual distributions. The thresholds are set from the dataset's need.
- Criterion 6.4 replaces a quantitative annotation-agreement assessment with a qualitative one. A full assessment requires blind annotation of a representative sample of the delivery with an IoU (intersection over union — a metric for the overlap of two boxes) computation, as done for the current dataset's gold set. That was not performed in this check.
