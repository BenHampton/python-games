# Drowning Tides

A low-poly 3D / painterly-2D maritime game in the spirit of *Dredge*: cozy fishing on
the surface, creeping cosmic-horror underneath. Canonical name is **Drowning Tides**
(the directory). Built with `pygame + moderngl + pyglm + numpy`, Python 3.10, `uv`.

## Aesthetic (the north star)

- **Low-poly 3D** world — simple shapes, few polygons, stylized.
- **Painterly, impressionistic 2D** — hard-edged opaque brush feel for UI/portraits.
- **Nautical horror** — muted, subdued palette, minimal gradients, dreamlike dread.
  Calm fishing balanced against deep unease.
- **Chromatic aberration** — *planned*, not yet implemented. The post pass
  (`src/drowning_tides/shaders/post.frag`) currently does a painterly smear + cool
  grade + vignette + canvas grain, but **no color-channel fringing yet**. Aberration is
  intended to sell the mutated "aberrated" creatures and reality-warping moments.

## Commands

```
uv run python main.py        # launch the game (or: uv run drowning-tides)
uv run pytest                # run tests
uv run ruff check src tests  # lint
```

`uv sync` installs deps (incl. the `dev` group: pytest, ruff).

## Architecture

Source is an installable package under `src/drowning_tides/`:

| Package  | Contents                                          |
| -------- | ------------------------------------------------- |
| `config` | `settings.py` — every tuning constant lives here  |
| `core`   | GL infra: `mesh`, `shader_program`, `model` (glTF loader), `meshbuilder`, `frustum` |
| `render` | `scene`, `camera`, `sky`, `water`, `rain` + bloom / god-ray / painterly post passes |
| `world`  | sim: `boat`, `waves`, `weather`, `daycycle`, `island`, `town`, `player`, `npc`/`npc_boats`, `game_state`, `fishing` |
| `ui`     | `console`, `hud`, `pause_menu`                     |
| `shaders`| GLSL `.vert`/`.frag` pairs, loaded by name         |
| `assets` | baked glTF models (`models/`), CC0 kits + `CREDITS.md`; `tools/gen_islands.py` bakes islands |

- **No ECS.** A single `Game` class in `app.py` composes everything and owns the
  fixed-order loop: `handle_events → update → render`. Subsystems take the `app` and
  read sibling state off it (`app.weather`, `app.camera`, `app.wave_field`, …).
- **Render pipeline:** world geometry → offscreen FBO → painterly post pass
  (fullscreen triangle) → crisp UI overlay (console) drawn last, after post.
- **Shaders** are loaded package-relative via `SHADERS_DIR` in `core/shader_program.py`
  — the game does not depend on the current working directory.

## Key invariants — don't break these

- **One `storm_intensity` (0–1) drives everything.** `world/weather.py` runs a
  calm→buildup→hold→ease scheduler that sets it; waves, rain, wind/current, and mood
  lighting all read from it. Add weather-driven effects by reading `storm_intensity`,
  not by inventing parallel state.
- **GPU/CPU wave parity.** The Gerstner wave field is evaluated *identically* on the GPU
  (`shaders/water.vert`) and the CPU (`world/waves.py::WaveField.sample`) so the boat
  floats on the visibly rendered sea. If you change one, change the other and keep them
  matching, or the boat will desync from the water. This parity **includes the
  distance-from-town shelter gain** — waves are calmer near the home-island harbor and
  rougher out to sea; `waves.py::shelter_gain` must mirror the gain block in `water.vert`
  (both keyed to `cfg.SHELTER_*`, centred on the town `cfg.SHELTER_CENTER`).
- **Home island is a symmetric circle with a flat town shelf.** `tools/gen_islands.py`
  builds the home (`freeport`) island as a clean radial circle: a flat shelf where the
  town/dock sit, with hills/mountain/rocks added *only outside* that strip. Terrain +
  foliage are **baked** to `assets/models/islands/<name>_lod{0,1}.glb` plus a
  `<name>_height.npz` heightmap — **re-run `gen_islands.py` after any island tuning**, and
  keep `cfg.HOME_LAND_FRAC` in sync with the profile's shelf height. `world/island.py::
  ground_y` bilinear-samples that heightmap so foliage/props/the player follow the surface.

## World: home island + harbor town

- **Home island** (`freeport`, `cfg.ISLANDS`, scale 98): radial circle with a flat coastal
  shelf to the south; a central **mountain + rolling hills + scattered rocks/boulders + a
  forest** elsewhere (all baked by `gen_islands.py`, seated on the terrain via a `height_at`
  lookup so nothing floats). Foliage/relief are **masked out of the town strip**.
- **Harbor town** (`world/town.py`): a **sealed walled courtyard** — buildings (CC0 Kenney
  Fantasy Town Kit, assembled from wall/roof modules and baked muted) packed edge-to-edge as
  three walls with **alley gaps plugged by colliding props** (fences/hedges/carts/crates).
  The opening faces the dock; a **wide grand wooden staircase → landing → pier** leads to the
  moored boat, with a lighthouse, jetties, dock shacks, rowboats and a wreck offshore
  (CC0 Pirate Kit). The well + market stalls sit centred in the courtyard.
- **On-foot movement** (`world/player.py`): `walk()` (pure) moves along the camera yaw, then
  the position is resolved against **town collision** (`Town.collide` /
  `resolve_town_collision`, AABB push-out) and seated on the ground via `Island.ground_y` or
  **walkable plank decks** (`Town.deck_height`: flat-deck rects + sloped ramps for the
  stairs/pier). The collider ring + water **seal the player to the dock + courtyard**.
- **Camera** (`render/camera.py`): `FOLLOW` (boat orbit) and `FIRST_PERSON` (on-foot) modes;
  mouse pitch sign is **mode-aware** (mouse-up tilts the view up in both).
- **Models / assets** (`core/model.py`): glTF loaded to baked flat per-vertex colours
  (`COLOR_0` → base-colour texture sampled per face → material factor). `Model(..., mute=)`
  desaturates toward the muted palette. CC0 Kenney kits (Watercraft, Nature, Pirate, Fantasy
  Town) live under `assets/models/`, credited in `assets/CREDITS.md`.

## Conventions

- **`src/` layout, package imports.** Import siblings by full path, e.g.
  `from drowning_tides.core.mesh import Mesh`.
- **Config via namespace, never `import *`.** Use
  `from drowning_tides.config import settings as cfg` and reference `cfg.NAME`. Wildcard
  imports are not allowed (PEP 8). All tunable numbers go in `config/settings.py`.
  *Future:* move tuning to a data-driven TOML config once values stabilize.
- **Tests** cover pure logic only (no GL context needed) — see `tests/test_waves.py`,
  `tests/test_weather.py`. Rendering classes need a live GL context and stay untested
  for now. Keep new game logic testable without a window.
- Keep code **ruff-clean** (`E,F,I,UP,B`), line length 100.

## Roadmap (build one feature at a time, iterate)

Open-world for now; a story and side-quests come later. Rough order:

1. **Island / town** — *largely built*: the `freeport` home island + sealed harbor town,
   walkable dock/courtyard, day/night, weather. NPCs/NPC-boats are stubbed; more polish + a
   second island later.
2. **Fishing mechanics** — the core catch loop (`world/fishing.py` stubbed).
3. **Aberrated creatures + chromatic aberration** — mutated fish/monsters and the
   matching post effect.
4. **On-deck first-person** — flesh out the stubbed `FIRST_PERSON` camera mode in
   `render/camera.py` so a character can walk the deck.
5. **More world content**, then **story + side-quests**.

## Dev console

Backtick (`` ` ``) toggles an in-game console. Commands live in `ui/console.py`'s
`commands` table — extend it there. Current: `/storm-on`, `/storm-kill`, `/fog-on`,
`/fog-kill`, `/time`, `/timescale`, `/lightning`, `/clouds`.

Other keys: `E` mount/dismount (dock when near land), `F` interact, `F11` fullscreen,
`Esc` pause menu, mouse-look + scroll-zoom.
