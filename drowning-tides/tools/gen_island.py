"""Generate a placeholder low-poly island model at
src/drowning_tides/assets/models/island.glb.

Authors a small surface-of-revolution hill (jittered rings + apex + base cap) with flat
outward normals and a single dark-rock material, then writes a glTF 2.0 binary. This is a
stand-in until real art exists; tweak the profile/seed/colour and re-run:

    uv run python tools/gen_island.py
"""
import math
import random
from pathlib import Path

import numpy as np
import pygltflib as g
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

OUT = Path(__file__).resolve().parent.parent / "src/drowning_tides/assets/models/island.glb"

SEG = 11                 # radial segments (odd -> less obvious symmetry)
SEED = 7
ROCK_COLOR = [0.11, 0.14, 0.12, 1.0]
# surface-of-revolution profile: (radius, height) rings from base up, then a single apex
PROFILE = [(1.00, -0.05), (0.93, 0.06), (0.74, 0.26), (0.50, 0.50), (0.26, 0.70)]
APEX_Y = 0.86
BASE_Y = -0.12


def _build_triangles():
    rng = random.Random(SEED)
    rings = []
    for r, y in PROFILE:
        verts = []
        for s in range(SEG):
            ang = 2.0 * math.pi * s / SEG
            jr = r * (1.0 + rng.uniform(-0.10, 0.10))
            jy = y + rng.uniform(-0.03, 0.03)
            verts.append((jr * math.cos(ang), jy, jr * math.sin(ang)))
        rings.append(verts)
    apex = (rng.uniform(-0.05, 0.05), APEX_Y, rng.uniform(-0.05, 0.05))

    body = []
    for k in range(len(rings) - 1):
        lo, hi = rings[k], rings[k + 1]
        for s in range(SEG):
            s2 = (s + 1) % SEG
            body.append((lo[s], lo[s2], hi[s2]))
            body.append((lo[s], hi[s2], hi[s]))
    top = rings[-1]
    for s in range(SEG):
        body.append((top[s], top[(s + 1) % SEG], apex))

    cap = []
    base = rings[0]
    center = (0.0, BASE_Y, 0.0)
    for s in range(SEG):
        cap.append((base[(s + 1) % SEG], base[s], center))

    return body, cap


def _normal(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    n = np.cross(b - a, c - a)
    ln = np.linalg.norm(n)
    return n / ln if ln > 1e-9 else np.array([0.0, 1.0, 0.0])


def _expand(body, cap):
    positions, normals = [], []
    for a, b, c in body:
        n = _normal(a, b, c)
        centroid = (np.array(a) + np.array(b) + np.array(c)) / 3.0
        radial = np.array([centroid[0], 0.0, centroid[2]])  # outward = away from the axis
        if np.linalg.norm(radial) > 1e-6 and np.dot(n, radial) < 0:
            n = -n
        positions += [a, b, c]
        normals += [n, n, n]
    for a, b, c in cap:
        n = np.array([0.0, -1.0, 0.0])  # underside faces down
        positions += [a, b, c]
        normals += [n, n, n]
    return np.array(positions, dtype="float32"), np.array(normals, dtype="float32")


def main():
    body, cap = _build_triangles()
    pos, nrm = _expand(body, cap)
    blob = pos.tobytes() + nrm.tobytes()

    gltf = GLTF2(
        scenes=[Scene(nodes=[0])],
        nodes=[Node(mesh=0)],
        materials=[
            Material(pbrMetallicRoughness=PbrMetallicRoughness(baseColorFactor=ROCK_COLOR))
        ],
        meshes=[Mesh(primitives=[
            Primitive(attributes=Attributes(POSITION=0, NORMAL=1), material=0)
        ])],
        accessors=[
            Accessor(bufferView=0, componentType=g.FLOAT, count=len(pos), type="VEC3",
                     min=pos.min(0).tolist(), max=pos.max(0).tolist()),
            Accessor(bufferView=1, componentType=g.FLOAT, count=len(nrm), type="VEC3"),
        ],
        bufferViews=[
            BufferView(buffer=0, byteOffset=0, byteLength=pos.nbytes, target=g.ARRAY_BUFFER),
            BufferView(
                buffer=0, byteOffset=pos.nbytes, byteLength=nrm.nbytes, target=g.ARRAY_BUFFER
            ),
        ],
        buffers=[Buffer(byteLength=len(blob))],
    )
    gltf.set_binary_blob(blob)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    gltf.save_binary(str(OUT))
    print(f"wrote {OUT} ({len(pos)} verts, {len(pos) // 3} tris)")


if __name__ == "__main__":
    main()
