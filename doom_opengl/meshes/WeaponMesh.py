from doom_opengl.meshes.quad_mesh import QuadMesh


class WeaponMesh(QuadMesh):
    def __init__(self, eng, shader_program, weapon_instance):
        super().__init__(eng, shader_program)
        #
        self.weapon = weapon_instance
        self.program['m_model'].write(self.weapon.m_model)

    def render(self):
        self.program['tex_id'] = self.weapon.frame + self.weapon.weapon_id
        self.vao.render()