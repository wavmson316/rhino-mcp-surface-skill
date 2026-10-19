# From an object to buildable patches: construction playbooks

Read this before modeling a complex object, together with [input interpretation](01-intent-and-reference.md) and [layout principles](02-patch-layout.md). Mouse/speaker examples are adaptable templates, not geometry to copy without inspecting the actual reference.

## 0. Five required planning outputs

1. A geometric shape statement, such as “a double-curved crown, lower at the front, with a deep left recess and approximately planar bottom,” rather than merely “a streamlined mouse.”
2. Constraints: extents, crown/belly locations, silhouette, negative spaces, symmetry, parts/motion; label dimensions, observations, and assumptions separately.
3. Curve graph: IDs, source views/section planes, endpoints, roles, and editable constraints. Cross-check reliable views.
4. Patch/adjacency table: actual side curves, UV, construction inputs, neighboring continuity, movement width, corners, and singularity risks.
5. Build order and stopping conditions: fixed parents, dependent details, comparisons, and recovery levels.

Trial surfaces can revise the plan. “Choose a method from geometry” alone is not a build plan. Without annotation tools, describe positions and IDs; never claim a diagram was drawn.

```text
P01 top parent
Extent: between front/rear assembly planes, slightly beyond final side trims
U front→rear, V left→right
Boundaries T_F/T_B/T_L/T_R, separately identified natural/trimmed status
Inputs Q00…Q04 transverse sections, ordered front→rear for trial Loft
Locks: confirmed crown, silhouette and maximum-width locations
Neighbors: side bands target G2 only if reflection requires it; an assembly gap
does not require continuity across separate parts
Exit: fixed-camera silhouette/landmarks, sections, validity and interior fairness
Recovery: revise section placement/shape/parameterization before adding points
```

## 1. Executable case: 120×70 crowned product enclosure, actual height40

### Contract

Dimensions use current document units; tested in millimeters. Length120, width70, shoulder z=10, crown z=40, bottom z=0. Shoulder/base edges are intentionally G0. Outputs: one crowned top, four walls, one bottom, and one valid joined solid.

This tests a complete parameter→control-net→derived-edge→wall→bottom→Join→inspection chain at the parent/blockout stage. It is not photo reconstruction, a thin-walled molded part, a finished mouse, or a G2 transition.

### Patches and source curves

| Patch | Domain/boundaries | Construction | Continuity |
|---|---|---|---|
| P01 | Rectangular top, all four edges at z10 | U along length, V width; degree3×4, CP4×5, single-span each | Intended G0 perimeter |
| P02–P05 | Each actual top edge to its XY projection | Direction-aligned ruled surface | G0 to top/bottom/neighbor |
| P06 | One closed loop from four projected edges | Planar face | G0 to walls |

Derive wall top edges from P01 instead of redrawing approximate copies. Script wall numbering follows actual edge enumeration, not permanent left/right semantics; map directions geometrically in production.

### How the control net defines volume

Four U columns have x=0,40,80,120. Five V columns span y=−35…35. Set longitudinal coefficients a=[0,1,1,0] and transverse b=[0,1,1,1,0]:

```text
CP[i,j].z = 10 + A*a[i]*b[j]
A = (40-10)/(0.75*0.875)
```

The Bernstein factors peak at0.75 and0.875 at their midpoints, so the actual surface center is(60,0,40) and boundary z=10. Control points can exceed40: the control hull is not the actual surface height.

### Construction and checks

| Step | Operation/API | Exit | First diagnosis |
|---|---|---|---|
| 1 | Nonrational NurbsSurface, orders4×5, CP4×5, clamped single spans | Degree3×4, spans1×1, valid | Degree/order, indexing, knots |
| 2 | Set grid, convert to Brep | Center z40, boundaries z10 | Control hull confused with surface, UV |
| 3 | Duplicate each edge; PlanarProjection copy to XY | Corresponding aligned upper/lower curves | Wrong curve or plane |
| 4 | CreateRuledSurface for each pair | Four valid walls sharing top positions | Direction/disconnection |
| 5 | JoinCurves lower loop; CreatePlanarBreps | One planar bottom | Open/nonplanar/multiple loops |
| 6 | JoinBreps six faces | One valid solid, no naked/nonmanifold edges | Real gaps, duplicates, tolerance |
| 7 | Outward orientation; VolumeMassProperties | Positive volume, six faces | Orientation/intersection |

### Run it

Inside Rhino Python3, with skill_root set to the installed skill directory:

```python
import sys
sys.path.insert(0, str(skill_root / 'scripts'))
from example_closed_shell import build_shell, run_example_tests
result = build_shell(__rhino_doc__, length=120, width=70,
                     height=40, shoulder_height=10)
print(run_example_tests(__rhino_doc__))
# result['patches']: six editable parents; result['solid']: joined body.
# In-memory only: no user document edits.
```

Only when the task asks to place it in the document, add one representation in a controlled edit rather than displaying coincident parents and solid together:

```python
doc = __rhino_doc__
record = doc.BeginUndoRecord('Add example parent enclosure')
try:
    object_id = doc.Objects.AddBrep(result['solid'])
    print(str(object_id))
finally:
    doc.EndUndoRecord(record)
    doc.Views.Redraw()
```

For per-face editing, add named parents on separate layers and hide overlapping final geometry. Never delete unrelated originals. Tests12/12 are recorded in example-test-results.json.

### Transfer to a real housing

Off-center crown: revise longitudinal sections/coefficients. Waist variation: change widths by station and remeasure actual maximum width, not just CP width. G2 shoulders: redesign for transition bands, not relabel joined hard walls. Thickness: perform actual offset/closure checks. Openings: derive trims from accepted parents. Recheck dimensions and neighboring seams after every change.

## 2. Mouse-like shell: deriving layout from references

### Make five shape decisions

Determine front/rear, crown position along length, maximum-width position, left/right asymmetry, and whether a real thumb recess exists. A dark region in one perspective view is insufficient. Normalize L=1 when unknown, with W/L and H/L as reference-based assumptions.

Compare a multi-span sculpted parent for shallow, rounded forms against independent top/side/recess surfaces with wide bands for deep recesses and stable glossy tops. The following develops the latter.

### Curve scaffold

| Curve | Source/definition | Purpose |
|---|---|---|
| C00 | Bottom datum and front/rear planes | Scale/contact/assembly extent |
| C01 | Top arch from side view, checked in other views | Crown and taper |
| C02/C03 | Left/right plan silhouette with 3D height | Width variation, not shadow tracing |
| Q00…Q04 | Transverse sections at distinct x | Crown flatness/roundness, shoulders, belly |
| C04 | Section through deepest thumb point | Recess depth/width |
| C05/C06 | Front/rear fading sections | Avoid pinched recess ends |

Trial stations x/L=0,0.2,0.45,0.72,1 are starting positions, moved to actual shape changes. Five CP/degree4 sections are candidates, not standards. For transverse z coefficients [shoulder,shoulder+q,shoulder+q,shoulder+q,shoulder], center rise is0.875q; the middle CP is not actual crown height.

### Patch allocation

| ID | Role | Main boundaries | Candidate |
|---|---|---|---|
| P01 | Glossy top parent | T_F/T_B/T_L/T_R | Ordered Loft Q sections or boundary/section Network |
| P02 | Right side | Shoulder/bottom/front/rear | Loft/two-rail; do not drag top down |
| P03 | Left front side | Front shoulder/bottom/front/recess-front | Simple side parent |
| P04 | Thumb-recess base | Front/rear fades, upper/lower recess edges | C04 primary, C05/C06 decay |
| P05 | Left rear side | Rear shoulder/bottom/recess-rear/rear | Coordinate tail volume |
| P06R | Top-to-right band | P01 right, P02 shoulder, end sections | BlendSrf or constrained Sweep2 |
| P06La/b/c | Top-to-left front/recess/rear bands | Corresponding top edge subranges and P03/04/05 | Separate bridges with inter-band checks |
| P07/P08 | Front/rear closure or assembly opening | Confirmed surrounding boundaries | Construct or intentionally leave open |

Regions may require multiple four-sided faces. If the recess-to-front/rear side connections need longitudinal soft bands, reserve and name them separately; do not force incompatible boundaries together with Match.

### Build sequence

1. Match camera/blockout: extents, crown, negative spaces. SaveV00.
2. Build C01–C03 and Q sections, cross-check at least two reliable views and intended comb trends.
3. Build only P01, inspect primary sections and fixed-camera silhouette. Revise stations/shape/correspondence before buttons.
4. Build P02/P03/P05 side volumes with transition room. Do not collapse the confirmed top crown to make contact. SaveV01.
5. Construct P04 from the deepest section, then fade toward its ends. Unknown depth remains an editable assumption.
6. Design P06 widths and cross-band sections. Trial Blend; inspect correspondence/width/bulge. Extract good sections and rebuild with Sweep2 when necessary. Real face edges are required for transverse continuity semantics.
7. For each E seam inspect position, tangent plane, then required curvature. Recheck old/inter-band seams after edits. Enlarge incompatible corners.
8. Resolve P07/P08 and bottom assembly trims. Mirror only confirmed symmetric regions. SaveV02.
9. Derive button seams, wheel openings, material regions, and lower shell from accepted shape. Black color does not substitute for inner walls or negative space.
10. Add engineering thickness, clips, bosses, draft, motion, and clearance only as required, with independent checks. Save delivery version.

Exit: three-to-five user-critical features have corresponding dimensional/section/projection evidence; parents/layout remain editable; unmeasured G2 is not a pass. High overall IoU must not hide incorrect recess depth or a wrong wheel opening.

## 3. Rotational speaker or bottle

1. Verify real axial symmetry from multiple views; flat backs, handles, and noncircular sections can invalidate Revolve.
2. Define axisA, heightZ0/Z1, profileR(z), maximum radius and its location, top/bottom taper and mouth separately.
3. Revolve a fair profile for P01. Use analytic segments where appropriate and place the seam away from sensitive views. Inspect pole/tangent behavior; do not trace every pixel.
4. Define P02 lid and P03 base as assembly parts, deriving shared shapes from the same profile/parent instead of redrawing inconsistent circles.
5. Treat grille color as material first. If real perforations exist, define size/spacing/margins, validate one unit, then repeat and recheck actual curved-surface spacing.
6. Wrong silhouette returns to R(z), not cosmetic blends. Nonrotational regions need their own parents/transitions.

Acceptance: axis, total height, maximum diameter/location, top/bottom silhouette, interfaces, reflection, and seam placement. Do not invent unseen wall thickness for a surface-only deliverable.

## 4. Three-way tube/handle junction

1. Define three axes/sections, angles, envelope, center width, and required passages/connection datums.
2. Build P01/P02/P03 branch parents beyond the center. Check overall proportions before removing intersecting center regions.
3. Design cross-sections for P04/P05/P06 bridge bands. Three smooth bridges do not finish the central topology.
4. Draw/describe central adjacency and tangent conditions; compare multiple four-sided patches against a wider network reconstruction. Move incompatible convergence away from critical reflections.
5. Patch may initialize volume, followed by edge/section validation and wider-band reconstruction. It is never automatic G2.
6. Check branch end sections, central bulge, star reflections, and corner compatibility; engineering adds minimum wall/passage and self-intersection checks.

Recovery: pinched center→larger region or revised bridge-end sections; conflicting bands→adjacency/tangents; drifting branches→lock analytic masters and enlarge the allowed transition rather than densifying the entire model.

## 5. Task-specific intent gates

| Stage | Evidence | If it fails |
|---|---|---|
| Blockout | Fixed-camera silhouette, proportions, crown, negative space | Revisit camera/depth/blockout, delay detail |
| Parents | Sections, curvature trends, editability | Revise sections/layout before openings |
| Transitions | Seam samples, reflections, corners, G2 status | Widen/relayout or state limits |
| Details | Critical-feature position/size/count checklist | Correct locally and recheck parents |
| Engineering | Contract-specific thickness/interference/draft/exchange | Appearance acceptance is insufficient |

Actually inspect fixed-camera outputs when images are available and allowed. If not, clearly state numerical-only checks. A detailed skill cannot guarantee every agent/reference succeeds. Real task benchmarks require the reference, targets, final model, and per-feature scoring; this procedural enclosure validates only its construction chain.
