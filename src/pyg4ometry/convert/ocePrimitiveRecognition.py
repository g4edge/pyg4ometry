from __future__ import annotations

from collections import Counter
from itertools import combinations, product
from typing import Any

import math

import numpy as np

from .. import pyoce as _pyoce


def classify_surface(surface: Any) -> str:
    geom = _pyoce.Geom

    known_types = [
        (geom.Geom_Plane, "Plane"),
        (geom.Geom_CylindricalSurface, "Cylinder"),
        (geom.Geom_ConicalSurface, "Cone"),
        (geom.Geom_SphericalSurface, "Sphere"),
        (geom.Geom_ToroidalSurface, "Torus"),
        (geom.Geom_BSplineSurface, "B-spline"),
        (geom.Geom_BezierSurface, "Bezier"),
        (
            geom.Geom_RectangularTrimmedSurface,
            "Rectangular-trimmed surface",
        ),
        (geom.Geom_OffsetSurface, "Offset surface"),
        (geom.Geom_SweptSurface, "Swept surface"),
    ]

    for surface_class, name in known_types:
        if isinstance(surface, surface_class):
            return name

    return type(surface).__name__


def canonical_axis(axis: np.ndarray) -> np.ndarray:
    axis = np.asarray(axis, dtype=float)
    length = float(np.linalg.norm(axis))

    if length <= 0.0:
        message = "Zero-length box axis."
        raise RuntimeError(message)

    axis = axis / length

    for value in axis:
        if abs(float(value)) <= 1.0e-15:
            continue

        if value < 0.0:
            axis = -axis

        break

    return axis


def point_set_error(
    predicted: np.ndarray,
    observed: np.ndarray,
) -> tuple[float, float]:
    differences = predicted[:, None, :] - observed[None, :, :]
    distances = np.linalg.norm(differences, axis=2)

    forward = np.min(distances, axis=1)
    reverse = np.min(distances, axis=0)
    combined = np.concatenate([forward, reverse])

    return (
        float(math.sqrt(np.mean(np.square(combined)))),
        float(np.max(combined)),
    )


def clean_vector(
    values: list[float],
    tolerance: float = 1.0e-12,
) -> list[float]:
    return [0.0 if abs(float(value)) < tolerance else float(value) for value in values]


def reconstruct_box_from_vertices(
    body_name: str,
    vertices: Any,
    orthogonality_tolerance: float = 1.0e-9,
    reconstruction_tolerance_mm: float = 1.0e-9,
) -> dict[str, Any]:
    points = np.asarray(vertices, dtype=float)

    if points.shape != (8, 3):
        message = (
            f"{body_name}: exact G4Box reconstruction "
            f"requires 8 unique vertices; observed "
            f"shape {points.shape}."
        )
        raise RuntimeError(message)

    best: dict[str, Any] | None = None

    for origin_index, origin in enumerate(points):
        other_indices = [index for index in range(len(points)) if index != origin_index]

        for edge_indices in combinations(
            other_indices,
            3,
        ):
            edges = np.array(
                [points[index] - origin for index in edge_indices],
                dtype=float,
            )
            lengths = np.linalg.norm(edges, axis=1)

            if np.any(lengths <= reconstruction_tolerance_mm):
                continue

            measured_axes = edges / lengths[:, None]
            gram = measured_axes @ measured_axes.T

            orthogonality_residual = float(np.max(np.abs(gram - np.identity(3))))

            if orthogonality_residual > orthogonality_tolerance:
                continue

            predicted = np.array(
                [
                    origin + bit_a * edges[0] + bit_b * edges[1] + bit_c * edges[2]
                    for bit_a, bit_b, bit_c in product((0.0, 1.0), repeat=3)
                ],
                dtype=float,
            )

            rms, maximum = point_set_error(
                predicted,
                points,
            )

            candidate = {
                "origin": origin,
                "edges": edges,
                "lengths": lengths,
                "axes": measured_axes,
                "orthogonality_residual": (orthogonality_residual),
                "rms": rms,
                "maximum": maximum,
            }

            if (
                best is None
                or maximum < best["maximum"]
                or (maximum == best["maximum"] and rms < best["rms"])
            ):
                best = candidate

    if best is None:
        message = f"{body_name}: eight vertices do not form an orthogonal box."
        raise RuntimeError(message)

    if best["maximum"] > reconstruction_tolerance_mm:
        message = (
            f"{body_name}: best box reconstruction "
            f"maximum error {best['maximum']:.12g} mm "
            f"exceeds {reconstruction_tolerance_mm:.12g} mm."
        )
        raise RuntimeError(message)

    axes = np.array(
        [canonical_axis(axis) for axis in best["axes"]],
        dtype=float,
    )
    lengths = np.asarray(best["lengths"], dtype=float)

    order = sorted(
        range(3),
        key=lambda index: (
            int(np.argmax(np.abs(axes[index]))),
            tuple(np.round(axes[index], 15)),
            float(lengths[index]),
        ),
    )

    axes = axes[order]
    lengths = lengths[order]

    basis_determinant = float(np.linalg.det(axes))
    if not np.isclose(
        abs(basis_determinant),
        1.0,
        atol=orthogonality_tolerance,
        rtol=0.0,
    ):
        message = (
            f"{body_name}: reconstructed box basis determinant "
            f"{basis_determinant:.12g} is not orthogonal."
        )
        raise RuntimeError(message)
    if basis_determinant < 0.0:
        # A box is invariant under an axis sign flip.  Enforce a
        # right-handed basis so the downstream correction is a proper
        # rotation rather than a reflection.
        axes[-1] = -axes[-1]

    centre = np.asarray(best["origin"], dtype=float) + 0.5 * np.sum(best["edges"], axis=0)

    local_corners = np.array(
        [
            np.asarray(signs, dtype=float) * 0.5 * lengths
            for signs in product(
                (-1.0, 1.0),
                repeat=3,
            )
        ],
        dtype=float,
    )

    reconstructed = centre + local_corners @ axes
    rms, maximum = point_set_error(
        reconstructed,
        points,
    )

    if maximum > reconstruction_tolerance_mm:
        message = (
            f"{body_name}: canonical G4Box "
            f"reconstruction maximum error "
            f"{maximum:.12g} mm exceeds "
            f"{reconstruction_tolerance_mm:.12g} mm."
        )
        raise RuntimeError(message)

    return {
        "representation": "G4Box",
        "centre": clean_vector(centre.tolist()),
        "dimensions": clean_vector(lengths.tolist()),
        "local_axes": [clean_vector(axis.tolist()) for axis in axes],
        "reconstruction_source": ("in_memory_tessellated_vertices"),
        "vertex_rms_mm": rms,
        "vertex_maximum_mm": maximum,
        "axis_orthogonality_residual": float(np.max(np.abs(axes @ axes.T - np.identity(3)))),
    }


def shape_surface_summary(shape) -> Counter:
    explorer = _pyoce.TopExp.TopExp_Explorer(
        shape,
        _pyoce.TopAbs.TopAbs_FACE,
        _pyoce.TopAbs.TopAbs_SHAPE,
    )

    counts = Counter()

    while explorer.More():
        face = _pyoce.TopoDS.TopoDSClass.Face(explorer.Current())
        surface = _pyoce.BRep.BRep_Tool.Surface(face)
        counts[classify_surface(surface)] += 1
        explorer.Next()

    return counts


def recognise_box_from_shape_vertices(name: str, shape, vertices):
    if shape_surface_summary(shape) != Counter({"Plane": 6}):
        return None

    try:
        return reconstruct_box_from_vertices(name, vertices)
    except RuntimeError:
        return None
