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
Inputs: authoritative arch/high-point, width distribution and transverse roundness constraints; compare an editable control-net parent with a boundary trial. Q sections are diagnostic by default, not automatic Loft inputs
Constraints: back arch height, high point in side view, maximum-width position in top view; do not move an already confirmed primary silhouette for Match
Seams: the left/right transition bands target G2 only if reflection requires it; if the front is a part separation, do not force continuity across it
Exit: fixed-camera silhouette/key points and primary sections pass; validity passes; no unintended interior waviness
Fallback: inspect uncontrolled constraints, then reconsider method and partitioning; do not perpetuate a failed approach by adding sections
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

The example remains an in-memory construction-chain check. Production delivery must also persist each wall's actual upper/lower inputs and the bottom loop under lines with mappings. P01 is directly control-net-driven: preserve its editable parent/parameters rather than inventing original curves. Follow [input preservation](16-preserve-construction-curves.md); AddBrep of the final solid alone does not satisfy editable delivery.

The native patch_with_lines/publish_patch helpers provide explicit registration for their returned inputs. This procedural enclosure remains an in-memory example, not an automatic delivery writer. Its historical12 checks validate only that chain.

### 1.6 Transferring from the example to a real housing

The client's side-view high point is off-centre → modify the longitudinal sections or the control net coefficients. A waist in top view → change the width of each column, but re-measure the actual maximum width; you cannot keep claiming it equals the input CP width. G2 side edges needed → first revise the layout to reserve transition bands; calling four walls joined by Join "G2" is invalid. Constant thickness needed → perform separate offset/edge-closure and self-intersection checks. Openings needed → derive the trim from an already-passed parent surface. After every change, re-check the dimensions and the related adjacent edges.

## 2. Asymmetric mouse shell with a deep side recess

See [15 Surface-led decisions, worked route](15-surface-led-construction.md) for the complete revised sequence. The default five-transverse-profile top Loft has been withdrawn. Establish independent top, flank, recess and transition roles; diagnostic sections are not automatic generative inputs. Choose the method from authoritative constraints.

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


## Retain construction inputs

Persist production input curves in the document under `lines`, map them to output patches and retain them through cleanup. See [16 Preserve construction curves](16-preserve-construction-curves.md), including Sweep2 input roles.
