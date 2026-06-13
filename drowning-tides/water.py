import numpy as np
from settings import *
from mesh import Mesh


class Water:
    """A high-res water patch that follows the camera (recentred per frame, snapped
    to the grid). Vertices carry only (x, z); the vertex shader adds the patch centre
    and applies Gerstner displacement using world-space phase, so the sea stays put
    while the patch slides under the camera.
    """

    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.program = app.shader_program.water
        self.cell = (2.0 * WATER_SIZE) / WATER_GRID
        self.mesh = Mesh(self.ctx, self.program, self._build(), '2f', ('in_position',))

    def _build(self):
        n, s = WATER_GRID, WATER_SIZE
        coords = np.linspace(-s, s, n + 1, dtype='f4')
        gx, gz = np.meshgrid(coords, coords, indexing='ij')          # (n+1, n+1)

        def corner(i0, i1, j0, j1):
            return np.stack([gx[i0:i1, j0:j1], gz[i0:i1, j0:j1]], axis=-1)

        a = corner(0, n, 0, n)
        b = corner(1, n + 1, 0, n)
        c = corner(1, n + 1, 1, n + 1)
        d = corner(0, n, 1, n + 1)
        tris = np.stack([a, b, c, a, c, d], axis=2)                  # (n, n, 6, 2)
        return tris.reshape(-1, 2).astype('f4')

    def render(self):
        cam = self.app.camera.position
        cx = round(cam.x / self.cell) * self.cell
        cz = round(cam.z / self.cell) * self.cell
        self.program['u_center'] = (cx, cz)
        self.mesh.render()
