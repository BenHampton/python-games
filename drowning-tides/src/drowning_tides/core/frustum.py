"""View-frustum culling (Gribb–Hartmann).

Extracts the six frustum planes from a combined view-projection matrix and tests bounding
spheres against them, so off-screen islands can be skipped. glm is column-major, so matrix
rows are gathered as `(m[0][i], m[1][i], m[2][i], m[3][i])`.
"""
from pyglm import glm


def extract_planes(view_proj):
    """Return six (normal, d) planes; a point is inside when dot(normal, p) + d >= 0."""
    m = view_proj

    def row(i):
        return glm.vec4(m[0][i], m[1][i], m[2][i], m[3][i])

    r0, r1, r2, r3 = row(0), row(1), row(2), row(3)
    raw = [r3 + r0, r3 - r0, r3 + r1, r3 - r1, r3 + r2, r3 - r2]

    planes = []
    for p in raw:
        n = glm.vec3(p.x, p.y, p.z)
        length = glm.length(n)
        if length > 1e-9:
            planes.append((n / length, p.w / length))
        else:
            planes.append((n, p.w))
    return planes


def sphere_visible(planes, center, radius):
    for n, d in planes:
        if glm.dot(n, center) + d < -radius:
            return False
    return True
