# Motion data

Reference clips live in `motions/` as `.npz` files. `motions/soccer-standard`
holds ten kicks used by the default run; `motions/soccer-stylized` holds three
with a wider swing, kept separate so the two sets can be trained against
independently.

## File layout

Every clip is a flat `.npz` with one entry per array:

| Key | Shape | Meaning |
| --- | --- | --- |
| `fps` | `(1,)` | Sampling rate of the clip |
| `joint_pos` | `(T, 29)` | Joint positions, radians |
| `joint_vel` | `(T, 29)` | Joint velocities, radians per second |
| `body_pos_w` | `(T, 30, 3)` | Body positions in the world frame |
| `body_quat_w` | `(T, 30, 4)` | Body orientations, `(w, x, y, z)` |
| `body_lin_vel_w` | `(T, 30, 3)` | Body linear velocities |
| `body_ang_vel_w` | `(T, 30, 3)` | Body angular velocities |
| `kick_leg` | scalar string | `left` or `right`, optional |

Joint order follows the articulation in `soccer/robots/g1.py`; body order
follows the links in the URDF. A clip written against a different joint order
will load without error and train against nonsense, so regenerate rather than
reorder by hand.

Velocities are stored rather than differentiated at load time: the loader
reads them directly, and a clip whose velocities disagree with its positions
will produce tracking rewards that cannot be satisfied.

## Converting capture data

`scripts/csv_to_npz.py` replays a CSV clip in the simulator and writes the npz,
resampling from the input rate to the output rate:

```bash
python scripts/csv_to_npz.py --input_file capture/kick01.csv --input_fps 30 \
    --frame_range 122 722 --output_file motions/soccer-standard/kick01.npz --output_fps 50
```

`scripts/pkl_to_npz.py` does the same for pickled capture, reusing the CSV
loader. `--frame_range` is not available there; trim the clip beforehand.

## Labelling the striking foot

`scripts/kick_motion_label.py` adds the `kick_leg` entry and writes a new file
with a `_left` or `_right` suffix, leaving the original untouched:

```bash
python scripts/kick_motion_label.py motions/soccer-standard --label left
```

The loader reads only the state arrays, so an unlabelled clip still trains;
the label exists for selecting clips and for reading the set at a glance.

## Checking a clip

`scripts/replay_npz.py` plays a clip back on the articulation with no policy
involved. A clip that looks wrong in replay will not be rescued by training.

```bash
python scripts/replay_npz.py --motion_file motions/soccer-standard/soccer-standard-001_right.npz
```
