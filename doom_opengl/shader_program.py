from settings import *

class ShaderProgram:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.player = app.player

        #--------- sharder --------- #
        self.level = self.get_program(shader_name='level')
        # self.quad = self.get_program(shader_name='quad')
        #--------------------------- #
        self.set_uniforms_on_init()

    def set_uniforms_on_init(self):
        # level
        self.level['m_proj'].write(self.player.m_proj)
        self.level['u_texture_array_0'] = TEXTURE_UNIT_0

    def update(self):
        self.level['m_view'].write(self.player.m_view)

    def get_program(self, shader_name):
        with open(f'shaders/{shader_name}.vert') as file:
            vertex_shader = file.read()

        with open(f'shaders/{shader_name}.frag') as file:
            fragment_shader = file.read()

        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program