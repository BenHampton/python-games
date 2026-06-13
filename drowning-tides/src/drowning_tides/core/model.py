"""glTF 2.0 model loading.

Parses a `.glb`/`.gltf` file into a flat, non-indexed interleaved vertex array
(`[pos.xyz, normal.xyz, color.rgb]` per vertex) that feeds the existing
`core/mesh.py::Mesh` with format `'3f 3f 3f'` — the same layout the procedural boat
uses, so loaded models render through the shared lit `model` shader unchanged.

Vertex colour comes from each primitive's PBR `baseColorFactor` (flat per-material),
which suits the low-poly look. Missing normals are computed flat per triangle.
"""
from pathlib import Path

import numpy as np
from pyglm import glm
from pygltflib import GLTF2

from drowning_tides.core.mesh import Mesh

# package-relative asset root (mirrors SHADERS_DIR in core/shader_program.py)
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
MODELS_DIR = ASSETS_DIR / "models"

DEFAULT_COLOR = (0.6, 0.6, 0.6)

# glTF componentType -> numpy dtype
_CTYPE = {5120: "i1", 5121: "u1", 5122: "i2", 5123: "u2", 5125: "u4", 5126: "f4"}
# glTF accessor type -> component count
_NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}


def _buffer_bytes(gltf, buffer):
    # glb stores everything in the binary blob (uri is None); .gltf may use a uri
    if buffer.uri is None:
        return gltf.binary_blob()
    return gltf.get_data_from_buffer_uri(buffer.uri)


def _read_accessor(gltf, index):
    acc = gltf.accessors[index]
    bv = gltf.bufferViews[acc.bufferView]
    data = _buffer_bytes(gltf, gltf.buffers[bv.buffer])
    ncomp = _NCOMP[acc.type]
    start = (bv.byteOffset or 0) + (acc.byteOffset or 0)
    arr = np.frombuffer(
        data, dtype=_CTYPE[acc.componentType], count=acc.count * ncomp, offset=start
    )
    return arr.reshape(acc.count, ncomp) if ncomp > 1 else arr


def _material_color(gltf, material_index):
    if material_index is None or material_index >= len(gltf.materials or []):
        return np.array(DEFAULT_COLOR, dtype="f4")
    pbr = gltf.materials[material_index].pbrMetallicRoughness
    if pbr is None or pbr.baseColorFactor is None:
        return np.array(DEFAULT_COLOR, dtype="f4")
    return np.array(pbr.baseColorFactor[:3], dtype="f4")


def _flat_normals(tri_positions):
    """Per-triangle face normals (one normal repeated across each triangle's 3 verts)."""
    p = tri_positions.reshape(-1, 3, 3)
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    length = np.linalg.norm(n, axis=1, keepdims=True)
    n = np.divide(n, length, out=np.zeros_like(n), where=length > 0)
    return np.repeat(n, 3, axis=0).astype("f4")


def load_vertices(path) -> np.ndarray:
    """Load a glTF file into a flat interleaved `'3f 3f 3f'` vertex array (non-indexed)."""
    gltf = GLTF2().load(str(path))
    chunks = []
    for mesh in gltf.meshes or []:
        for prim in mesh.primitives:
            pos = _read_accessor(gltf, prim.attributes.POSITION).astype("f4")
            if prim.indices is not None:
                idx = _read_accessor(gltf, prim.indices).astype("i4").reshape(-1)
            else:
                idx = np.arange(len(pos), dtype="i4")

            tri_pos = pos[idx]  # (3*tris, 3)
            if prim.attributes.NORMAL is not None:
                nrm = _read_accessor(gltf, prim.attributes.NORMAL).astype("f4")
                tri_nrm = nrm[idx]
            else:
                tri_nrm = _flat_normals(tri_pos)

            color = _material_color(gltf, prim.material)
            cols = np.tile(color, (len(tri_pos), 1)).astype("f4")
            chunks.append(np.concatenate([tri_pos, tri_nrm, cols], axis=1))  # (n, 9)

    if not chunks:
        raise ValueError(f"no mesh primitives found in {path}")
    return np.concatenate(chunks, axis=0).reshape(-1).astype("f4")


class Model:
    """A loaded glTF mesh rendered with the shared lit `model` program.

    Reusable for islands, buildings, NPCs — anything authored in Blender. Owns a model
    matrix; call `render()` inside the depth-tested world pass.
    """

    def __init__(self, ctx, program, path, position=(0.0, 0.0, 0.0), scale=1.0, yaw=0.0):
        self.program = program
        self.mesh = Mesh(
            ctx, program, load_vertices(path), "3f 3f 3f",
            ("in_position", "in_normal", "in_color"),
        )
        self.set_transform(position, scale, yaw)

    def set_transform(self, position, scale=1.0, yaw=0.0):
        m = glm.translate(glm.mat4(1.0), glm.vec3(*position))
        m = glm.rotate(m, yaw, glm.vec3(0, 1, 0))
        m = glm.scale(m, glm.vec3(scale))
        self.m_model = m

    def render(self):
        self.program["m_model"].write(self.m_model)
        self.mesh.render()
