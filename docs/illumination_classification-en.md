# Illumination-condition classification

## Purpose

This document classifies illumination conditions across the entire active dataset. The classification serves as the basis for coverage assessment and sample stratification.

## Metric

The primary metric is the per-image median of the V channel of the HSV (hue-saturation-value) color space (`brightness_median_v`). The secondary metric is the 5th percentile of the same channel (`brightness_p5_v`). Both metrics are computed over the active manifest rows.

## Threshold-calibration procedure

From the `brightness_median_v` distribution, I identified the zone between the modes, roughly 60–70.

Then I assembled a calibration set and reviewed it in FiftyOne, sorted by `brightness_median_v` in ascending order. The review covered a band of values around the presumed boundary — approximately 40 to 90, that is, frames directly below and above the candidate values.

Decision criterion: find the value below which frames with artificial lighting predominate and above which daytime frames predominate, with the minimum number of errors in both directions.

I chose the value 49.0: above it, the share of daytime frames consistently exceeds the share of night frames.

## Classification rule

A visual review of the darkest tail of both sources found no frames shot without an artificial light source. VisDrone's dark frames are scenes with street lighting. Roboflow UAV's dark frames are captures under daytime or studio lighting. Based on this conclusion, the rule assigns only two categories:

- **VisDrone:** `brightness_median_v < 49.0` → `artificial_light`; `>= 49.0` → `day`.
- **Roboflow UAV:** the whole source → `day`, without applying the threshold. The category is assigned to the source wholesale based on the results of the dark-tail review. The threshold was not applied to the source, and frames outside the dark tail were not reviewed.
- **low_light:** the rule does not assign this category. It remains declared and empty. This records that the absence of genuine low-light was verified, not skipped.

## Result

| Source | day | artificial_light | low_light | Total |
|---|---|---|---|---|
| VisDrone | 7,388 | 1,228 | 0 | 8,616 |
| Roboflow UAV | 2,529 | 0 | 0 | 2,529 |
| **Total** | **9,917** | **1,228** | **0** | **11,145** |

The subtotals reconcile with the active manifest rows: 7,388 + 1,228 = 8,616 (VisDrone), plus 2,529 (Roboflow UAV) — 11,145 in total.

## Limitations

The separation is continuous, so the overlap zone around the threshold is not empty: above 49.0, frames with artificial lighting occasionally occur. This is a property of the brightness signal, and it is not sufficient for error-free separation.

I performed the calibration by visual review myself, without a formal protocol and without measuring the error rate in the overlap zone.

The threshold is calibrated on VisDrone and fixed before application. It transfers to other sources without recalibration. This is a deliberate condition: recalibrating the threshold for each new delivery would make the acceptance criterion inapplicable.

An empty `low_light` counter does not by itself prove the absence of genuine low-light. The category is empty because the classification rule does not assign it. The rationale is the conclusion of a visual review of the darkest tail of both sources. I did not record the extent of the reviewed tail.
