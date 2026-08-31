# cv-dataset-pipeline

This is a portfolio project. It shows an object-detection dataset pipeline: from ingesting heterogeneous sources to accepting external data deliveries.

My role was data management. I owned six areas:

- requirements specification;
- data structuring;
- annotation guidelines;
- annotation-agreement measurement;
- delivery acceptance.

## Data composition

The dataset combines two sources:

| Source | Class | Ingested, rows | Active rows | With target-class objects |
|---|---|---|---|---|
| VisDrone-DET | `vehicle` (merges car, van, truck, bus into a superclass) | 8,629 | 8,616 | 8,262 |
| Roboflow UAV (`aicup-5yzqf/uav-ajf13`) | `Drone` | 4,202 | 2,529 | 2,529 |
| **Total** | | **12,831** | **11,145** | **10,791** |

"Active rows" and "rows with target-class objects" are different quantities. In VisDrone, 354 active images contain no `vehicle` object. These are scenes with only non-target classes or only `ignore` service zones. Check: 8,616 − 8,262 = 354.

Active rows are the rows left after excluding duplicates. The pipeline excluded 1,686 images marked as duplicates. That is 13.1% of ingested rows (1,686 / 12,831 = 0.131). Duplicates stay physically present: the manifest marks each one with its method and rationale. All counters in the project documents are computed over active rows, unless stated otherwise.

Splits are assigned at the video-sequence level, not per individual frame. Active rows by split:

- train — 8,558;
- val — 817;
- test — 1,770.

The sum matches the total number of active rows: 8,558 + 817 + 1,770 = 11,145.

Target classes by objects:

- `vehicle` — 244,708 objects across 8,262 images;
- `Drone` — 2,731 objects across 2,529 images.

The imbalance is 89.60x by objects (244,708 / 2,731) and 3.27x by images (8,262 / 2,529). Details are in the [class_distribution-en.md](reports/class_distribution-en.md) report.

## What was done

Each item names the result, the action, and the report. Verbs are active; tense is past.

- **Structuring and deduplication.** I built a manifest registry with a schema contract. The registry surfaced a structural leak across splits: all 6 Roboflow sequences (60.8% of the source's rows) and 24 of 321 VisDrone sequences crossed split boundaries. I reconstructed the splits at the sequence level and removed the cross-split spillover. I confirmed the check at every step. See [data_intake_report-en.md](docs/data_intake_report-en.md).
- **Capture-condition classification.** I calibrated the illumination threshold visually on VisDrone and fixed it before applying it. Visual review of the darkest tail of both sources found no frames without an artificial light source. The classification rule therefore assigns only `day` and `artificial_light`. The `low_light` category stays declared and empty. The empty category records a fact: the dataset has no genuine low-light, and this is verified, not skipped. See [illumination_classification-en.md](docs/illumination_classification-en.md).
- **Annotation guidelines.** I wrote the guidelines separately for each class. The guidelines fix box geometry, occlusion, dense clusters, and edge cases. They include precedents I resolved during annotation. See [annotation_guidelines-en.md](docs/annotation_guidelines-en.md).
- **Gold set.** I selected 179 frames, stratified by three features: object density, illumination, and size coverage. I exported the frames blind — without annotations, provenance metadata, or EXIF, and with neutral filenames. See [gold_set_selection-en.md](reports/gold_set_selection-en.md).
- **Annotation-agreement measurement.** I measured the median IoU: 0.863 for `vehicle` and 0.750 for `Drone`. I decomposed the divergence into components and identified it as mostly stylistic. I classified unpaired boxes separately and did not fold them into an overall quality score. See [annotation_agreement-en.md](reports/annotation_agreement-en.md).
- **Data request specification.** I derived delivery acceptance criteria from the measured coverage gap of my own dataset. The criteria cover the identified `low_light` gap. I did not revise them based on the delivery outcome. See [data_request_spec_lowlight_drone-en.md](docs/data_request_spec_lowlight_drone-en.md).
- **External-delivery acceptance.** I rejected the DUT Anti-UAV delivery (10,000 images) on two threshold criteria. First: 4.65% low-light frames (465 of 10,000) against the required 30%. Second: 78.71% internal duplicates (7,871 of 10,000) against the allowed 5%. See [external_delivery_acceptance-en.md](reports/external_delivery_acceptance-en.md).

## Reading order

Read the documents in this order. Each item names the file and what you'll find in it.

1. [docs/project_charter.md](docs/project_charter-en.md) — subject, project boundaries, phases, dataset-readiness criteria.
2. [docs/data_intake_report.md](docs/data_intake_report-en.md) — source composition and deduplication.
3. [reports/class_distribution.md](reports/class_distribution-en.md) — target-class distribution.
4. [docs/illumination_classification.md](docs/illumination_classification-en.md) — illumination-condition classification and threshold calibration. The threshold of 49.0 from here is applied downstream without recalibration, including as a delivery acceptance criterion.
5. [docs/annotation_guidelines.md](docs/annotation_guidelines-en.md) — annotation guidelines.
6. [reports/gold_set_selection.md](reports/gold_set_selection-en.md) — selection methodology and blind export of the gold set.
7. [reports/annotation_agreement.md](reports/annotation_agreement-en.md) — annotation-agreement measurement.
8. [docs/data_request_spec_lowlight_drone.md](docs/data_request_spec_lowlight_drone-en.md) — data request specification. It fixes the acceptance criteria. I derived them from the measured coverage gap and did not revise them based on the delivery outcome.
9. External-delivery reports, in reading order:
   1. [reports/external_delivery_inventory.md](reports/external_delivery_inventory-en.md) — inventory of the delivery's composition, without a conformance assessment.
   2. [reports/external_delivery_acceptance.md](reports/external_delivery_acceptance-en.md) — acceptance check and final verdict against the specification criteria.
   3. [reports/external_delivery_annotation_review.md](reports/external_delivery_annotation_review-en.md) — visual review of the delivery's annotation policy.
10. [docs/sources_and_licenses.md](docs/sources_and_licenses-en.md) — provenance, licenses, and terms of use for each source, including the rejected delivery.

## Repository layout

Abbreviations used in the listing:

- **DVC** (Data Version Control) — a data-versioning system layered on top of Git.
- **CVAT** (Computer Vision Annotation Tool) — an annotation tool.
- **COCO** — an annotation format for object detection.
- **EXIF** — image metadata written by the camera.

```
README.md                  — this file
manifest.parquet           — sample registry: identifiers, splits, deduplication status, illumination
manifest_schema.py         — manifest schema contract: field types, enumerations, constraints
docs/                      — specifications and rules: charter, annotation guidelines, illumination
                             classification, data request specification, licenses, data intake report
reports/                   — measurement and acceptance results
reports/data/              — samples for visual checks (CSV)
reports/annotation_defects.parquet — per-object flags for delivery annotation defects (criterion 6.2)
gold_set/visdrone/         — 30 gold-set images + NOTICE.md
gold_set/roboflow/         — 149 gold-set images + LICENSE.txt
gold_set/annotations/      — project annotation of the gold set, exported from CVAT in COCO format
gold_set/gold_set_manifest.csv — mapping of export names to manifest identifiers
data/                      — DVC pointers to source data (the images themselves are not included)
.dvc/                      — DVC configuration
```

## Data

The repository contains no source images beyond the gold set. In their place, the manifest holds identifiers: `sample_id` (SHA-256 of the file bytes) and the path. Using these identifiers, you can reconstruct the set from the public sources.

The gold set is included in the repository. I split it by source, because the sources' license regimes differ and don't allow a single license for a mixed set. Each directory carries its own license file or `NOTICE`. Details are in [docs/sources_and_licenses.md](docs/sources_and_licenses-en.md).

The DVC configuration is provided as a versioning scheme, not as a working store. The remote is local: `F:\dvc-storage\cv-dataset-pipeline`. A third-party reader therefore cannot restore the data from this configuration — a `dvc pull` from this repository will not work.

## Limitations

The project has four known limitations:

- I did not measure inter-annotator agreement.
- I did not measure annotation process metrics.
- I did not perform auto-assisted annotation.
- The ground-truth annotation is external.

The rationale and consequences of these limitations are described in [project_charter-en.md](docs/project_charter-en.md), section 7, and in the dataset-readiness criteria, section 9.

Limitations of individual measurements are given in the respective reports:

- annotation agreement — [annotation_agreement-en.md](reports/annotation_agreement-en.md), section 11;
- illumination classification — [illumination_classification-en.md](docs/illumination_classification-en.md), the "Limitations" section.
