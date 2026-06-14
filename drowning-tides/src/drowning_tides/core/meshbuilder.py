"""Tiny runtime builder for flat-shaded, per-vertex-coloured geometry, producing the
interleaved `'3f 3f 3f'` (pos, normal, colour) array the `model` shader + `core/mesh.py`
expect. Used for procedural props (village houses, NPCs, docks)."""
import numpy as np
from pyglm import glm


class MeshData:
    def __init__(self):
        self.rows = []

    def tri(self, a, b, c, color):
        a, b, c = glm.vec3(*a), glm.vec3(*b), glm.vec3(*c)
        n = glm.cross(b - a, c - a)
        if glm.length(n) > 1e-9:
            n = glm.normalize(n)
        else:
            n = glm.vec3(0, 1, 0)
        for p in (a, b, c):
            self.rows.append((p.x, p.y, p.z, n.x, n.y, n.z, color[0], color[1], color[2]))

    def quad(self, a, b, c, d, color):
        self.tri(a, b, c, color)
        self.tri(a, c, d, color)

    def box(self, cx, cy, cz, hx, hy, hz, color):
        x0, x1 = cx - hx, cx + hx
        y0, y1 = cy - hy, cy + hy
        z0, z1 = cz - hz, cz + hz
        self.quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), color)  # +z
        self.quad((x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0), color)  # -z
        self.quad((x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1), color)  # +x
        self.quad((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0), color)  # -x
        self.quad((x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0), color)  # top
        self.quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), color)  # bottom

    def gable_roof(self, cx, cy, cz, hx, hz, ridge_h, color):
        """A simple pitched roof: ridge along x at height cy+ridge_h over a (hx,hz) footprint."""
        x0, x1 = cx - hx, cx + hx
        z0, z1 = cz - hz, cz + hz
        r0 = (x0, cy + ridge_h, cz)
        r1 = (x1, cy + ridge_h, cz)
        self.quad((x0, cy, z1), (x1, cy, z1), r1, r0, color)   # front slope
        self.quad((x1, cy, z0), (x0, cy, z0), r0, r1, color)   # back slope
        self.tri((x0, cy, z0), (x0, cy, z1), r0, color)        # gable ends
        self.tri((x1, cy, z1), (x1, cy, z0), r1, color)

    def array(self):
        return np.array(self.rows, dtype="f4").reshape(-1)
