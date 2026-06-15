"""glTF 2.0 model loading.

Parses a `.glb`/`.gltf` file into a flat, non-indexed interleaved vertex array
(`[pos.xyz, normal.xyz, color.rgb]` per vertex) that feeds the existing
`core/mesh.py::Mesh` with format `'3f 3f 3f'` — the same layout the procedural boat
uses, so loaded models render through the shared lit `model` shader unchanged.

Vertex colour comes, in priority order, from baked `COLOR_0`, then from a base-colour
texture sampled at each face's UV (so palette-textured packs like Kenney/Quaternius bake
down to flat per-face colours), then from the flat material `baseColorFactor`. This keeps
the low-poly flat-shaded look with no texturing in the shader. Missing normals are flat.
"""
import base64
import io
from pathlib import Path

import numpy as np
import pygame as pg
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


def _decode_image(gltf, image, base_dir):
    """Decode a glTF image (glb bufferView, data-uri, or external file) -> (H, W, 4) uint8."""
    if image.bufferView is not None:
        bv = gltf.bufferViews[image.bufferView]
        data = _buffer_bytes(gltf, gltf.buffers[bv.buffer])
        s = bv.byteOffset or 0
        surf = pg.image.load(io.BytesIO(bytes(data[s:s + bv.byteLength])))
    elif image.uri and image.uri.startswith("data:"):
        surf = pg.image.load(io.BytesIO(base64.b64decode(image.uri.split(",", 1)[1])))
    elif image.uri:
        p = base_dir / image.uri          # external file relative to the glb/gltf
        if not p.exists():
            return None
        surf = pg.image.load(str(p))
    else:
        return None
    w, h = surf.get_size()
    raw = pg.image.tostring(surf, "RGBA", False)  # row 0 = top, matching glTF UV origin
    return np.frombuffer(raw, np.uint8).reshape(h, w, 4)


def _base_color_image(gltf, material_index, cache, base_dir):
    if material_index is None or material_index >= len(gltf.materials or []):
        return None
    pbr = gltf.materials[material_index].pbrMetallicRoughness
    if pbr is None or pbr.baseColorTexture is None:
        return None
    source = gltf.textures[pbr.baseColorTexture.index].source
    if source not in cache:
        cache[source] = _decode_image(gltf, gltf.images[source], base_dir)
    return cache[source]


def _sample(image, uvs):
    """Nearest-sample an (H, W, 4) image at UVs (N, 2) -> (N, 3) floats in [0, 1]."""
    h, w = image.shape[:2]
    ix = np.clip((uvs[:, 0] * w).astype(int), 0, w - 1)
    iy = np.clip((uvs[:, 1] * h).astype(int), 0, h - 1)
    return image[iy, ix, :3].astype("f4") / 255.0


def load_vertices(path) -> np.ndarray:
    """Load a glTF file into a flat interleaved `'3f 3f 3f'` vertex array (non-indexed)."""
    gltf = GLTF2().load(str(path))
    base_dir = Path(path).parent
    chunks = []
    img_cache = {}
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

            # colour: baked COLOR_0 -> base-colour texture (sampled per face) -> flat material
            color_idx = getattr(prim.attributes, "COLOR_0", None)
            uv_idx = getattr(prim.attributes, "TEXCOORD_0", None)
            image = _base_color_image(gltf, prim.material, img_cache, base_dir)
            if color_idx is not None:
                cols = _read_accessor(gltf, color_idx).astype("f4")[:, :3][idx]
            elif image is not None and uv_idx is not None:
                tri_uv = _read_accessor(gltf, uv_idx).astype("f4")[idx]
                face_uv = tri_uv.reshape(-1, 3, 2).mean(axis=1)        # swatch centre per face
                face_col = _sample(image, face_uv) * _material_color(gltf, prim.material)
                cols = np.repeat(face_col, 3, axis=0)
            else:
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

    def __init__(self, ctx, program, path, position=(0.0, 0.0, 0.0), scale=1.0, yaw=0.0,
                 mute=0.0):
        self.program = program
        verts = load_vertices(path)
        if mute:   # desaturate toward luminance + dim, to fit the muted maritime palette
            v = verts.reshape(-1, 9)
            lum = v[:, 6:9] @ np.array([0.299, 0.587, 0.114], dtype="f4")
            v[:, 6:9] = (v[:, 6:9] * (1.0 - mute) + lum[:, None] * mute) * 0.94
        self.mesh = Mesh(
            ctx, program, verts, "3f 3f 3f",
            ("in_position", "in_normal", "in_color"),
        )
        # local-space bounding sphere (for frustum/distance culling)
        pos = verts.reshape(-1, 9)[:, :3]
        c = (pos.min(axis=0) + pos.max(axis=0)) * 0.5
        self.local_center = glm.vec3(float(c[0]), float(c[1]), float(c[2]))
        self.local_radius = float(np.linalg.norm(pos - c, axis=1).max())
        self.set_transform(position, scale, yaw)

    def set_transform(self, position, scale=1.0, yaw=0.0):
        m = glm.translate(glm.mat4(1.0), glm.vec3(*position))
        m = glm.rotate(m, yaw, glm.vec3(0, 1, 0))
        m = glm.scale(m, glm.vec3(scale))
        self.m_model = m

    def render(self):
        self.program["m_model"].write(self.m_model)
        self.mesh.render()
