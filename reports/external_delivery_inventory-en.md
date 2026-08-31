# Inventory of the DUT Anti-UAV delivery (detection subset)

**Status:** delivery in acceptance. Not added to `manifest.parquet`, not tracked in DVC, not placed in `data/`.
**Location:** a staging directory, separate from the dataset. Deliveries in acceptance sit there until the verdict is issued: they are not entered into the sample registry and not versioned, and on rejection they do not enter the version history as accepted.
**Acceptance specification:** [docs/data_request_spec_lowlight_drone.md](../docs/data_request_spec_lowlight_drone-en.md).

This document contains only inventory facts. It does not assess conformance to the acceptance criteria (section 6 of the specification).

## 1. Source and download

- **Source:** https://github.com/wangdongdut/DUT-Anti-UAV, Apache-2.0 license (per the repository description; I did not find the license text in the delivery itself — see section 6).
- **Method of obtaining:** three archives from Google Drive via `gdown`, by direct `file_id`.
- **Download date:** 2026-08-03 (UTC, see the table below).
- **Method:** three sequential steps. First I downloaded the archives, computing SHA-256 and writing a manifest. Then I unpacked them, preserving the structure. Then I gathered inventory facts: counts, formats, annotations, resolutions, orphans, corrupted files.

### Archive SHA-256

| Split | File | Google Drive file_id | Size, bytes | SHA-256 | Downloaded (UTC) |
|---|---|---|---|---|---|
| train | `train.zip` | `1RVsSGPUKTdmoyoPTBTWwroyulLek1eTj` | 744,616,230 | `14f927290556df60e23cedfa80dffc10dc21e4a3b6843e150cfc49644376eece` | 2026-08-03T22:02:30.747073+00:00 |
| val | `val.zip` | `1333uEQfGuqTKslRkkeLSCxylh6AQ0X6n` | 372,283,691 | `238be0ceb3e7c5be6711ee3247e49df2750d52f91f54f5366c68bebac112ebf8` | 2026-08-03T22:03:10.310950+00:00 |
| test | `test.zip` | `1L1zeW1EMDLlXHClSDcCjl3rs_A6sVai0` | 271,153,425 | `a671989a01cff98c684aeb084e59b86f4152c50499d86152eb970a9fc7fb1cbe` | 2026-08-03T22:03:50.245966+00:00 |

I computed the hashes twice by independent methods (Python `hashlib.sha256` and `sha256sum`) — they match. The full download manifest is saved in the staging directory as a separate file.

The archives are saved unchanged in the staging directory. The total volume of the archives is ≈1.39 GB, of the unpacked data — 1.4 GB.

## 2. Delivery structure after unpacking

Unpacked into the staging directory, the original folder structure from the archives preserved.

```
.
├── test/
│   ├── img/
│   │   ├── 00001.jpg
│   │   ├── 00002.jpg
│   │   └── 00003.jpg
│   │       ... (+2197 files)
│   └── xml/
│       ├── 00001.xml
│       ├── 00002.xml
│       └── 00003.xml
│           ... (+2197 files)
├── train/
│   ├── img/
│   │   ├── 00001.jpg
│   │   ├── 00002.jpg
│   │   └── 00003.jpg
│   │       ... (+5197 files)
│   └── xml/
│       ├── 00001.xml
│       ├── 00002.xml
│       └── 00003.xml
│           ... (+5197 files)
└── val/
    ├── img/
    │   ├── 00001.jpg
    │   ├── 00002.jpg
    │   └── 00003.jpg
    │       ... (+2597 files)
    └── xml/
        ├── 00001.xml
        ├── 00002.xml
        └── 00003.xml
            ... (+2597 files)
```

Each split (`train`, `val`, `test`) contains two subfolders: `img/` (images) and `xml/` (annotations). I found no other directories or files inside the archives besides `img/` and `xml/`.

## 3. Image count by split

Numeric table (shared for both revisions, given once):

| Split | Declared | Actual (images) | Actual (annotations) | Difference from declared |
|---|---|---|---|---|
| train | 5,200 | 5,200 | 5,200 | 0 |
| val | 2,600 | 2,600 | 2,600 | 0 |
| test | 2,200 | 2,200 | 2,200 | 0 |
| **Total** | **10,000** | **10,000** | **10,000** | **0** |

## 4. Image file extensions and formats

| Split | Extension | File count | Format (per Pillow) |
|---|---|---|---|
| train | `.jpg` | 5,200 | JPEG — 5,200 |
| val | `.jpg` | 2,600 | JPEG — 2,600 |
| test | `.jpg` | 2,200 | JPEG — 2,200 |
| **Total** | `.jpg` | **10,000** | **JPEG — 10,000** |

I found no other extensions (`.png`, `.jpeg`, `.bmp`, etc.). The file extension in all cases matches the actual format determined from the contents.

## 5. Annotation location and format

- **Location:** `<split>/xml/`, a directory separate from the images (`<split>/img/`).
- **Format:** XML, Pascal VOC (Visual Object Classes) schema: `<annotation>` → `<size>`, `<object>` → `<bndbox>`.
- **Correspondence:** one annotation per image (the file `xml/00001.xml` corresponds to `img/00001.jpg`, and so on by number), not a shared file for the whole split.
- **Coordinate system:** absolute pixel coordinates, axes `xmin`, `ymin`, `xmax`, `ymax` (the top-left and bottom-right corner of the box in pixels of the source image). The origin is the top-left corner of the image (the standard Pascal VOC convention).
- **Declared object class:** `UAV` — the only value of the `<name>` field I encountered in all three splits.
- **Additional object fields:** `<pose>` (everywhere `Unspecified`), `<truncated>`, `<difficult>` (everywhere `0` in the reviewed files).
- **The `<size>` field:** contains `width`, `height`, `depth` — the image dimensions declared by the delivery's producer.

### Contents of the first annotations verbatim

The XML blocks below are given verbatim, shared for both revisions. They need no changes.

**`train/xml/00001.xml`:**
```xml
<annotation>
	<folder>train</folder>
	<filename>00001.jpg</filename>
	<path>./train/00001.jpg</path>
	<source>
		<database>DUT Anti-UAV Detection</database>
	</source>
	<size>
		<width>550</width>
		<height>412</height>
		<depth>3</depth>
	</size>
	<segmented>0</segmented>
	<object>
		<name>UAV</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>228</xmin>
			<ymin>155</ymin>
			<xmax>353</xmax>
			<ymax>245</ymax>
		</bndbox>
	</object>
</annotation>
```

**`train/xml/00002.xml`:**
```xml
<annotation>
	<folder>train</folder>
	<filename>00002.jpg</filename>
	<path>./train/00002.jpg</path>
	<source>
		<database>DUT Anti-UAV Detection</database>
	</source>
	<size>
		<width>1000</width>
		<height>667</height>
		<depth>3</depth>
	</size>
	<segmented>0</segmented>
	<object>
		<name>UAV</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>272</xmin>
			<ymin>107</ymin>
			<xmax>765</xmax>
			<ymax>491</ymax>
		</bndbox>
	</object>
</annotation>
```

**`val/xml/00001.xml`:**
```xml
<annotation>
	<folder>val</folder>
	<filename>00001.jpg</filename>
	<path>./val/00001.jpg</path>
	<source>
		<database>DUT Anti-UAV Detection</database>
	</source>
	<size>
		<width>527</width>
		<height>300</height>
		<depth>3</depth>
	</size>
	<segmented>0</segmented>
	<object>
		<name>UAV</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>258</xmin>
			<ymin>52</ymin>
			<xmax>370</xmax>
			<ymax>122</ymax>
		</bndbox>
	</object>
</annotation>
```

**`val/xml/00005.xml`** (an example of a file with several objects in the frame):
```xml
<annotation>
	<folder>val</folder>
	<filename>00005.jpg</filename>
	<path>./val/00005.jpg</path>
	<source>
		<database>DUT Anti-UAV Detection</database>
	</source>
	<size>
		<width>640</width>
		<height>384</height>
		<depth>3</depth>
	</size>
	<segmented>0</segmented>
	<object>
		<name>UAV</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>556</xmin>
			<ymin>175</ymin>
			<xmax>626</xmax>
			<ymax>229</ymax>
		</bndbox>
	</object>
	<object>
		<name>UAV</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>456</xmin>
			<ymin>309</ymin>
			<xmax>496</xmax>
			<ymax>339</ymax>
		</bndbox>
	</object>
	<object>
		<name>UAV</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>268</xmin>
			<ymin>289</ymin>
			<xmax>312</xmax>
			<ymax>322</ymax>
		</bndbox>
	</object>
	<object>
		<name>UAV</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>13</xmin>
			<ymin>265</ymin>
			<xmax>63</xmax>
			<ymax>304</ymax>
		</bndbox>
	</object>
	<object>
		<name>UAV</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>205</xmin>
			<ymin>105</ymin>
			<xmax>310</xmax>
			<ymax>191</ymax>
		</bndbox>
	</object>
	<object>
		<name>UAV</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>98</xmin>
			<ymin>55</ymin>
			<xmax>160</xmax>
			<ymax>106</ymax>
		</bndbox>
	</object>
</annotation>
```

### Number of objects per annotation file

| Split | Min. objects/file | Max. objects/file | Files with 0 objects | Files with >1 object |
|---|---|---|---|---|
| train | 0 | 6 | 3 | 29 |
| val | 1 | 6 | 0 | 13 |
| test | 1 | 3 | 0 | 33 |

The total number of class `UAV` objects across all annotations: train — 5,243; val — 2,621; test — 2,245 (10,109 objects across 10,000 images in total).

## 6. README, LICENSE, metadata

I found **no** README, LICENSE, format-description, or separate metadata files — neither in the unpacked delivery nor inside the archives themselves (checked by a sequential review of the `.zip` contents before unpacking). The only file types in the delivery are `.jpg` images and `.xml` annotations.

The download-manifest file in the staging directory is not part of the delivery: I created it as part of this inventory to record the SHA-256 and download parameters.

## 7. Images without annotation and annotations without image

| Split | Images without annotation | Annotations without image |
|---|---|---|
| train | 0 | 0 |
| val | 0 | 0 |
| test | 0 | 0 |
| **Total** | **0** | **0** |

I checked correspondence by the match of the base file name (number) between `img/` and `xml/` within each split.

## 8. Corrupted image files

| Split | Number of corrupted files (did not open as an image) |
|---|---|
| train | 0 |
| val | 0 |
| test | 0 |
| **Total** | **0** |

I performed the check via `PIL.Image.open().verify()` for each file.

## 9. Image resolutions

The tables are numeric, shared for both revisions, given once. The prose caption after them is given as a pair.

### Summary over the whole delivery (10,000 images)

| Parameter | Width | Height |
|---|---|---|
| Minimum | 240 px | 160 px |
| Maximum | 5616 px | 3744 px |
| Median | 1920 px | 1080 px |

### Top 10 most frequent resolutions (whole delivery)

| Resolution (W×H) | Image count |
|---|---|
| 1920×1080 | 7,937 |
| 1280×720 | 1,785 |
| 640×360 | 16 |
| 960×720 | 15 |
| 480×360 | 10 |
| 1000×667 | 4 |
| 800×450 | 4 |
| 852×480 | 3 |
| 960×540 | 3 |
| 615×409 | 3 |

### By split

| Split | Min. W×H | Max. W×H | Median W×H |
|---|---|---|---|
| train | 240×160 | 5616×3744 | 1920×1080 |
| val | 320×206 | 4288×2848 | 1920×1080 |
| test | 640×360 | 1920×1080 | 1920×1080 |

**Top 3 resolutions for train:** 1920×1080 (4,393), 1280×720 (634), 640×360 (7).
**Top 3 resolutions for val:** 1920×1080 (2,196), 1280×720 (315), 480×360 (4).
**Top 3 resolutions for test:** 1920×1080 (1,348), 1280×720 (836), 960×720 (8).

I found no divergences between the size declared in the XML (`<size><width>/<height>`) and the actual image file size in any of the 10,000 files.

## 10. Signs of video-derived structure

- All file names in all three splits are end-to-end numeric numbering with leading zeros and the `.jpg` extension: from `00001.jpg` to `05200.jpg` (train), from `00001.jpg` to `02600.jpg` (val), from `00001.jpg` to `02200.jpg` (test). The numbering in each split is continuous, without gaps, starting from `00001`.
- I found no fields indicating the source video or the frame number in a sequence (for example, video_id, frame_id, timestamp) in the `.xml` annotations. The `<filename>` field matches the image file name, the `<path>` field contains the relative path `./<split>/<number>.jpg`.
- The 1920×1080 and 1280×720 resolutions dominate — standard Full HD and HD video formats. These two resolutions cover 97.2% of the delivery. The remaining 2.8% of images have non-standard, "photographic" resolutions (for example, 550×412, 1000×667, 479×261).

File name examples:

- `train/img/00001.jpg`, `train/img/00002.jpg`, ..., `train/img/05200.jpg`
- `val/img/00001.jpg`, `val/img/00002.jpg`, ..., `val/img/02600.jpg`
- `test/img/00001.jpg`, `test/img/00002.jpg`, ..., `test/img/02200.jpg`

There is no explicit group-id or sequence separator in the file names: the numbering is end-to-end within a split, without indicating which source sequence or video a specific frame belongs to.

## 11. Side observations while parsing the annotations (fact, without interpretation)

I automatically matched the box coordinates (`xmin`, `ymin`, `xmax`, `ymax`) against the image size declared in the same file (`<size><width>/<height>`) and found cases of coordinates going beyond the declared size or of zero or negative box area:

| Split | Number of objects with out-of-bounds coordinates / zero area |
|---|---|
| train | 16 |
| val | 8 |
| test | 9 |
| **Total** | **33** of 10,109 objects |

File examples: `train/xml/00155.xml`, `train/xml/00470.xml`, `val/xml/00991.xml` (zero or negative area), `test/xml/00078.xml`.

I found no XML parsing errors (invalid syntax) in any of the 10,000 annotation files.
