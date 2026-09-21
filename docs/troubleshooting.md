# Troubleshooting

Run the preflight first; it reports interpreter, package versions and GPU in
one pass instead of failing halfway into a launch:

```bash
python original_training/run.py --check
```

## Installation

**`Python 3.10 required`** — Isaac Sim 4.5 does not run on 3.11 or later. The
Windows installer builds its own environment; point it at a 3.10 interpreter
with `-Python310`.

**`isaaclab: expected 0.41.3, found ...`** — the environment is not at the
v2.1.1 tag. Mixing an Isaac Lab version against these task configurations
fails late, inside manager construction, with an error that names a term
rather than the version.

**`Missing CUDA PyTorch` / `CUDA PyTorch cannot access a GPU`** — a CPU wheel
was installed over the CUDA one, which pip will do quietly when another
dependency pins `torch`. Reinstall the CUDA build after the rest of the
environment is in place.

## Startup

**`Training source or asset changed: <path>`** — a tracked file differs from
its recorded hash. Restore it, or regenerate `FILE_HASHES.json` deliberately
if the change was intended.

**Stage two aborts with `Stage one did not produce an unambiguous training
checkpoint`** — either stage one failed before its first save at iteration
1,000, or several run directories match the same name. Clear the stale ones.

**First launch hangs for several minutes** — Isaac Sim compiles shaders and
populates its cache on first run. This is once per machine, not once per run.

## Training

**Out of memory** — lower `--num-envs`. Memory scales with the environment
count; the batch shape changes with it, so reward behaviour at 2,048
environments is not the behaviour at 8,192.

**Episode length pinned at the minimum** — the robot falls immediately. Check
the clip in replay before suspecting the reward terms.

**Ball never moves** — contact is never detected. A kick is only counted when
contact coincides with the foot moving into the ball, so a policy that
shuffles into the ball scores nothing; confirm in playback that the foot
swings.

**Throughput far below expectation** — confirm the run is headless and that
the logger is `tensorboard`. Rendering 8,192 environments to a window costs
more than the training step.

## Smoke run

```bash
python original_training/run.py --smoke
```

Two iterations per stage with 32 environments. It proves the pipeline
executes end to end. It does not establish that anything is learned, and a
clean smoke run says nothing about convergence.
