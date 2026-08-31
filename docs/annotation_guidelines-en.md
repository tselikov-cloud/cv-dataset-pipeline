# Annotation Guidelines

This document is for the annotator. It specifies which objects to annotate, how to build the box, and how to act in edge cases.

Abbreviations used in this document:

- **GT** (ground truth) — the source's original annotation, which the project annotation is checked against.
- **IoU** (intersection over union) — a metric for the overlap of two boxes.
- **UAV** (unmanned aerial vehicle).

---

## Class `vehicle` (VisDrone)

**Status:** complete. The gold set was annotated under this revision; the precedents section was filled in based on its results.

### 1. Scope

Apply these rules to `vehicle`-class objects in VisDrone-DET images. The annotation type is a bounding box aligned to the frame axes (axis-aligned).

### 2. Class composition

Annotate: cars, vans, trucks, passenger transport (buses). In terms of the original VisDrone annotation, these are `car`, `van`, `truck`, `bus`, merged into the `vehicle` superclass.

Don't annotate: motorcycles and mopeds, bicycles, tricycles (including canopied ones), animal-drawn transport, pedestrians, or objects whose type can't be determined.

The class merges subtypes for two reasons. Subtype discrimination is not part of the project's task. At the capture altitude, subtypes are often visually indistinguishable. Merging removes this source of ambiguity.

### 3. Distinguishability threshold

Annotate an object if you confidently assign it to one of the types in the class composition. Act by three cases:

- Type determined, subtype unclear — annotate as `vehicle`.
- Object recognized as transport outside the class composition (motorcycle, bicycle, tricycle) — don't annotate.
- Type can't be determined — don't annotate.

Don't apply a numeric minimum-size threshold. Such a threshold follows from the distinguishability rule and is not an independent criterion.

#### 3.1 The role of context

Recognize an object by the combination of its own features and the frame context: position on the roadway or a parking space, embedding in a row of similar objects, direction and character of movement, characteristic shadow.

Context works both ways:

- **Confirms recognition.** Annotate a small object with an ambiguous silhouette if the context gives reliable cues of membership in the target class: the object stands in a row of parked cars, moves in traffic along a lane, occupies a parking space.
- **Refutes recognition.** Don't annotate an object with a transport-like silhouette if the context makes its presence in that place unlikely: a position outside the roadway and parking zones, on a roof, in water, in a tree canopy.

Context confirms or refutes recognition but doesn't replace it. If an object is indistinguishable on its own and context only makes the presence of transport likely, don't annotate it.

### 4. Box geometry

Follow four rules:

- Fit the object into the box completely.
- Leave no visible gap between the box border and the object's outermost points.
- For an object positioned diagonally, expand the box to full coverage.
- Build the box aligned to the frame axes (axis-aligned).

**Compression artifacts.** Around objects, especially in VisDrone, a color halo is visible — a compression artifact. Include the halo in the box as part of the object's visible body. Don't include the cast shadow. To tell them apart: a shadow has direction and lies on the surface next to the object, whereas the halo surrounds the object itself.

**Nighttime glare.** In `artificial_light` frames, headlights and marker lights on create white or red glare circles that fully hide the body. `artificial_light` is the illumination category for scenes under artificial light; for the criterion and threshold, see [docs/illumination_classification.md](illumination_classification-en.md). Act by the state of the objects:

- If objects are separable, draw the box along the border of the glare circle. This is the object's visible boundary, because the body is hidden.
- If the circles merge and the objects are inseparable, apply the rule in section 6.

### 5. Occlusion

To choose the rule, determine: are there frame pixels behind the hidden part of the object.

- **Occlusion by another object.** The object lies within the frame, hidden by transport, terrain, a pole, or vegetation, but is recognized as `vehicle`. Complete the box to the full silhouette, including the hidden part. There is frame behind the hidden part, so completion is allowed.
- **Frame edge.** The object continues beyond the image border. Crop the box at the frame border. There are no pixels beyond the edge, so completion is impossible.
- **Combination.** The object is both occluded by another object and extends past the edge. Complete the part hidden by the object and crop the part hidden by the edge. Apply both rules to the respective parts of a single box.

### 6. Dense clusters and merged objects

The rule has three cases. Determine which one matches the frame.

- **Objects are individually distinguishable.** Annotate each object with an individual box, even under mutual overlap in a row or traffic flow and at a small size. Use context (rows, lanes, regularity of arrangement) as a basis for separation. Don't apply a group box to a cluster of distinguishable objects.
- **Objects form a monolithic entity.** If a boundary between objects can't be drawn — due to pixelation, optical distortion, uncertainty of scale and proportions — annotate the entity with **a single box**. Do this only on the condition that: you confidently recognize the entity as transport of the target class, or context gives reliable membership cues (a parking space, a row of parked transport, a traffic lane). Don't split such an entity into an assumed number of objects: the count within it is not recoverable and is not subject to guessing.
- **The entity is not recognized.** Apply the distinguishability-threshold rule (section 3) and don't annotate it.

### 7. What not to annotate

Don't annotate:

- reflections of objects;
- objects behind glass, in storefronts, on advertising images;
- objects outside the class composition (section 2).

### 8. Source `ignore_regions` zones

`ignore_regions` is a construct of the original VisDrone annotation: frame areas that the source authors marked as not subject to per-object annotation. How they're applied in the source and what role they play in metric computation is described in [reports/annotation_agreement.md](../reports/annotation_agreement-en.md), section 9.

Don't account for `ignore_regions` zones during annotation. Annotate all distinguishable objects by the rules of this guideline, regardless of where the source zones run.

These zones apply only at the metric-computation stage. Adjusting annotation to fit them would strip the gold set of its status as an independent check.

### 9. Resolving ambiguities

Resolve disputed cases by the existing guideline rules. Document each decision in the precedents section with a rationale.

If no rule covers a case, add a rule and re-annotate the already-processed material under the new version. Distinguish two types of change:

- Adding a precedent doesn't change a rule — re-annotating backward is not needed.
- Changing a category's definition requires re-annotating backward.

### 10. Precedents

Each precedent contains: a description of the case, the rule applied, the rationale for the decision.

**Nighttime glare from headlights and marker lights.** In night frames (`artificial_light`), distant transport with lights on is fully hidden by white or red glare circles. Rule applied: where objects are separable, draw the box along the border of the glare circle (section 4, "Nighttime glare"). Rationale: the body is physically not visible, so the object's visible boundary coincides with the glare boundary. When writing the rule, I anticipated a systematic stylistic divergence from GT on such frames that would not be an annotation error. The measurement did not confirm this assumption: the median IoU on `artificial_light` frames is practically indistinguishable from daytime — 0.849 versus 0.865 (see [reports/annotation_agreement.md](../reports/annotation_agreement-en.md)).

**Color compression halo.** Objects have a color "aura" — a compression artifact. Rule applied: include the halo in the box, exclude the shadow (section 4, "Compression artifacts").

---

## Class `Drone` (Roboflow UAV)

**Status:** complete. The gold set was annotated under this revision; the precedents section was filled in based on its results.

### 1. Scope

Apply these rules to `Drone`-class objects in Roboflow UAV dataset images. The annotation type is a bounding box aligned to the frame axes (axis-aligned).

The source differs structurally from VisDrone: a single target class, the drone is the main subject in most frames, and lighting is mostly good. The shots are taken mostly from the ground, but frames from altitude, over water, and shot from other drones do occur.

### 2. Class composition

Annotate: a rotary-wing or multirotor aircraft of any type and size — multicopters, fixed-wing-type craft, hybrid designs, consumer and professional models.

**Class boundaries.** Define the class by the visual feature of an aircraft, not by the absence of a pilot. The dataset contains piloted rotary-wing craft (for example, piloted-type hexacopters) visually indistinguishable from large drones. Annotate them as `Drone`. The class name `Drone` reflects this assumption: the target object is an aircraft of this class in the frame, regardless of whether a pilot is present. This is a deliberate broadening relative to the literal notion of an "unmanned" craft.

**Object state is irrelevant.** Annotate the craft in any state:

- in flight, on the ground, on a surface, in a person's hands, in transport position;
- in a compactly folded configuration (folding models);
- with missing elements (for example, without part of the rotors);
- deformed or destroyed (for example, after a crash).

The condition in all cases is the same: you confidently recognize the object as an aircraft of the target class.

Don't annotate images of a craft that are not its physical presence in the frame: on a monitor or phone screen, on an advertising poster, on printed material, in a reflection. Also don't annotate unrealistic images (drawings, pictograms, stylized graphics). Annotate only a realistic photographic capture of a physical object.

### 3. Distinguishability threshold

Annotate an object if you confidently recognize it as an aircraft of the target class. Act by three cases:

- Object recognized as an aircraft of the class, model and type unclear — annotate as `Drone`.
- Only a detail is visible in the frame (a propeller, part of the body) by which the object can't be recognized as a whole — don't annotate.
- It's impossible to determine whether it's a drone (a bird, a dot in the sky, an unrelated object) — don't annotate.

Don't apply a numeric minimum-size threshold: it follows from the distinguishability rule. The dataset contains frames with very small objects. The confident-recognition boundary was refined during the pilot review and, where needed, fixed in the precedents section.

### 4. Box geometry

Follow four rules:

- Fit the entire object into the box, including rotors, arms, landing gear, gimbal, and payload.
- Leave no visible gap between the box border and the object's outermost points.
- For an object positioned diagonally, expand the box to full coverage.
- Build the box aligned to the frame axes (axis-aligned).

Include rotors in the box: when static — along the edge of the blades; when spinning — along the visible edge of the blurred disk.

Always include the landing supports (gear, legs). The source annotation includes them inconsistently; this rule is a deliberate divergence from part of the GT toward stricter geometry.

### 5. Occlusion

To choose the rule, determine: are there frame pixels behind the hidden part of the object.

- **Occlusion by another object.** The craft lies within the frame, partly hidden by the operator's hand, vegetation, or a structure, but is recognized as `Drone`. Complete the box to the full silhouette, including the hidden part.
- **Frame edge.** The object continues beyond the image border. Crop the box at the frame border. There are no pixels beyond the edge, so completion is impossible.
- **Combination.** The object is both occluded by another object and extends past the edge. Complete the part hidden by the object and crop the part hidden by the edge. Apply both rules to the respective parts of a single box.

### 6. Multiple objects in the frame

Annotate each drone with an individual box, including cases of mutual overlap. Don't apply a group box.

### 7. What not to annotate

Don't annotate:

- images of a craft on screens, posters, printed material;
- unrealistic images: drawings, pictograms, stylized graphics;
- reflections;
- objects not recognized as an aircraft of the class (section 3).

### 8. Resolving ambiguities

Resolve disputed cases by the existing guideline rules. Document each decision in the precedents section with a rationale.

If no rule covers a case, add a rule and re-annotate the already-processed material under the new version. Distinguish two types of change:

- Adding a precedent doesn't change a rule — re-annotating backward is not needed.
- Changing a category's definition requires re-annotating backward.

### 9. Precedents

Each precedent contains: a description of the case, the rule applied, the rationale for the decision.

**Piloted hexacopter.** In the gold set, piloted rotary-wing craft occurred, visually indistinguishable from large drones. Decision: annotated as `Drone` (section 2, "Class boundaries"). Rationale: the class is defined by the visual feature of an aircraft, not by the absence of a pilot.

**Deformed or destroyed craft.** In the gold set, a drone occurred after a crash, deformed. Decision: annotated (section 2, "Object state is irrelevant"). Rationale: the object is recognized as a craft of the target class; state does not affect the decision.

**Folded configuration and missing elements.** Craft occurred in a compactly folded form and with missing parts (in particular, without part of the rotors). Decision: annotated (section 2). Rationale: the same — recognizability outweighs completeness and standard configuration.

**Unrealistic image of a drone.** A frame with an image of a drone as a pictogram or non-photographic graphic (`gold_0173.jpg`) got into the gold set. Decision: not annotated, the frame was excluded from the gold set (section 7). Rationale: only a realistic photographic capture of a physical object is annotated.
