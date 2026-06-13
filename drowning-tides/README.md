# Drowning Tides

A deep-sea ocean fishing game with low-poly 3D and a dark, painted maritime
impressionism aesthetic — cozy maritime scenery with a creeping cosmic-horror mood.
Built with `pygame + moderngl + PyGLM + numpy`, managed with `uv`.

## Admin / console commands

Press `` ` `` (backtick) to toggle the dev console at the bottom of the window. Type
a command and press `Enter`. Press `` ` `` again or `Esc` to close it.

| Command       | Effect                                                        |
| ------------- | ------------------------------------------------------------- |
| `/storm-on`   | Rolls a storm in (random peak intensity), overriding the weather scheduler. |
| `/storm-kill` | Rapidly clears the current storm back to calm.                |

While the console is open, boat controls are disabled so typing doesn't steer.

## Running the game

Requires [`uv`](https://docs.astral.sh/uv/).

```
cd drowning-tides
uv run python main.py
```

(Or, via the installed entry point, `uv run drowning-tides`.)

`uv` resolves and installs dependencies from `pyproject.toml` automatically on the
first run.

## Project layout

Source lives under `src/drowning_tides/` as an installable package:

| Package  | Contents                                               |
| -------- | ------------------------------------------------------ |
| `config` | `settings.py` — all tuning constants                   |
| `core`   | GL infrastructure: `mesh`, `shader_program`            |
| `render` | `scene`, `camera`, `sky`, `water`, `rain`              |
| `world`  | simulation: `boat`, `waves`, `weather`                 |
| `ui`     | `console`                                              |
| `shaders`| GLSL `.vert` / `.frag` pairs                           |

Run the tests with `uv run pytest` and lint with `uv run ruff check`.

## Controls

| Key       | Action                          |
| --------- | ------------------------------- |
| `W` / `S` | Throttle forward / reverse      |
| `A` / `D` | Steer left / right              |
| `` ` ``   | Toggle dev console              |
| `Esc`     | Quit (or close the console)     |

## Weather

A single `storm_intensity` (0–1) drives the wind, waves, rain, and mood lighting
together. Storms roll in on their own at random intervals with a random peak each
time, building and clearing like real weather. Wind has a slowly wandering direction
that sets the wave travel, slants the rain, and pushes the boat as a current. The
boat is rocked and shoved by the sea but is clamped so it can never capsize.

Tuning knobs live in `settings.py` — wave size (`WAVE_STORM_AMP`,
`WAVE_MAX_AMPLITUDE`), current strength (`CURRENT_PUSH`), wind (`WIND_*`), rain
(`RAIN_*`), boat tilt limit (`BOAT_MAX_TILT`), the calm↔storm colour presets
(`*_STORM`), and the weather scheduler timings (`WEATHER_*`).
