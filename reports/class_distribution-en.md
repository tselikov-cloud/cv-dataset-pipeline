# Target-class distribution

## Purpose

This computation provides the quantitative basis for the data request specification and for gold-set stratification: the count of objects and images per target class, the distribution of the object count per image, the class ratio.

The goal of the computation is to give a reproducible source for the numbers on which the coverage-gap rationale and the class-imbalance assessment are built.

## Method

**Annotation source.** The computation takes the source annotation of the sources — the same one the manifest was assembled from: VisDrone — the `ground_truth` field of the `visdrone` dataset; Roboflow UAV — the `ground_truth_detections` field of the `uav-roboflow-train`, `-valid`, `-test` datasets. I additionally reconciled the class `Drone` annotation against the source's COCO files on disk (`data/uav-raw/{train,valid,test}/_annotations.coco.json`): an independent recount gives the same object and image counts.

**Computation base.** The active manifest rows (`dedup_status == "active"`) — 11,145 rows: VisDrone 8,616, Roboflow UAV 2,529. Rows marked `duplicate` are excluded entirely, together with their annotation. The computation joins the annotation to the manifest by file name. Name uniqueness among the active rows and the source match for each row are verified.

**Class-assignment rules.** `vehicle` is the union of the source VisDrone subclasses `car`, `van`, `truck`, `bus`. `Drone` is the single Roboflow UAV class (in the source, `drone`). The source-label vocabulary is closed: a label outside the known vocabulary aborts the computation.

**Counting unit.** An object is one bounding box (bbox). The computation counts an image toward a class if it contains at least one object of that class. The computation counts the distribution of objects per image only over images that contain at least one object of the respective class.

The computation only reads the manifest and the annotation; it writes nothing to the data or the manifest.

## Objects and images by class

| Class | Objects | Images with ≥1 object | Source |
|---|---|---|---|
| `vehicle` | 244,708 | 8,262 | VisDrone |
| `Drone` | 2,731 | 2,529 | Roboflow UAV |

Breakdown of `vehicle` by the source VisDrone subclasses:

| Subclass | Objects | Share of `vehicle` |
|---|---|---|
| `car` | 186,663 | 76.28% |
| `van` | 32,667 | 13.35% |
| `truck` | 16,268 | 6.65% |
| `bus` | 9,110 | 3.72% |
| **Total `vehicle`** | **244,708** | **100%** |

Breakdown by split:

| Class | train | val | test | Total |
|---|---|---|---|---|
| `vehicle`, objects | 189,207 | 16,057 | 39,444 | 244,708 |
| `vehicle`, images | 6,207 | 491 | 1,564 | 8,262 |
| `Drone`, objects | 2,224 | 330 | 177 | 2,731 |
| `Drone`, images | 2,071 | 298 | 160 | 2,529 |

## Objects per image

The numbers below count only images that contain at least one object of the respective class.

| Class | Images | min | median | p95 | max |
|---|---|---|---|---|---|
| `vehicle` | 8,262 | 1 | 23 | 78 | 349 |
| `Drone` | 2,529 | 1 | 1 | 2 | 13 |

The classes differ not only in volume but in the structure of their presence in the frame. `vehicle` yields dense scenes — a median of 23 objects per frame. `Drone` yields practically one object per frame (median 1, p95 equals 2). This matches the source profile: in most frames, the drone is the main subject.

## Class ratio

| Comparison base | Ratio |
|---|---|
| By objects | 89.60x (244,708 / 2,731) |
| By images | 3.27x (8,262 / 2,529) |

The two ratios answer different questions and do not reduce to a single number. The ratio by objects characterizes the imbalance at the instance level. The ratio by images characterizes how many frames must be included in a sample for the class to be represented in it. It is an order of magnitude smaller precisely because `Drone` occurs one per frame, while `vehicle` occurs by the dozens.

For gold-set stratification, the decisive ratio is the one by images: a random sample by frames would underrepresent `Drone` threefold, not ninetyfold.

## What is not part of the computation

**Non-target VisDrone classes.** Objects of these classes exist in the source annotation but are not part of the project's target taxonomy, so the computation does not count them (the numbers are over the active rows):

| Class | Objects |
|---|---|
| `pedestrians` | 109,060 |
| `motor` | 40,283 |
| `people` | 38,430 |
| `bicycle` | 12,985 |
| `tricycle` | 6,378 |
| `awning_tricycle` | 4,371 |
| `others` | 1,829 |

The class `others` is excluded on the same grounds as the rest of the non-target ones: it is a separate label of the source VisDrone annotation, not part of the `vehicle` superclass. I did not examine its contents — it takes no part in the merge into `vehicle`.

**The `ignore_regions` zones.** In the VisDrone annotation, `ignore_regions` are stored not as a separate field but as ordinary objects in the same list as the target classes. Over the active rows — 12,357 zones across 3,515 images. The computation excludes these zones by label: they are area masks, not objects, and do not enter the class object count.

The computation does not count the objects inside the `ignore_regions` zones by definition: inside a zone there is no per-object annotation — that is its purpose. The numbers above are the count of the zones themselves, not the count of objects hidden within them.

**Images without target-class objects.** 354 active VisDrone images contain no object of class `vehicle` — these are scenes with only non-target classes or only `ignore_regions` zones. In Roboflow UAV there are no such images: all 2,529 contain at least one object of class `Drone`.

## Limitations

The computation relies on the source annotation and inherits its properties: it measures what is annotated, not what is present in the frames. Objects missed in the source annotation are not reflected in these numbers. I assessed the divergence of the project annotation from the source separately, on the gold set ([annotation_agreement-en.md](annotation_agreement-en.md)); it does not carry over into this distribution.

The numbers are tied to the manifest state at the time of the computation — 11,145 active rows, before the inclusion of any external deliveries. The DUT Anti-UAV delivery is not included in the dataset (rejected under the acceptance criteria), so it is not in these numbers.

The `vehicle` subclasses are given as a breakdown of the source annotation. In the project's target taxonomy they are merged and not used separately: distinguishing subtypes is not the task's objective (rationale — `project_charter.md`, section 3).

Capture-condition coverage takes no part in this computation. The illumination classification across the whole active dataset is in [illumination_classification-en.md](../docs/illumination_classification-en.md); the remaining conditions are assessed on a sample.
