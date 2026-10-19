# Changelog

## 1.2.0 — 2026-10-19

**Documentation release. The code and geometric behavior are exactly identical to 1.1.0, and the test results are unchanged.**

- Added [13 construction-discipline rules](references/13-construction-discipline.md): three things to do before starting, three ordering rules,
  and the irreversible constraints for the surfacing, curve, 3C, continuity, and acceptance stages (each with its failure signal and source).
- Expanded [10 parameters](references/10-parameters-and-recipes.md):
  within the five-category numeric classification framework, added unit conversion tables, exploration budgets, measured MatchSrf tolerance anchors, edge-smoothing chains, key recipes,
  measured fillet tables, a Class-A scope warning, and three IoU implementation pitfalls.
  **Every figure is labelled with its source, applicability conditions, and failure signal**, and is not a manufacturing standard or a permanent default.
- `03`: added the applicable boundaries of the three-row method, `EdgeSrf` opposite-edge degree checks, the distinction between the two `ChangeDegree` modes,
  and `ExtrudeCrv`/`Extrude` options.
- `04`: added three wrong approaches to judging G2, why the light–dark boundary does not demand G2, checking inputs first when matching fails,
  mirror timing, and CurvatureAnalysis timing.
- `05`: added four API forms disproven by actual testing in Rhino 8 (`doc.Units.SetUnits` and similar)
  and port discipline.
- `07`: added 17 measured symptoms and the upstream fallback paths for hangs.
- `11`: added offset patch planning, `Extrude` degree elevation to recover G2, edge-smoothing chains, the correct interpretation of a twisting `Same height shapes`,
  mid-section alignment in `Setpt`, and the 7-step key recipe.
- `SKILL.md`: additional reading on parameter routing, the three ordered steps and three rules, and the Stage 3–6 check items.

**No new platform or modeling validation claim was added**; the test results remain 45/45, 17/17, and 12/12.

## 1.1.0 — 2026-10-19

- Added object patch planning and step-by-step construction playbooks, curve and patch contracts, task acceptance gates, and a closed-shell parent-form construction script with 12 measured checks.
- Completed the Chinese and English overview pages, clarifying Rhino 8, McNeel Rhino MCP Platform, router/connector, and the installation steps.
- Added the complete English skill body, 12 references, installation, self-checks, a project template, validation notes, and update instructions.
- Chinese and English packages are provided separately, sharing the same skill ID and geometry implementation; install one or the other.
- This is a documentation and distribution update, adding no geometry or platform validation claim.

## 1.0.0 — 2026-10-19

- Unified the entry point and 12 references, routing them by geometric constraint, purpose, and evidence; removed hard category restrictions and mutually contradictory rules.
- Corrected statements about Degree/span/period/circle/degree elevation/Refine/Offset/projection/mesh Weld; added applicability conditions to the case recipes.
- Fixed the rebuild, EdgeSrf, Loft, curvature, and curve G1 helpers; removed the unverified view-placement command concatenation entry point and replaced it with explicit geometric input.
- Made the 2D outline metrics an independent ordinary Python module and added boundary conditions; expanded Rhino in-memory validation and release checks.
- Separated measured results, cases, and unverified items; the release package depends on no workspace, images, or external legacy knowledge graph.
