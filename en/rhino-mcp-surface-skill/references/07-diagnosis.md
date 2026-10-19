# Diagnosis and recovery

Test one plausible cause per iteration and compare geometry/evidence. After two ineffective iterations reconsider upstream constraints. These are candidate causes, not one-to-one symptom recipes.

| Symptom | Inspect | Recovery |
|---|---|---|
| One view matches, others fail | Camera, depth, sections, occlusion | Return to blockout |
| Loft/Sweep twist | Direction, seams, frame, order | Correct correspondence |
| Boundaries match but interior bulges | Parameter speeds, corners, internal sections | Change boundary or method/layout |
| Wide/narrow Blend bulges | Pairing, sections, bulge, width | Try height options or section reconstruction |
| Star reflections | Poles, narrow corners, too many incident patches | Enlarge/relocate junction |
| Matching one edge breaks another | Freedom, masters, conflicting constraints | Wider band, joint constraints, relayout |
| Refine explodes points | Tolerances, target complexity, initial fit | Compare local insertion/reconstruction |
| Elevation does not change shape | Exact elevation selected? | Expected; edit increased freedom next |
| Join fails | Real gap, units, short edges, correspondence | Reintersect/reconstruct before loosening tolerance |
| Joined seam still creases | Tangent planes/curvature | Check G1/G2 separately |
| Trim fails | Cutter crossing, projection, tangency | Inspect intersection/endpoints and extend locally |
| Offset intersects itself | Radius, concavity, thickness | Revise geometry/thickness/corners |
| Numbers pass but reflection fails | Missed samples, display mesh, interior ripples | Refine local checks and sections |
| Uniform color map hides defects | Scale, averaging cancellation, mesh | Inspect principal curvature/sections |
| Fillet corner fragments | Radius, short edges, feature order | Reconstruct corner or revise sequence |
| MCP timeout | Operation already completed? | Query IDs/state before retry |
| API error | Signature, host, return type | Docstring and memory reproduction |

Recovery hierarchy: local parameters → boundaries/sections → transition band → neighboring freedom → untrimmed parents → layout. More CP and fewer CP can both be wrong depending on cause. Preserve intentional creases and negative curvature. Moving cameras or hiding defective objects is not repair.
