from doom_opengl.meshes.base_mesh import BaseMesh
from settings import *
import numpy as np


class QuadMesh(BaseMesh):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.ctx = app.ctx
        self.program = app.shader_program.quad

        self.vbo_format = '3f 3f'
        self.attrs = ('in_position', 'in_color')
        self.vao = self.get_vao()

    def get_vertex_data(self):
        # vertices = [
        #     (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0), (-0.5, -0.5, 0.0),
        #     (0.5, 0.5, 0.0), (-0.5, -0.5, 0.0), (0.5, -0.5, 0.0)
        # ]
        #
        # colors = [
        #     (0, 1, 0), (1, 0, 0), (1, 1, 0),
        #     (0, 1, 0), (1, 1, 0), (0, 0, 1)
        # ]

        vert_position = (
            [-0.5, 0.0, 0.0, 1.0], [-0.5, 1.0, 0.0, 1.0],
            [0.5, 1.0, 0.0, 1.0], [0.5, 0.0, 0.0, 1.0]
        )

        uv_coords = (
            [1, 1], [1, 0], [0, 0], [0, 1]
        )

        vert_indices = [
            0, 2, 1, 0, 3, 2
        ]

        # vertex_data = np.hstack([vertices, colors], dtype='float32')
        vert_data = []
        for vert_index in vert_indices:
            vert_data += vert_position[vert_index]
            vert_data += uv_coords[vert_index]

        vert_data = np.array(vert_data, dtype='float32')
        return vert_data
