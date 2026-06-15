# Drowning Tides

A deep-sea ocean fishing game with low-poly 3D and a dark, painted maritime
impressionism aesthetic — cozy maritime scenery with a creeping cosmic-horror mood.
Built with `pygame + moderngl + PyGLM + numpy`, managed with `uv`.

## Admin / console commands

Press `` ` `` (backtick) to toggle the dev console at the bottom of the window. Type
a command and press `Enter`. Press `` ` `` again or `Esc` to close it.

| Command            | Effect                                                                      |
| ------------------ | --------------------------------------------------------------------------- |
| `/storm-on`        | Rolls a storm in (random peak intensity), overriding the weather scheduler. |
| `/storm-kill`      | Rapidly clears the current storm back to calm.                              |
| `/fog-on`          | Rolls a fog bank in (random peak), overriding the fog scheduler.            |
| `/fog-kill`        | Rapidly clears the current fog bank.                                        |
| `/rain-on`         | Starts a rain event now (drizzle…downpour), independent of storms.          |
| `/rain-kill`       | Rapidly clears the current rain.                                            |
| `/time <0..1>`     | Jumps the day cycle to a phase (0 = midnight, 0.25 dawn, 0.5 noon, 0.75 dusk). |
| `/timescale <x>`   | Multiplies how fast the day advances (e.g. `/timescale 20` to fast-forward). |
| `/lightning`       | Triggers a lightning flash + bolt now.                                      |
| `/clouds <0..1>`   | Sets the cloud-cover target (0 clear … 1 full overcast).                    |

While the console is open, boat controls are disabled so typing doesn't steer.

> **Note:** All admin/dev-console commands live in `ui/console.py`'s `commands` table.
> Whenever that table changes, update this section to match.

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

| Key / Input | Action                                          |
| ----------- | ----------------------------------------------- |
| `W` / `S`   | Throttle fwd / reverse (at helm) · walk fwd / back (on foot) |
| `A` / `D`   | Steer left / right (at helm) · strafe (on foot) |
| `E`         | Board / disembark — only near land to step onto an island   |
| `F`         | Fish (at the helm over open water) · talk to a nearby NPC (on foot) |
| Mouse       | Orbit the camera (helm) · look around (on foot) |
| Scroll      | Zoom the camera in / out                        |
| `` ` ``     | Toggle dev console                              |
| `Esc`       | Pause / resume (opens the pause menu)           |
| `F11`       | Toggle fullscreen / windowed                    |
| Click       | Resume / Quit buttons (while paused)            |

The mouse is captured for camera look; it's released automatically while the dev console
is open, and recaptured when you close it.

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
