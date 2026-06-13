import numpy as np


class Mesh:
    """Thin wrapper over a moderngl VAO built from an interleaved vertex array.

    fmt / attrs follow moderngl conventions, e.g. fmt='3f 3f',
    attrs=('in_position', 'in_normal').
    """

    def __init__(self, ctx, program, vertex_data: np.ndarray, fmt: str, attrs):
        self.ctx = ctx
        self.vbo = ctx.buffer(vertex_data.astype('f4').tobytes())
        self.vao = ctx.vertex_array(
            program, [(self.vbo, fmt, *attrs)], skip_errors=True
        )

    def render(self, mode=None):
        if mode is None:
            self.vao.render()
        else:
            self.vao.render(mode)

    def destroy(self):
        self.vbo.release()
        self.vao.release()
