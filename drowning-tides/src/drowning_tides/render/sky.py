import numpy as np

from drowning_tides.core.mesh import Mesh


class Sky:
    """Fullscreen gradient sky. Drawn first with depth test disabled; the view ray
    is reconstructed per fragment so the gradient tracks the camera orientation and
    the horizon band sits where the water meets the sky.
    """

    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.program = app.shader_program.sky
        quad = np.array([
            -1.0, -1.0, 3.0, -1.0, -1.0, 3.0,  # oversized triangle covering NDC
        ], dtype='f4')
        self.mesh = Mesh(self.ctx, self.program, quad, '2f', ('in_position',))

    def render(self):
        self.mesh.render()
