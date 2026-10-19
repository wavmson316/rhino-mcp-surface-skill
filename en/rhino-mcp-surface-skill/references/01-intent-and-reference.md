# Inputs, intent, and uncertainty

## Define what must be reconstructed

Describe three to five distinguishing features: proportions, maximum belly/crown, shoulder or recess, negative space, edge softness, part division, and motion. Record purpose, source reliability, and permitted completion. Separate faithful reconstruction from redesign; do not silently beautify a source.

| Input | Useful constraints | Risks |
|---|---|---|
| Dimensioned orthographic drawings | Scale, projected boundaries, assembly positions | Distortion, inconsistent revisions |
| Perspective photographs | Projected silhouettes, occlusion, reflection trends | Focal-length/depth ambiguity, lens distortion |
| Sketches or text | Style and key proportions | Inconsistent perspective, unseen regions |
| Meshes or point clouds | Sample positions and deviations | Noise, outliers, holes, registration |

Typical priority: explicit dimensions/assembly, emphasized features, reliable multiple views, sections/reflections, details. Record conflicts and resolve by source quality instead of silently averaging.

## Interpret lines

A silhouette can be view-dependent occlusion, not a fixed 3D edge. Bright strips may be fillets or reflected lights; dark areas may be openings, recesses, or material. A terminator does not establish a patch boundary or discontinuity. Label each conclusion observed, cross-checked, inferred, or unknown.

## Calibrate orthographic drawings

Define world axes and image planes, image y direction, and handedness. Known length L over pixel distance d gives s=L/d. With unit plane axes A/B and origin O:

```text
a = s * (px - px0)
b = s * (py0 - py)
P = O + a*A + b*B
```

Use another dimension or shared feature to check scale, mirroring, and crop offsets. Apply nonuniform correction only for established drawing distortion and record residuals. Two arbitrary points do not determine independent axis scales.

For unknown scale normalize total length to 1 or 1000 units. When dimensions arrive, scale the model, then independently reconsider thickness and clearance. Reference uncertainty is different from seam tolerance.

## Perspective

Match projection, orientation, location, focal length, and cropping with a simple blockout first. Fix the camera during shape comparisons. Record alternative depth hypotheses if needed. A planar homography rectifies one plane, not an entire 3D photograph.

## Metrics

An orthographic location uncertainty of e pixels at scale s contributes about e*s length uncertainty, plus line width and registration. For photos report pixel/normalized residuals and camera assumptions.

Compare landmarks, contour distances, sections, IoU, or scan deviation distributions. IoU cannot certify depth, small holes, curvature, or dimensions. Fix projection/crop/size and report algorithm and sampling. Without actually viewing returned images, describe numerical checks rather than claiming visual acceptance.
