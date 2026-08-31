# Data sources: provenance, licenses, terms of use

**License-check date:** 2026-08-09.

## 1. Roboflow UAV

**Identifier:** `aicup-5yzqf/uav-ajf13`, Roboflow Universe.
**URL:** https://universe.roboflow.com/aicup-5yzqf/uav-ajf13

**Dataset version:** 1 (`uav-ajf13/1`), 4,202 images. The project page states 4,367 images. The divergence is explained by the difference between the project's total image count and the composition of a specific version. This work uses version 1 — 4,202 images.

**Source class:** `drone` (in the project manifest — `Drone`).

**License:** CC BY 4.0. The dataset page states it in two places: in the header next to the Task field and in the Cite This Project block.

**Terms:** permit use, modification, and distribution, including commercial, provided attribution is given.

**Attribution** (as stated on the project page):

> author: aicup, title: uav Dataset, publisher: Roboflow Universe, year: 2022, URL: https://universe.roboflow.com/aicup-5yzqf/uav-ajf13

**Project decision:** the project includes the gold-set images from this source (149 frames) in the repository, with an accompanying license file and attribution.

**Versioning of the source annotation.** DVC (Data Version Control) pins both the images and the source annotation: the pointer `data/uav-raw.dvc` tracks 4,205 files — images together with three COCO (Common Objects in Context) annotation files. Consequence: the numeric results for class `Drone` are reproducible from DVC without going back to the source. For VisDrone there is no such coverage: only the images are under versioning there (section 2).

## 2. VisDrone-DET

**Primary source:** the AISKYEYE team, Lab of Machine Learning and Data Mining, Tianjin University.
**Repository URL:** https://github.com/VisDrone/VisDrone-Dataset
**Team website URL:** https://aiskyeye.com

Downloaded through the Hugging Face mirror `Voxel51/VisDrone2019-DET`.

**License status:**

- There is no formal license: neither a license file nor a terms-of-use section exists in the primary source's repository or on the team website. The Download, Introduction, and "data and code" sections were checked.
- The Download section of aiskyeye.com contains written permission to download and use the datasets.
- Distribution terms are not defined.
- Mirrors state inconsistent licenses. The `Voxel51/VisDrone2019-DET` card on Hugging Face declares `cc-by-sa-3.0`, but the text of that same card mentions a restriction on commercial use. This is third-party labeling; the primary source does not confirm it.

**Attribution required by the authors:**

> Zhu P., Wen L., Du D. et al. Detection and Tracking Meet Drones Challenge. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2021. DOI 10.1109/TPAMI.2021.3119563.

**Project decision:** the project includes 30 gold-set images (0.35% of the source) in the repository as an illustration of the gold-set construction and annotation-divergence analysis methodology. There is no commercial use; the set does not reproduce or replace the primary source. On the rights holder's request, the project will remove the images.

**Versioning of the source annotation.** DVC pins only the source images: the pointer `data/visdrone.dvc` tracks 8,629 `.jpg` files and no annotation files. The source annotation came from Hugging Face through FiftyOne and is not under versioning. Consequence: to reproduce the numeric results for class `vehicle`, the annotation must be obtained separately from Hugging Face — it is not recoverable from DVC. For Roboflow UAV there is no such gap: three COCO files are pinned under DVC together with the images.

## 3. DUT Anti-UAV — external delivery in acceptance (rejected)

This source went through acceptance as an external delivery against the request to close the low-light gap and did not enter the dataset. This section records the delivery's license status. Acceptance checked it as part of criterion 6.1, "formal completeness."

**Identifier:** DUT Anti-UAV, detection subset.
**Repository URL:** https://github.com/wangdongdut/DUT-Anti-UAV

**License:** Apache-2.0, per the source repository's description. There is no license text in the delivery itself: no LICENSE or README files and no metadata were found in the archives ([inventory](../reports/external_delivery_inventory-en.md), sections 1 and 6). The license traces to the source but is not confirmed by the delivery's contents.

**License terms:** permit use, modification, and distribution, including commercial, on three conditions: retain the copyright notice, retain the license text, state the changes made in modified files.

**Status:** the delivery is **rejected** based on the acceptance result — threshold criteria 6.3 and 6.5 were violated ([acceptance report](../reports/external_delivery_acceptance-en.md)). The project did not include it in the dataset or the repository and did not add it to `manifest.parquet` and DVC. The delivery's images are not distributed: the archives remained in the staging directory, and no image is reproduced in the portfolio.

Since there is no distribution, the obligations regarding attribution and stating changes do not arise.

## 4. Summary and packaging consequences

| Source | License | Distribution permitted | Project decision |
|---|---|---|---|
| Roboflow UAV (`aicup-5yzqf/uav-ajf13`) | CC BY 4.0 | Yes, including commercial use, with attribution | 149 gold-set images included in the repository with a license file and attribution |
| VisDrone-DET (AISKYEYE, via the Voxel51 mirror) | Not declared by the primary source; download and use permitted; distribution terms not defined | Not defined | 30 images (0.35% of the source) included as an illustration of methodology; no commercial use; removed on the rights holder's request |
| DUT Anti-UAV (`wangdongdut/DUT-Anti-UAV`) | Apache-2.0 per the repository description; license text absent from the delivery | Yes, provided the copyright notice is retained and changes are stated | Delivery rejected in acceptance; not included in the dataset or repository, images not distributed |

The first two sources are under different legal regimes. So the project packages the gold set separately by source rather than as a single directory: assigning one license to a mixed set is impossible. The DUT Anti-UAV delivery does not participate in packaging — it is rejected and not part of the repository.

**Target structure:**

```
gold_set/roboflow/               — images, CC BY 4.0 license file, attribution
gold_set/visdrone/                — images, NOTICE file with the decision text from section 2
gold_set/annotations/             — annotation created within the project
gold_set/gold_set_manifest.csv    — mapping of names to manifest identifiers
```

The gold-set annotation was created within the project and is not derived from the sources' annotation: the annotator annotated the images blind, and the source annotations were not shown during the annotation stage.
