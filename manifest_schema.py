"""Manifest contract for cv-dataset-pipeline.

The manifest is the central inventory/registry of the dataset project. One row
== one sample (an image or a single video frame). It is the single source of
truth for provenance, deduplication, split control (data-leakage protection)
and annotation status. It is built *alongside* FiftyOne (it does not replace
it) and persisted as ``manifest.parquet``.

This module is the CONTRACT, written first. The builder
(``build_manifest.py``) must produce rows that validate against
:class:`ManifestRow` here — it does not "collect whatever columns come out".
Every row is validated through this model before it is allowed into the
manifest.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class AnnotationFormat(str, Enum):
    """Format of the annotation that arrived with the sample."""

    COCO = "coco"
    YOLO = "yolo"
    NONE = "none"


class AnnotationStatus(str, Enum):
    """Where the sample sits on the annotation pipeline."""

    PRE_LABELED = "pre-labeled"  # came already labeled from the source
    TO_ANNOTATE = "to-annotate"  # raw, awaiting annotation
    ANNOTATED = "annotated"      # labeled by us
    GOLD = "gold"               # reference set for QA / inter-annotator agreement


class Split(str, Enum):
    """Train / validation / test assignment. Guards against leakage."""

    TRAIN = "train"
    VAL = "val"
    TEST = "test"


class DedupStatus(str, Enum):
    """Outcome of deduplication review for a row."""

    ACTIVE = "active"
    DUPLICATE = "duplicate"


class IlluminationClass(str, Enum):
    """Capture-lighting category, derived from Phase 3a's brightness
    statistics and calibrated per-source by visual review (Phase 3b).

    ``LOW_LIGHT`` is a declared, deliberately-possibly-empty category: it
    marks genuine low light with no artificial illumination. Phase 3b's
    visual review of the darkest tail of both sources found no such
    frames — everything dark in this dataset is lit by streetlights. The
    value stays in the enum so that absence is a documented, checked
    finding rather than an omitted one."""

    DAY = "day"
    ARTIFICIAL_LIGHT = "artificial_light"
    LOW_LIGHT = "low_light"


class ManifestRow(BaseModel):
    """One sample in the manifest. Validated on construction."""

    sample_id: str
    """Primary key: SHA-256 hex digest of the file bytes. Stable across
    file moves/renames, unique per distinct byte content."""

    source: str
    """Origin tag of the sample (e.g. ``visdrone``, ``roboflow-uav``,
    ``own-video-01``). Enables filtering and provenance by vendor."""

    filepath: str
    """Path to the file on disk linking the manifest row to the physical
    object."""

    split: Split
    """train / val / test assignment, controlling the split and preventing one
    sample from leaking into more than one split."""

    format: str
    """Image file format (``jpg`` / ``png`` ...). Normalized to lowercase
    without a leading dot."""

    annotation_format: AnnotationFormat
    """Format the incoming annotation was in (coco / yolo / none)."""

    width: int
    """Image width in pixels (> 0). Used for resolution checks and bbox
    normalization."""

    height: int
    """Image height in pixels (> 0). Paired with width."""

    annotation_status: AnnotationStatus
    """Readiness of the annotation (pre-labeled / to-annotate / annotated /
    gold)."""

    condition_tags: Optional[str] = None
    """Shooting-condition tags (day/night, altitude, object density ...).
    May be empty/None on the first ingestion pass."""

    phash: str
    """Perceptual hash (hex) for detecting visually similar but not
    byte-identical frames (adjacent video frames, recompressed copies).
    Separate from ``sample_id``."""

    ingested_at: datetime
    """Timestamp the sample was added to the manifest."""

    dedup_status: Optional[DedupStatus] = DedupStatus.ACTIVE
    """Deduplication outcome: ``active`` (kept) or ``duplicate`` (superseded
    by another row). Defaults to ``active`` for rows no dedup step has
    touched yet."""

    duplicate_of: Optional[str] = None
    """``sample_id`` of the canonical row this one duplicates. ``None`` when
    ``dedup_status`` is ``active``."""

    dedup_method: Optional[str] = None
    """How the duplicate was identified, e.g. ``exact_sha256`` (Step A.1,
    identical file bytes) or ``phash_exact`` (Step A.2, identical perceptual
    hash). Generic string so later dedup steps can add methods without a
    schema change."""

    dedup_decided_at: Optional[datetime] = None
    """Timestamp the dedup decision (canonical vs. duplicate) was made."""

    sequence_id: Optional[str] = None
    """Video/sequence identifier recovered from ``filepath`` (e.g. the VisDrone
    video number, or the Roboflow ``videoN`` token). ``None`` when no reliable
    sequence pattern could be extracted for the row's source — such rows are
    single images with no known sequence membership, not an extraction
    failure to paper over."""

    split_before_resplit: Optional[Split] = None
    """Snapshot of ``split`` immediately before a sequence-level resplit
    changed it. ``None`` if the row's split was never reassigned."""

    split_reassigned: Optional[bool] = None
    """Whether a resplit step moved this row to a different split than its
    source dataset originally assigned. ``None``/``False`` if untouched."""

    resplit_reason: Optional[str] = None
    """Why the split changed, e.g. ``sequence_majority_vote``. ``None`` if
    ``split_reassigned`` is not true."""

    dedup_hamming_distance: Optional[int] = None
    """Hamming distance from this row's ``phash`` to its ``duplicate_of``
    canonical's ``phash``. Populated by Hamming-threshold dedup methods
    (e.g. ``phash_hamming_sequence``, ``phash_hamming_pairwise``). ``None``
    for active/canonical rows and for Step A exact-match rows (their
    distance is implicitly 0, but those rows are not retroactively
    rewritten)."""

    brightness_median_v: Optional[float] = None
    """Median of the HSV V (value) channel over the full image, 0-255 scale.
    Robust to a handful of blown-out highlights (e.g. streetlights) that
    would skew a mean. Populated by Phase 3a's illumination profiling pass;
    ``None`` for rows not yet profiled. Raw statistic only — no day/night
    classification is implied or derived from it at this stage."""

    brightness_p5_v: Optional[float] = None
    """5th percentile of the same HSV V channel, 0-255 scale. Median alone
    cannot separate an artificially-lit night scene (bright streetlights,
    dark background) from a genuine day scene with similar median
    brightness; the low percentile captures how dark the bulk of the frame
    actually is. Populated alongside ``brightness_median_v``; ``None`` for
    unprofiled rows."""

    illumination_class: Optional[IlluminationClass] = None
    """Day / artificial-light / low-light category, assigned per-source by
    Phase 3b from ``brightness_median_v`` (visually calibrated thresholds,
    not a single dataset-wide cutoff — VisDrone's bimodal brightness
    distribution is not comparable to Roboflow UAV's uniformly
    well-lit footage). ``None`` for rows not yet classified (all non-active
    rows, plus any active row predating this pass)."""

    @field_validator("sample_id")
    @classmethod
    def _sample_id_is_sha256(cls, v: str) -> str:
        if len(v) != 64:
            raise ValueError(
                f"sample_id must be a 64-char SHA-256 hex digest, got {len(v)} chars"
            )
        return v

    @field_validator("format")
    @classmethod
    def _normalize_format(cls, v: str) -> str:
        return v.strip().lstrip(".").lower()

    @field_validator("width", "height")
    @classmethod
    def _positive_dimension(cls, v: int) -> int:
        if v <= 0:
            raise ValueError(f"dimension must be > 0, got {v}")
        return v


# Stable column order for deterministic parquet output. The builder reindexes
# the DataFrame to exactly this order before writing.
MANIFEST_COLUMNS: list[str] = [
    "sample_id",
    "source",
    "filepath",
    "split",
    "format",
    "annotation_format",
    "width",
    "height",
    "annotation_status",
    "condition_tags",
    "phash",
    "ingested_at",
    "dedup_status",
    "duplicate_of",
    "dedup_method",
    "dedup_decided_at",
    "sequence_id",
    "split_before_resplit",
    "split_reassigned",
    "resplit_reason",
    "dedup_hamming_distance",
    "brightness_median_v",
    "brightness_p5_v",
    "illumination_class",
]
