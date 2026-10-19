# From an object to buildable patches: detailed construction playbook

This document is the construction layer covering how a reference becomes a model. Read it before modeling any complex object; use it together with [input analysis](01-intent-and-reference.md) and [patch layout principles](02-patch-layout.md). The mouse and speaker cases below are **adjustable templates**; they must not be copied as-is without inspecting the client's reference.

## 0. Five things the agent must produce before surfacing

1. **Shape statement**: describe the object in geometric terms, for example "a double-curved top cover that is low at the front and high at the back, with a deep recessed grip area on the left and an approximately planar bottom edge," rather than only saying "a streamlined mouse."
2. **Constraint table**: overall length, width, and height; maximum volume / high-point locations; primary silhouettes and negative spaces; symmetric or asymmetric; parts and their motion relationships. Label each item as a measured dimension, a reference observation, or an assumption.
3. **Curve graph**: the ID of each curve, its source view or section plane, its start and end points, its role, and who may modify it. Cross-check 3D silhouettes against several reliable views first.
4. **Patch and adjacency table**: which edges or sections supply the four sides of each patch; U/V, surfacing inputs, adjacent G-levels, and the movable range. Identify corner fills and singularities early; do not wait until the end and then Patch arbitrarily.
5. **Construction order and stopping conditions**: which parent surfaces are fixed first and which details are derived later; how each stage is compared against the reference, and which level to fall back to when it fails.

Trial surfaces may be revised during planning, but "choose a command from the geometry" is not by itself a complete construction plan. Without drawing tools, use textual orientation, curve IDs, and the adjacency table; never claim that a diagram has been drawn.

### Recording format: an example, not mandatory values

```text
P01 top parent
Extent: visible top region between the front/rear assembly planes, extending slightly beyond the final side trims on both left and right
U: front→rear; V: left→right
Edges: T_F, T_B, T_L, T_R; note separately which are natural edges and which are later trimmed edges
Inputs: five cross sections Q00…Q04; trial Loft in front→rear order
Constraints: back arch height, high point in side view, maximum-width position in top view; do not move an already confirmed primary silhouette for Match
Seams: the left/right transition bands target G2 only if reflection requires it; if the front is a part separation, do not force continuity across it
Exit: fixed-camera silhouette/key points and primary sections pass; validity passes; no unintended interior waviness
Fallback: change sections/parameter distribution first, subdivide the region only if that still fails, and never simply add points to the whole surface
```

## 1. Complete executable example: a 120×70 double-curved product shell parent form with an actual maximum height of 40

### 1.1 Task and boundaries

Input units follow the current document units; testing was done in a millimetre document. The design is 120 long, 70 wide, with shoulder height 10, apex height 40, and bottom face z=0. **Intentional G0 hard edges** are kept all around. The output is one double-curved cover, four walls, a bottom face, and the valid closed body after joining.

This validates the complete parent-form chain of "explicit parameters → control net → derived edges → side walls → bottom face → Join → inspection." It is **not** a real photo reconstruction, a thin-walled injection-moulded part, a finished mouse, or a G2 transition example; a pass here must not be used to claim any of those tasks were completed.

### 1.2 Patch layout and curve sources

| Patch | Extent and boundaries | UV and method | Continuity |
|---|---|---|---|
| P01 | One rectangular top cover, all four edges at z=10 | U along the length, V across the width; Degree 3×4, 4×5 CP, single-span in both directions | Hard transitions all round, target G0 |
| P02–P05 | From each natural edge of P01 to the corresponding projected edge at z=0 | Ruled surfaces with matching upper/lower edge directions | G0 to the cover, bottom, and neighbouring walls |
| P06 | A closed planar loop formed by the four projected edges at z=0 | Construction equivalent to PlanarSrf | G0 to the four walls |

The top edges of the side walls are **extracted directly from P01's edges**; do not redraw a set of lines that merely "looks the same." The script numbers P02–P05 by actual edge order; do not assume a given edge index is permanently left/right — a production project must re-map them by geometric orientation.

### 1.3 How the top-cover control net determines the volume

U has 4 columns, with x equally divided at 0, 40, 80, 120; V has 5 columns, with y equally divided from −35 to 35. Set the longitudinal shape coefficient `a=[0,1,1,0]` and the transverse coefficient `b=[0,1,1,1,0]`:

```text
CP[i,j].z = 10 + A * a[i] * b[j]
A = (40 - 10) / (0.75 * 0.875)
```

The two Bernstein polynomials peak at 0.75 and 0.875 respectively at their midpoints, so **the actual surface centre** is (60,0,40) and the surrounding edges are z=10. Control point heights may exceed 40; that is the normal control envelope, and the highest CP cannot be taken as the actual surface height.

### 1.4 Operating steps and checks

| Step | Operation / real API | Exit condition for this step | Check this first on failure |
|---|---|---|---|
| 1 | Create a non-rational NurbsSurface, order 4×5, CP 4×5, with a clamped single-span knot vector | Degree 3×4, Span 1×1, valid surface | degree/order, point array indexing, knots |
| 2 | Set the x/y/z point grid, convert to Brep | Centre z=40, edges z=10 | Mistaking control point values for actual values, UV direction |
| 3 | DuplicateCurve each edge, PlanarProjection the copy to XY | Each upper/lower pair corresponds and runs in the same direction | Wrong isocurve selected, projection plane |
| 4 | CreateRuledSurface for each pair → Brep | Four valid side walls sharing positions with the top cover | Edge direction or disconnection |
| 5 | JoinCurves the lower edges to close the loop, then CreatePlanarBreps | One valid bottom face | Loop not closed, not coplanar, multiple loops |
| 6 | JoinBreps the six faces | One valid Solid with no naked edges and no non-manifold edges | Actual gaps, duplicate faces, tolerance |
| 7 | Correct the solid to face outward, check with VolumeMassProperties | Positive volume, six faces, outward orientation | Flipped faces or self-intersection; do not rely on loosening tolerance |

### 1.5 Directly runnable

In Rhino Python 3, with `skill_root` set to this skill's installation directory:

```python
import sys
sys.path.insert(0, str(skill_root / 'scripts'))
from example_closed_shell import build_shell, run_example_tests
result = build_shell(__rhino_doc__, length=120, width=70,
                     height=40, shoulder_height=10)
checks = run_example_tests(__rhino_doc__)
print(checks)
# result['patches'] keeps the 6 editable parent surfaces; result['solid'] is the joined body.
# In-memory construction by default; no user document objects are added or removed.
```

Only when the task requires placing the example in the document, add one representation in a controlled edit so that coincident parent surfaces and the Solid are not both displayed:

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

When per-face editing must be preserved, add named parent surfaces to separate layers, hide the recombined result, and never automatically delete the user's originals. The 12/12 test results are in `example-test-results.json`.

### 1.6 Transferring from the example to a real housing

The client's side-view high point is off-centre → modify the longitudinal sections or the control net coefficients. A waist in top view → change the width of each column, but re-measure the actual maximum width; you cannot keep claiming it equals the input CP width. G2 side edges needed → first revise the layout to reserve transition bands; calling four walls joined by Join "G2" is invalid. Constant thickness needed → perform separate offset/edge-closure and self-intersection checks. Openings needed → derive the trim from an already-passed parent surface. After every change, re-check the dimensions and the related adjacent edges.

## 2. Mouse-style shell: from reference to patch layout

### 2.1 Make five decisions first

Confirm the front/rear direction, where along the length the top high point sits, the position of the maximum width in top view, whether left and right are symmetric, and whether a thumb recess genuinely exists. A dark region in a single oblique view cannot be treated directly as a recess. With no dimensions, start with L=1 and take W/L and H/L as reference-based assumptions; with dimensions, use the measured values.

Compare two layouts first: a shallow recess with an overall rounded form can be sculpted with a single multi-span parent surface; a deep side recess with a stable top highlight requires an independent top face + side faces + wide transitions. This section develops the latter.

### 2.2 The curve scaffold must actually be defined

| Curve | Content / source | Purpose |
|---|---|---|
| C00 | Bottom datum plane and the front/rear cutting planes | Scale, ground contact, and assembly extent |
| C01 | Top arch line in side view, cross-checked against perspective/top view | Determines the high point and the front/rear taper |
| C02/C03 | Primary left/right silhouettes in top view, with 3D height corrected | Width variation; do not trace shading directly |
| Q00…Q04 | Cross sections at different x positions | Control the flattened top roundness, shoulder-line position, and belly |
| C04 | The section passing through the deepest point of the thumb recess | Controls the true recess depth and transition width |
| C05/C06 | Cross sections where the recess fades out front and rear | Prevents the recess ends from being pinched into sharp points |

Initial cross-section stations may be tried at x/L=0, 0.2, 0.45, 0.72, 1; these are trial positions, and at key changes they should be moved according to the reference. Five CP / Degree 4 per cross section is a candidate, not a fixed standard. If the transverse z coefficients `[shoulder height, shoulder height+q, shoulder height+q, shoulder height+q, shoulder height]` control the centre height, the centre difference is 0.875q; the middle CP cannot be taken directly as the actual arch height.

### 2.3 Patch plan

| ID | Responsibility | Four sides / primary boundaries | Construction candidate |
|---|---|---|---|
| P01 | Primary glossy top parent surface | T_F/T_B front/rear, T_L/T_R left/right | Ordered Loft over Q00…Q04, or a four-edge plus inner-section Network |
| P02 | Right side primary surface | Right shoulder edge / bottom edge / front and rear trim edges | Loft / two-rail; do not drag P01 straight down to the bottom |
| P03 | Left front side primary surface | Front left shoulder / bottom edge / front trim edge / recess front edge | Low-complexity side surface |
| P04 | Thumb recess base | Front and rear fades, upper and lower recess edges | C04 as primary, C05/C06 controlling the decay |
| P05 | Left rear side primary surface | Rear left shoulder / bottom edge / recess rear edge / rear trim edge | Coordinated with the rear volume |
| P06R | Top → right transition band | P01 right natural/trimmed edge, P02 shoulder edge, front and rear sections | BlendSrf or a true edge-constrained Sweep2 |
| P06La/b/c | Top → left front / recess / left rear bands | P01 left edge split by region, corresponding edges of P03/04/05, section at the segment ends | Bridged per zone with inter-band continuity checks |
| P07/P08 | Front/rear end closures or assembly openings | Already-confirmed surrounding boundaries | Construct additional faces per the real design, or leave the opening |

The table above is a patch-region contract; P06L may need multiple four-edge faces, and "one region" must not be mistaken for "one face." If a longitudinal soft transition is needed between the recess base and the front/rear side surfaces, reserve and number separate front/rear transition bands; do not force incompatible edges together with Match.

### 2.4 Step-by-step construction

1. Match the camera with a low-complexity blockout, and first make length/width/height, the high point, and negative space valid. Save V00.
2. Complete C01–C03 and the Q sections, and cross-check in at least two reliable views; curvature comb changes should agree with the design intent.
3. Build only P01 and check the longitudinal/transverse sections and the fixed-camera silhouette. On failure, change section stations/shape/parameter correspondence first; do not build buttons yet.
4. Build the side volumes P02, P03, and P05, leaving room for transitions; do not collapse the top high point just to make them meet. Save V01.
5. Build the P04 recess base; first pass the deepest-point section, then control the front/rear fading. Where there is no basis for depth, keep the parameters and assumptions adjustable.
6. Design the widths and cross-band sections of each P06 band. Use Blend for quick trials; if there is a bulge, check correspondence/width/bulge, and where necessary extract a good section and use Sweep2 instead. Only real surface edges give transverse continuity semantics.
7. Check every E seam: position → tangent plane → the curvature actually required. After modifying one edge, recheck all the older edges and the inter-band edges. Enlarge the region when the centre or corner is incompatible.
8. Only then handle P07/P08 and the bottom assembly trims; mirror only regions whose symmetry has been proven. Save V02.
9. After the primary form passes acceptance, derive button seams, the scroll wheel hole, material regions, and the lower shell. A black hole cannot substitute for an inner wall and negative space.
10. Handle wall thickness, clips, bosses, draft, motion, and assembly clearance only when the engineering requires it, and verify them separately. Save the delivery version.

**Exit condition for this example:** the 3–5 features the client emphasised have corresponding dimensional / section / projection evidence; the patch layout and untrimmed parent surfaces remain editable; if G2 was not measured, do not report it as passing. A high global IoU must not mask an incorrect thumb recess depth or wheel hole.

## 3. Rotational speaker / bottle: prefer the object's real generative relationships

1. Judge whether it is genuinely axisymmetric: are the multi-view sections circular, and is there a flat area or a handle at the side/rear? Looking cylindrical from the front alone is not enough.
2. For a true solid of revolution, first define axis A, the upper and lower bounds Z0/Z1, and the profile R(z), separating the maximum belly radius, the height, the top/bottom taper, and the mouth.
3. Build the P01 body by Revolving one clean profile, and place the seam on a less sensitive side; use analytic lines/arcs where the profile requires it, and avoid interpolating every pixel. Check tangency and flatness at the polar region per the design.
4. Treat P02 top cover and P03 base as separate assembly parts; derive the continuous outer shape from a shared profile / parent surface wherever possible, rather than redrawing an inconsistent set of circles.
5. Treat grille colour as a material region first and do not automatically cut a recess. If real perforations exist, define the hole diameter, spacing, and edge margin; build one cell first and then array it, and verify the actual spacing after the surface mapping.
6. When the silhouette is wrong, go back to R(z) rather than covering an error in the belly with an added Blend. Build non-rotational regions as separate primary surfaces and transitions; do not force Revolve over the entire part.

Acceptance: axis, total height, maximum diameter and its height, top/bottom profiles, interfaces, reflections, and seam placement. When only the appearance surface is needed, there is no need to invent internal wall thickness.

## 4. Three-way tube handle / Y junction: treat the centre as its own problem

1. Build the three axes and branch sections, and determine the outer envelope, branch angles, centre width, and the passages/connection faces that must be preserved.
2. Build the P01/P02/P03 branch primary surfaces, extending past the centre; check the proportions of the whole part first, then cut away the intersecting centre.
3. Design the P04/P05/P06 bridge bands from sections normal to the branches. Three individually smooth bands do not mean the centre is finished.
4. Draw the centre's adjacency and tangent conditions first, and compare multiple four-edge patch fills against a wider network reconstruction; move incompatible convergence away from the critical highlight areas.
5. Patch may initialise the centre volume, but the edge zones and sections must be verified, and wide edge bands may need to be cut and rebuilt. The conclusion "Patch fills the hole and is automatically G2" is prohibited.
6. Check the circular/elliptical sections at every branch end, the central bulge, star reflections, and corner compatibility; when engineering requires it, check the thinnest wall, the internal passage, and self-intersection.

Failure fallback: pinched centre → enlarge the centre or re-define the bridge-end sections; bands conflicting with each other → change adjacency / edge tangents; drifting branch outlines → lock the analytic primary surfaces and widen the permitted deformation region instead of densifying every control point of the whole part.

## 5. Does the model match the client's intent: in-task acceptance gates

| Stage | What to present / record | What to do if it fails |
|---|---|---|
| Blockout | Fixed-camera silhouette, proportions, primary high point, negative space | Adjust the camera/depth assumptions and the blockout; defer detail |
| Parent surfaces | Primary sections, curvature flow, editable structure | Adjust sections or patch layout; do not fill holes first |
| Transitions | Key seam samples, reflections, corner regions; G2 evidence status | Widen/re-lay out the bands, or honestly state the limits |
| Detail | Item-by-item correspondence of the client's key features, position/size/count | Correct locally and recheck the parent form |
| Engineering | Contract-based thickness / interference / draft / exchange checks | Appearance pass is not a substitute for engineering |

When image capability is available, actually inspect the fixed-camera output; when the client asks you not to read images or no tool is available, state clearly that only numerical checks were performed. **The fact that the skill is detailed does not guarantee success for any agent with any reference.** A real task benchmark additionally requires the reference, the targets, and the final model, scored item by item; this package's procedural shell validates only the executable construction chain.
