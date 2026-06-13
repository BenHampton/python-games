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
| `core`   | GL infrastructure: `mesh`, `shader_program`       |
| `render` | `scene`, `camera`, `sky`, `water`, `rain`         |
| `world`  | simulation: `boat`, `waves`, `weather`            |
| `ui`     | `console`                                          |
| `shaders`| GLSL `.vert`/`.frag` pairs, loaded by name         |

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
  matching, or the boat will desync from the water.

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

1. **Island / town** — first landmass with NPCs and NPC boats.
2. **Fishing mechanics** — the core catch loop.
3. **Aberrated creatures + chromatic aberration** — mutated fish/monsters and the
   matching post effect.
4. **On-deck first-person** — flesh out the stubbed `FIRST_PERSON` camera mode in
   `render/camera.py` so a character can walk the deck.
5. **More world content**, then **story + side-quests**.

## Dev console

Backtick (`` ` ``) toggles an in-game console. Commands live in `ui/console.py`'s
`commands` table — extend it there. Current: `/storm-on`, `/storm-kill`.
