# Candidate label admission protocol v2 — visible solid extent convention

Revision 2026-11-09: train-only QA20 found 3 selected/completed nodes for which v1 did not say whether to include the green outer rim. Preserve both original review files. No model training or frozen benchmark truth was used to choose this convention. This changes NEW training annotation policy only, not the formal IoU scorer or pixel proof.

Machine identifier: `visible_outer_solid_extent_v2`. Old `visible_outer_solid_edge_v1` labels are not silently promoted; they require re-review. The three ambiguous representative crops were independently rechecked against v2 and found visually resolvable; this is not certification of numerical boxes or all objects in those images.

This is an operational annotation specification, not completed labels. No frozen annotation is edited. Model proposals or old template detections may assist inspection but cannot be silently promoted to reviewed ground truth.

## Acquisition and split

Target 400 newly admitted raw images: 240 train / 80 validation / 80 independent-source test. Group by source video, game run and persistent map/layout before augmentation. Reappearing maps and near-duplicates stay in one split. Exclude every frozen positive/holdout/negative interaction, its transformations and adjacent samples from the same interaction. Timestamp separation alone is not proof of independence.

Conservative A0 inventory initially blocks all four previously exposed source videos until whole-run/layout provenance is documented. This is a temporary admission policy, not a claim that every unused pixel in those videos is permanently unusable. To admit an unused training/validation interval, record complete interaction boundaries, run/layout identity and near-duplicate comparisons against the entire frozen corpus. A genuinely new source remains necessary for the proposed independent test, rather than relabeling an exposed challenge set as blind.

Preferred acquisition: at least three independent runs/source groups across train/val/test, preferably an additional training source for diversity, with different map layouts and aspect ratios. Reuse eligible unused intervals only after the provenance audit. Keep original watermarks and file hashes. No new recording through game control is authorized; new public video links or user-provided recordings can be inventoried in a subsequent data step.

## Physical boundary and labels

- Classes: `map_node`, `entry_gate`; semantic action authority is not a training label.
- Complete node: tight axis-aligned box around the **outermost solid painted enclosing rim belonging to this node**, including an attached solid green selected/completed rim when present. This is the visible object extent, not an assumed state-invariant underlying blue-body extent. A green connecting path is a separate line and is excluded. Exclude diffuse bloom, detached pointer arrows, internal check marks, labels and connection lines. Do not infer the extent from an orange inner circle or copy a template canvas size.
- If the node's enclosing rim is partly hidden by text, a dialog, another object or source cropping, label it partial; do not project the rim from a prior frame or reconstruct an amodal whole hexagon. If the painted-rim versus bloom transition itself cannot be resolved visually, retain unresolved QA rather than deriving a constant shrink factor.
- Partial/cropped/covered node: annotate visible support and `visibility=partial`; do not invent an amodal rectangle. Record which exterior segments/corners are not observable. A partial box is never counted as complete outer-boundary proof.
- Visually ambiguous frame layers: retain a separate unresolved QA record. Do not average two incompatible physical boundary definitions or shrink a box until it matches frozen scoring truth.
- Hard negatives: portraits, treasure icons, emulator bars, buttons, watermarks and unrelated hexagonal decoration. A gray map node may still be a generic candidate; color does not grant clickability.
- Two independent review records must name reviewers/passes, image SHA, chosen boundary layer and disagreements. Disagreements require source-visible resolution before `reviewed=true`; duplicating one annotation twice does not count as independent review.
- Before training, audit image existence, actual PNG/RGB SHA, source dimensions, box bounds, visibility, group membership and annotation/review lineage. The current metadata validator alone does not perform that entire certification.

## Initial QA batch

Use 20 **new eligible** raw images spanning sources, widths/heights, partial visibility and difficult outer rings. Freeze this policy only after both reviews can identify the same physical edge. If not, candidate-recall research may remain meaningful, but outer-IoU improvement and the new boundary proof remain blocked. Do not use cases55–57 to select the annotation convention or tune a numerical correction.

Current QA artifacts: `artifacts/candidate-data-20261108-02/qa20/`. Twenty native-size train-reserved images from two new video IDs have raw PNG/RGB hashes and two separate qualitative reviews. These reviews are NOT exhaustive full-frame box annotations. Certified train=0, val=0, independent test=0 until all asset/lineage/layout/dedup and full label checks pass. A representative object's clear boundary does not certify every object in its full image.
