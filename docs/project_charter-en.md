# Project Charter — cv-dataset-pipeline

## 1. Purpose

The project's goal is to build an end-to-end pipeline for working with a computer-vision (CV) dataset. The pipeline covers ingesting heterogeneous sources, versioning, annotation, accepting external data deliveries, and data quality control.

## 2. Project scope

**In scope:**

- two sources: VisDrone-DET (8,629 rows) and Roboflow UAV (4,202 rows);
- two target classes: `vehicle` (VisDrone superclass: car, van, truck, bus) and `Drone` (Roboflow UAV);
- class distribution across the whole dataset; the project assesses condition coverage on a stratified sample;
- annotation guidelines and manual annotation of a stratified gold set of 179 images;
- dataset specification: translating machine-learning (ML) requirements into dataset-readiness criteria;
- accepting external deliveries as a process: a request spec against an identified gap → receiving the delivery → QA acceptance against criteria derived from the measured coverage gap and not revised based on the delivery outcome → an inclusion decision and versioning with provenance recorded;
- versioning the source data by source via DVC; the project versions the dataset state via a manifest in git.

**Out of scope:**

- model training and model metrics;
- building a synthetic-data generator. The project runs external data of any kind as a vendor process: scenario prioritization, specification, acceptance;
- the remaining VisDrone and Roboflow classes beyond the two target ones;
- inter-annotator agreement — see section 7;
- auto-assisted annotation at scale — see section 7;
- operational process metrics (throughput, cycle time, error rate) — see section 7.

## 3. Dataset

The dataset composition after deduplication (see `data_intake_report.md`):

| State | Count |
|---|---|
| Total ingested | 12,831 |
| Active | 11,145 |
| Marked duplicate | 1,686 |

The project reconstructed the splits at the sequence level after finding frame-level leakage in both sources. The breakdown:

- by active rows: train 8,558 / val 817 / test 1,770;
- by all ingested rows: train 10,197 / val 858 / test 1,776.

Zero leakage was confirmed at every step.

**Taxonomy:**

- `vehicle` — target object: four-wheeled motor transport. The project excludes pedestrians and two- and three-wheeled transport as unrelated to the task. The VisDrone classes car, van, truck, bus are merged into a superclass. Subtype discrimination is not part of the detection task, and the boundary between subtypes is a source of annotation divergences that requires separate rules and separate quality control. Merging removes this source.
- `Drone` — from Roboflow UAV. The task is counter-UAV detection: the drone as an object in the frame, not as the camera platform.

The project's target-class name is `Drone`. The label `uav` refers to the data source (Roboflow UAV, source class `drone`), not to the target class. For the rationale of the name choice, see `annotation_guidelines.md`, class `Drone`, the "Class composition" section: the class is defined by the visual feature of an aircraft, not by the absence of a pilot.

## 4. Phases

**Phase 1 — Structuring.** A manifest registry with a schema contract, deduplication by two hashes (SHA-256 and perceptual), reconstruction of the splits at the sequence level. Artifact: data intake report.

**Phase 2 — Versioning.** Configuring the DVC remote, versioning the source data by source. The project versions the manifest in git; data and manifest are synchronized by commit.

**Phase 3 — Annotation.** Annotation guidelines. The manual annotation of the gold set was done under these guidelines: the source annotation is hidden, the annotator annotates blind. Artifacts: annotation guidelines, gold set.

**Phase 4 — Accepting external deliveries of real data.** The project computes class distribution across the whole dataset and condition coverage on a sample. The request spec serves as a vendor brief against the measured coverage gap. The project received an external delivery (DUT Anti-UAV) and performed an acceptance check against criteria derived from the measured coverage gap and not revised based on the delivery outcome: conformance to the request spec, annotation validity, domain-gap assessment. The result is a verdict on the delivery with a rationale. Artifacts: request spec, QA acceptance report.

The delivery was obtained from a public dataset; there was no vendor interaction. The acceptance criteria do not depend on the nature of the delivery: the project applies the same criteria to any external delivery, including synthetic.

**Phase 5 — Annotation-quality metrics.** IoU (intersection over union — a metric for the overlap of two boxes) of the manual annotation of the gold set against the source annotation, per class separately. The project classifies unpaired boxes (present in one annotation and absent in the other) separately, rather than folding them into an overall IoU.

Artifact: metrics report.

## 5. Coverage gaps (Phase 4)

Both sources are visually narrow, but in different ways. They are nearly complementary in viewpoint and coincide in what they lack.

**VisDrone (`vehicle`).** The viewpoint is mostly fixed and high — an "isometric" top-down look. Scene variety is low: dense urban development, highways, urban locations. The viewpoint barely changes. Night frames exist, but they are lit by street lamps, so this is not genuine low-light. Genuine low-light is capture under insufficient natural lighting with no artificial light sources in the frame. Night scenes with street lighting do not belong to it. For illumination classification and the threshold, see [illumination_classification-en.md](illumination_classification-en.md).

**Roboflow UAV (`Drone`).** The inverse profile. High diversity of viewpoints, locations, and drone models. The source is heterogeneous in origin: some frames are cut from video, some are single photographs, and capture quality varies. The shots are taken mostly from the ground; frames from altitude, over water, and shot from other craft occur. In most frames, the drone is the main subject. Lighting is mostly good.

**Shared gap.** The conditions are separated by how they are established:

- **Illumination.** The conclusion of a visual review of the darkest tail of both sources: I found no frames shot without an artificial light source, and no genuine low-light was observed in the sources.
- **Infrared spectrum, smoke and atmospheric obscuration, heavy partial occlusion.** I did not measure these: these conditions were not observed while reviewing the sources, and the share of frames with them is not established.
- **Class `Drone` incidentally in the frame.** Frames where the craft entered the field of view incidentally, rather than as the subject, are rare in the sources.

**Quantification method.** The project computes class distribution across the whole active dataset. It determines both the size of the gap and how the gold set is stratified: a random sample would underrepresent the rare class.

The project assesses condition coverage rather than annotating it fully. Illumination is a cheap signal (day/night from image statistics), so it is computed across all images of the active set. The other axes — viewpoint, location type, occlusion, visibility — were not annotated on a stratified sample, and there is no measurement for them. The request spec must establish the absence of certain conditions, and absence is demonstrable on a sample — annotating all 11,145 images is not required.

## 6. Artifacts

| Artifact | Purpose |
|---|---|
| Data intake report | Source composition, deduplication, structural findings, final dataset composition |
| DVC-versioned dataset | Reproducibility: data and manifest synchronized by commit |
| Class distribution + condition coverage | Quantitative basis for the request spec and gold-set stratification: target-class distribution ([class_distribution-en.md](../reports/class_distribution-en.md)), illumination-condition classification across the whole active dataset ([illumination_classification-en.md](illumination_classification-en.md)) |
| Annotation guidelines | Annotation rules in working form: classes, edge cases, occlusion, minimum bounding-box (bbox) size |
| Gold set + per-class IoU | Reference annotation and the measured divergence from the source, including a breakdown of the direction of divergences for `Drone` ([annotation_agreement-en.md](../reports/annotation_agreement-en.md)) |
| Dataset specification | Dataset-readiness criteria: what counts as an acceptable result. Section 9 of this document implements it; there is no separate document |
| Request spec: closing the low-light gap | Data request specification and delivery acceptance criteria, derived from the measured coverage gap and not revised based on the delivery outcome ([data_request_spec_lowlight_drone-en.md](data_request_spec_lowlight_drone-en.md)) |
| QA acceptance of the DUT Anti-UAV delivery | Inventory, an acceptance check against criteria 6.2, 6.3, 6.5, 6.6, and a visual review of annotation policy ([external_delivery_inventory-en.md](../reports/external_delivery_inventory-en.md), [external_delivery_acceptance-en.md](../reports/external_delivery_acceptance-en.md), [external_delivery_annotation_review-en.md](../reports/external_delivery_annotation_review-en.md)) |

## 7. Limitations

**Inter-annotator agreement is not measured.** IAA (inter-annotator agreement) requires a second annotator: with a single annotator, the metric is impossible. The metric is mandatory and tracked continuously. A single annotator did the annotation in this project.

**Process metrics (throughput, cycle time, error rate) are not measured.** The annotation was done without time instrumentation, and a retrospective estimate is not a measurement. These metrics are taken from the annotation system; they serve as the basis for planning volume, deadlines, and evaluating the performer. Error rate additionally requires an independent reviewer — for the same reason as inter-annotator agreement.

**Auto-assisted annotation was not performed.** The project's target annotation artifact is the gold set and the guidelines, not a fully annotated dataset. Scaling annotation with a model followed by review belongs to the ML team's execution zone and was not part of the scope.

**Synthetic generation was not performed.** Building a synthetic-data generator was not part of the scope. The project exercised the external-delivery acceptance loop on real data; the acceptance criteria do not depend on the nature of the delivery.

**The label space is heterogeneous across sources.** In the project's label space, VisDrone is represented only by class `vehicle`, and Roboflow UAV only by class `Drone`. Neither source is annotated for both classes. A significant share of VisDrone frames are shot from a fixed high viewpoint, and some frames from an altitude atypical for the rest of the set. Craft of class `Drone` were not observed in the frames; this was not verified by measurement.

Consequence: the absence of a box is not a negative example for a class that was not annotated in that source. In joint training of a two-class detector on the union of sources, unannotated objects enter training as background.

The share of Roboflow frames with unannotated transport is not measured.

**Ground truth.** Both datasets arrived annotated. Based on review, the annotation of both looks coherent and of good quality. The method is the same for both classes: the project hides the source annotation on a subsample, the annotator annotates images blind by the rules, and the result is measured by IoU against the source.

The limitation is that ground truth here is external: the reference belongs to a third-party source rather than being created within the project. How acceptable that is depends on the project's goals and policy. In this case, the project accepts the external annotation as the reference and the baseline. In other cases, it may itself require revision and QA for conformance to internal rules.

## 8. Environment

| Component | Purpose |
|---|---|
| FiftyOne | Dataset review, visual revision, similarity search |
| DVC (Data Version Control) | Versioning of data and the manifest |
| CVAT (Computer Vision Annotation Tool) | Manual annotation |
| Pandas / PyArrow | Manifest (Parquet), analytics |
| Pydantic | Manifest schema contract |

## 9. Dataset-readiness criteria

This section defines the conditions under which the dataset is fit to hand over to the ML team. It implements the dataset specification (section 6): there is no separate document.

| Criterion | Threshold | Status |
|---|---|---|
| Sequence-level split leakage | zero | met |
| Leakage by groups of perceptually identical frames | zero among active rows | met |
| Duplication | a flag on every duplicate, canonical sample determined | met |
| Manifest schema | all rows pass contract validation | met |
| Provenance | source, license, and terms of use recorded per source | met |
| Reproducibility of dataset state | the delivered state is recoverable by commit | achieved. DVC versions the source data by source, git versions the manifest, and the state is synchronized by commit. Intermediate states are not tagged. The VisDrone source annotation is not pinned under DVC (see [sources_and_licenses-en.md](sources_and_licenses-en.md)) |
| Label space declared per source | class coverage recorded for each source | met. In the project's label space, VisDrone is represented only by class `vehicle`, Roboflow UAV only by class `Drone`; the consequences for training are in §7 |
| Target-class distribution | measured over the full active set | met ([class_distribution-en.md](../reports/class_distribution-en.md)) |
| Annotation guidelines | documented, covering box geometry, occlusion, dense clusters, and edge cases | met |
| Annotation divergence from the source | measured on the gold set, divergences categorized by type without deriving a single quality score | met |
| Dataset annotation brought to the project's rules | not set | not achieved. Only the gold set (179 frames) is annotated by the project's rules. The remaining active images carry the source's original annotation, not reviewed against the project's rules. The magnitude of the divergence is measured and documented ([annotation_agreement-en.md](../reports/annotation_agreement-en.md)) |
| External deliveries | accepted only through criteria derived from the measured coverage gap and not revised based on the delivery outcome | met |
| Measurement of capture-condition coverage | all coverage axes measured, gaps documented | not achieved. Illumination is measured across the whole active set ([illumination_classification-en.md](illumination_classification-en.md)); viewpoint, location type, occlusion, and visibility were not annotated |
| Condition coverage: genuine low-light | not set | not achieved. The condition was not observed in the dataset: a visual review of the darkest tail of both sources found no frames without an artificial light source, so the classification rule does not assign the `low_light` category and it remains empty ([illumination_classification-en.md](illumination_classification-en.md)). The request spec is written; the candidate delivery did not pass the acceptance criteria |
| Target-class balance | not set | not achieved. Imbalance of 89.60x by objects, 3.27x by images ([class_distribution-en.md](../reports/class_distribution-en.md)). Closing it requires additional data of class `Drone`. Interpreting the figure depends on the heterogeneity of the label space — see the corresponding criterion above and §7 |
| Annotation uncertainty quantified | not set | not achieved. The spread between independent annotators is not measured, and the annotation noise level is unknown (§7) |
| Residual near-duplicates across splits | zero pairs within the threshold radius | not achieved. 7 pairs at Hamming distance 6 (Roboflow UAV) remain active — a consequence of the complete-linkage rule, see [data_intake_report-en.md](data_intake_report-en.md). |
