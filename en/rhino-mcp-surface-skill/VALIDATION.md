# 1.2.0 release validation record

1.2.0 is a **documentation-only release**: verified figures, construction discipline, and API errata were restored to the body text, and [13 construction-discipline rules](references/13-construction-discipline.md) were added. **The code, tests, and geometric behavior are exactly identical to 1.1.0; no new platform or modeling validation claim is added.**

The geometry results below all come from 1.0.0/1.1.0: Rhino in-memory regression 45/45, 2D metrics 17/17, construction chain 12/12.

Date: 2026-10-19. The tested platform was Windows, Rhino **8.29.26063.11001**, Rhino's internal Python 3, and the current MCP connection. No image reading was performed; the old claim of having "read every scan page" is not carried forward as a fact for this round.

## 1.2.0 documentation changes

| Change | Content | New validation added? |
|---|---|---|
| `10-parameters` rewritten | The five-category numeric framework is retained, and unit conversion tables, exploration budgets, measured MatchSrf tolerance anchors, key recipes, fillet tables, IoU pitfalls, and a Class-A scope warning were restored | ❌ Documentation only |
| `13-construction-discipline.md` added | Three things to do before starting, three ordering rules, and the irreversible constraints for surfacing, curves, 3C, continuity, and acceptance | ❌ Documentation only |
| Additions to `03` / `04` / `05` / `07` / `11` | Three-row method boundaries, Deformable usage, three G2 misjudgement errors, CurvatureAnalysis timing, API errata, port discipline, symptom table | ❌ Documentation only |
| `SKILL.md` | Additional reading on parameter routing, the three ordered steps and three rules, and the check items for Stage 3–6 | ❌ Documentation only |

⚠️ Every restored figure is labelled with its **source, applicability conditions, and failure signal**, and is not a manufacturing standard or a permanent default.
⚠️ The `Class-A` section gained a scope warning — it belongs to the automotive OEM system,
⛔ and does not apply to appliances, toys, or furniture (where injection-moulded tolerances are often in the 0.1–0.3 mm range).

## Automated tests

| Scope | Result | Verifiable evidence |
|---|---|---|
| Rhino in-memory geometry regression | **45/45** | [rhino-test-results.json](rhino-test-results.json)、[test code](scripts/smoke_test_rhino.py) |
| Standalone 2D metrics | **17/17** | [outline-test-results.json](outline-test-results.json)、[test code](scripts/test_outline_metrics.py) |
| Programmatic closed-shell parent form | **12/12** | [example-test-results.json](example-test-results.json)、[code](scripts/example_closed_shell.py) |
| Python syntax, local Markdown file links, entry point, and distribution checks | Run at release time | [check_release.py](scripts/check_release.py), release manifest |

The Rhino tests add, delete, or edit no document objects; object counts, units, and tolerance settings are identical before and after. The dates and versions in the test result JSON represent this run and do not guarantee that other versions pass automatically. After installation you can re-run them following the [self-check steps](INSTALL-CHECK.md).

## What the Rhino tests cover

- Surface seams: coplanar contact, same-side 90° folds, a 1-unit gap; rejection of negative indices, non-integer sample counts, and non-finite tolerances; closed edges explicitly rejected, requiring a seam-aware pairing strategy.
- Structural audit: valid open surfaces with 4 naked edges, actual U/V spans, repeated knots causing CP−Degree ≠ SpanCount, and explicit reports of missing document objects.
- Curves: control points and interpolation, periodic construction, interior geometry tangency of exact circles, shape-preserving exact degree elevation, and true properties.
- Rebuild: correct overload selection and single-span candidates, explicit deviation budgets, rejection when no budget is supplied, rejection of underfit polyline/low-degree cases, and rejection of closed inputs.
- Curve joining: same-direction contact passes; 90° corner, 180° reversal, and parallel-but-disconnected cases are rejected; opposite-endpoint pairing, unknown mode rejection, and closed-shape shortcut-check rejection.
- Surfacing: three-edge surfaces, four-edge surfaces, edge direction/order, edges of differing Degree, disconnected-boundary rejection, ruled surfaces, open Loft, capped solid, closed Loft direction, and rejection on insufficient input or missing cap tolerance.
- Curvature: planar zero curvature, spherical principal curvature magnitudes; explicit reference-plane width/height and illegal dimension handling.

## What the 2D metrics cover

Identical outlines, overlapping rectangles, separated shapes, repeated closing points, reversed outlines, analytical area ratios for four sets of concentric circles, boundary distance, empty/degenerate/non-finite inputs, illegal resolutions, and legacy buffer-behaviour rejection.

The error thresholds apply only to these test instances; no claim is made that an arbitrary outline yields the same error at any raster resolution. Thin, small features need higher resolution and local metrics. Only a single simple polygon outer ring is supported — holes, multiple components, and self-intersections are not; callers must ensure the input topology is valid.

## ⭐ Known implementation pitfalls (written into the parameters reference to prevent misuse)

| Pitfall | Consequence |
|---|---|
| Using point-set Jaccard instead of rasterisation to compute IoU | Every sampled point of a scaled copy falls inside the other outline, so **a 10% size error looks like a perfect score** |
| Ray casting does not handle on-boundary point ambiguity | Of 40 points on a circle only 20 are classified as inside, and IoU collapses |
| Treating IoU as dimensional accuracy | Scaling concentric circles by r gives IoU = r², so **at a 10% size difference IoU is still 0.83** |

## Explicitly unverified or not certified

1. **Full-domain inter-surface G2/G3 numerical certification.** The seam script samples only position and the unoriented tangent plane; it does not examine the second-order form operator and does not prove the absence of folds or overlap.
2. **End-to-end reconstruction quality from a real photograph to a complete model.** The examples are reasoning templates and cannot be described as a finished model. Unknown camera, scale, and back-side conditions still require in-task handling.
3. **Manufacturability.** Wall thickness, self-intersection, draft, parting lines, process shrinkage, assembly motion, and any OEM standard require per-project verification.
4. **STEP/IGES/STL round-tripping and material/layer fidelity.** No actual exchange test was performed in this round.
5. **The full option matrix of all Rhino native commands, GH components, other MCP plugins, Rhino 6/7, or other platforms.** Verify by capability discovery in the current environment and minimal experiments.
6. The curvature function evaluates the nearest underlying surface; it does not identify the trimmed visible domain and does not automatically convert to an outward solid normal. A single-point evaluation cannot represent surface fairness.
7. The curve distance check is a Rhino numerical estimate, not an exact Hausdorff bound; highly localised features require denser sampling or independent checks.
8. **Fillet values and tolerances marked as "textbook cases" in the parameters reference** were not verified on physical parts; they are operation records from the book only.

## Release blockers fixed from earlier versions (recorded in 1.1.0)

Fixed the wrong Rebuild overload, the non-existent `Surface.CreateEdgeSrf`, the wrong Loft overload, and the non-existent curvature method; fixed Unitize returning a boolean that was treated as a dot product, which caused 90° curves to report 0°. The old six smoke cases did not cover these public helpers, so they could not demonstrate that the entire older toolkit was correct. The new tests exercise each class of release entry point and each critical counterexample separately.

The unverified command-string helper for placing views was removed; explicit reference-plane geometry functions were retained. The 2D metrics were split into a module with no Rhino dependency. The main entry point and 12 references were unified on conditional methods, and the old knowledge graph is no longer an execution dependency.

## 1.1.0 addition: object construction chain validation

[example_closed_shell.py](scripts/example_closed_shell.py) builds a double-curved crown, four derived ruled walls, and a flat bottom in memory at explicit dimensions, then joins them into a valid solid, with an actual surface centre height of 40. **12/12** pass; see the [results](example-test-results.json) and the [detailed playbook](references/12-object-construction-playbooks.md). It checks the 6 parent surfaces, the valid closed body, edge state, orientation, Degree/Span, the actual crown height, positive volume, error inputs, and that the document is unchanged. It does not validate G2, wall thickness, injection moulding, or similarity to a reference image.
