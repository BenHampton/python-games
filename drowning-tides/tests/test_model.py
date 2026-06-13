import numpy as np
import pygltflib as g
import pytest
from pygltflib import (
    GLTF2,
    Accessor,
    Attributes,
    Buffer,
    BufferView,
    Material,
    Mesh,
    Node,
    PbrMetallicRoughness,
    Primitive,
    Scene,
)

from drowning_tides.core.model import load_vertices

COLOR = [0.2, 0.6, 0.3, 1.0]


def _write_glb(path, positions, normals, indices, color=COLOR):
    pos = np.asarray(positions, dtype="float32")
    idx = np.asarray(indices, dtype="uint16")
    accessors = [
        Accessor(bufferView=0, componentType=g.UNSIGNED_SHORT, count=len(idx), type="SCALAR"),
        Accessor(bufferView=1, componentType=g.FLOAT, count=len(pos), type="VEC3"),
    ]
    blob = idx.tobytes() + pos.tobytes()
    views = [
        BufferView(buffer=0, byteOffset=0, byteLength=idx.nbytes, target=g.ELEMENT_ARRAY_BUFFER),
        BufferView(buffer=0, byteOffset=idx.nbytes, byteLength=pos.nbytes, target=g.ARRAY_BUFFER),
    ]
    attrs = Attributes(POSITION=1)
    if normals is not None:
        nrm = np.asarray(normals, dtype="float32")
        accessors.append(
            Accessor(bufferView=2, componentType=g.FLOAT, count=len(nrm), type="VEC3")
        )
        views.append(
            BufferView(buffer=0, byteOffset=idx.nbytes + pos.nbytes,
                       byteLength=nrm.nbytes, target=g.ARRAY_BUFFER)
        )
        blob += nrm.tobytes()
        attrs.NORMAL = 2

    gltf = GLTF2(
        scenes=[Scene(nodes=[0])],
        nodes=[Node(mesh=0)],
        materials=[Material(pbrMetallicRoughness=PbrMetallicRoughness(baseColorFactor=color))],
        meshes=[Mesh(primitives=[Primitive(attributes=attrs, indices=0, material=0)])],
        accessors=accessors,
        bufferViews=views,
        buffers=[Buffer(byteLength=len(blob))],
    )
    gltf.set_binary_blob(blob)
    gltf.save_binary(str(path))
    return path


def test_load_quad_vertex_count_and_layout(tmp_path):
    # a 2-triangle quad (4 verts, 6 indices)
    positions = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    normals = [[0, 0, 1]] * 4
    indices = [0, 1, 2, 0, 2, 3]
    p = _write_glb(tmp_path / "quad.glb", positions, normals, indices)

    verts = load_vertices(p)
    # 6 indexed verts expanded, 9 floats each (pos3 + normal3 + color3)
    assert verts.shape == (6 * 9,)
    rows = verts.reshape(-1, 9)
    assert np.allclose(rows[0, :3], [0, 0, 0])      # first position
    assert np.allclose(rows[:, 3:6], [0, 0, 1])     # normals passed through
    assert np.allclose(rows[:, 6:9], COLOR[:3])     # material colour per vertex


def test_missing_normals_are_computed_flat(tmp_path):
    # single triangle in the XY plane -> face normal +Z
    positions = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    indices = [0, 1, 2]
    p = _write_glb(tmp_path / "tri.glb", positions, None, indices)

    rows = load_vertices(p).reshape(-1, 9)
    assert rows.shape == (3, 9)
    assert np.allclose(rows[:, 3:6], [0, 0, 1])


def test_raises_when_no_primitives(tmp_path):
    gltf = GLTF2(scenes=[Scene(nodes=[])], buffers=[Buffer(byteLength=0)])
    gltf.set_binary_blob(b"")
    p = tmp_path / "empty.glb"
    gltf.save_binary(str(p))
    with pytest.raises(ValueError):
        load_vertices(p)
