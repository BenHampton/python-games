# Drowning Tides — Build Plan

A low-poly maritime cosmic-horror fishing game. Built one phase at a time; each phase leaves
the game runnable so we can play-test and tweak before moving on.

**Run / test any time:**

```
uv run python main.py        # play
uv run pytest                # logic tests
uv run ruff check src tests  # lint
```

## Locked decisions

- **3D models:** complex shapes load as **glTF 2.0** via **pygltflib** (MIT, pure-Python),
  assembled into moderngl VBOs through the existing `core/mesh.py::Mesh`. Simple geometry
  (water, props) stays procedural like `world/boat.py`.
- **Boat ⇄ on-foot:** press **E** to mount/unmount the boat. Mounted = drive (follow cam);
  unmounted = first-person on-foot. Walking on the *moving boat deck* is future — for now you
  dismount onto land/docks.
- **Deferred (revisit later):** inventory, economy (sell/buy), save/load; deck-walking;
  story + side-quests.
- **Conventions:** reuse `Mesh`; `cfg` config (no `import *`); package-relative asset paths
  (mirror `SHADERS_DIR`); ruff-clean; pure-logic tests where no GL context is needed.
- **Invariant:** keep GPU/CPU Gerstner wave parity (`shaders/water.vert` ↔ `world/waves.py`).

---

## Phase 0 — Foundations

Infra every later phase needs.

- Add `pygltflib` to `pyproject.toml`; `uv sync`.
- `core/model.py` — glTF loader → interleaved data → existing `Mesh` (`'3f 3f 3f'`).
- `shaders/model.vert` / `model.frag` — lit mesh program mirroring `boat.*` (sun + fog);
  register in `core/shader_program.py`.
- `ASSETS_DIR` (package-relative, like `SHADERS_DIR`); add `assets/models/`.
- `core/game_state.py` — `HELM` / `ON_FOOT` control-mode state machine; route input + active
  camera/entity through it (generalizes today's `console.active` gating).

**Run after completion:** `uv run python main.py` still plays exactly as today (no visible
change). `uv run pytest` covers the loader (vertex counts from a tiny fixture `.glb`) and the
state-machine transitions. Tweakable: loader/material handling, state machine.

## Phase 0.5 — World environment (day/night, sky, light, water, fog)

- Day/night cycle (`world/daycycle.py`): sun arcs, moon opposite, time-keyed mood palette;
  composed with `storm_intensity` and fog in `core/shader_program.py`.
- Sky (`shaders/sky.frag`): sun disc, moon disc, stars fading in at night.
- Water (`shaders/water.frag`): sun/moon glint, whitecaps, sky-tinted fresnel.
- Rolling fog banks (`FogBank` in `world/weather.py`), day or night, capped at 60s
  (TODO: more realistic durations later).
- Console: `/time`, `/timescale`, `/fog-on`, `/fog-kill` (documented in the README).

**Run after completion:** `uv run python main.py`; use `/timescale 20` to fast-forward the
cycle, `/time 0.0|0.5|0.75` to jump to night/noon/dusk, `/fog-on` to force a fog bank. Watch
sun/moon arc, stars at night, water glint + sky tint. Tweak `cfg` day keyframes, `DAY_LENGTH`,
sun/moon colours, fog ranges.

## Phase 1 — Islands / terrain

- `world/island.py` — load low-poly island model(s), place with model matrices, render in the
  fog-lit world pass (`render/scene.py`).
- Boat collision — per-island radius test in `boat.update`; block/push the boat off land.
  Radii in `cfg`.

**Run after completion:** sail toward an island; it renders lit + fogged; boat collides and is
pushed back. Tweak island placement/scale and collision radii in `cfg`.

## Phase 2 — First-person on-foot + mount/unmount (E)

- `world/player.py` — on-foot controller: WASD move + mouse-look, ground clamp (flat dock /
  island height). First-person → no character mesh needed.
- Wire `render/camera.py` `FIRST_PERSON` to the player (replace the boat-anchored stub).
- E mount/unmount via `game_state`: near boat + E → `HELM`; E again → spawn player beside boat,
  `ON_FOOT`. Idle boat keeps floating while on foot. Unify input gating (console + mode).

**Run after completion:** drive to an island, press E to disembark, walk in first person,
press E near the boat to re-board. Tweak walk speed, mouse sensitivity, mount range in `cfg`.

## Phase 3 — Town: buildings, NPCs, NPC boats

- `world/town.py` — place building models on an island; define dock points.
- `world/npc.py` — character models, simple idle/waypoint movement.
- `world/npc_boat.py` — wandering NPC boats on simple sea paths.
- Dialogue stub in `ui/` — approach NPC + press E → painterly 2D text panel (reuse the
  console's pygame-surface→GL-texture overlay). No quest logic yet.

**Run after completion:** dock, walk the town, see NPCs moving + NPC boats sailing, trigger a
dialogue panel. Tweak town layout, NPC paths/speeds, dialogue text.

## Phase 4 — Fishing mechanics (no economy)

- `world/fishing.py` — cast → wait → catch sequence from helm or on foot at a spot; show the
  result via message/log. Fish as data in `cfg` (species, rarity). No inventory/economy yet.

**Run after completion:** trigger fishing, receive a catch result. RNG seedable for tests.
Tweak catch timing, fish table/rarities.

## Phase 5 — Aberrated creatures + chromatic aberration

- Aberrated creature variants (glTF) with warped behavior; some catches are "aberrated."
- Chromatic aberration in `shaders/post.frag`: radial per-channel (R/G/B) UV offsets scaled by
  a new uniform, driven by proximity to aberrated creatures and/or `storm_intensity`.

**Run after completion:** aberration visibly ramps near aberrated creatures / horror beats.
Tweak aberration strength/falloff and creature behavior.

---

## Deferred (noted, not dropped)

- Game systems: inventory, economy (currency, sell/buy), save/load persistence.
- Walking on the moving boat deck (parented-transform problem).
- Story + side-quests, progression.

---

## Progress

- [x] Phase 0 — Foundations (glTF loader, model shader, ASSETS_DIR, control-state machine)
- [x] Phase 0.5 — World environment (day/night cycle, sky bodies, water light, fog banks)
- [x] Phase 1 — Islands / terrain + boat collision
- [ ] Phase 2 — First-person on-foot + E mount/unmount
- [ ] Phase 3 — Town: buildings, NPCs, NPC boats, dialogue stub
- [ ] Phase 4 — Fishing mechanics (no economy)
- [ ] Phase 5 — Aberrated creatures + chromatic aberration
