# FIELD Soccer Trainer

Two-stage humanoid soccer training: motion imitation followed by ball-kicking
training. Uses Isaac Sim 4.5.0, Isaac Lab v2.1.1, Python 3.10 and CUDA PyTorch.

## Contents

- `source/`: robot assets, simulation tasks, rewards and PPO configuration.
- `motions/`: reference motion data.
- `scripts/rsl_rl/`: training and policy playback entry points.
- `original_training/`: installation, preflight and two-stage launcher.
- `shell/`: original progressive training shell entry point.

No web panel, existing experiment history or trained weights are included.

## Windows

Provide a Python 3.10 executable; the installer creates a separate environment.
Installation downloads Isaac Sim and its dependencies. First launch presents a
license agreement to accept. The host must support the installed CUDA build.

```powershell
.\original_training\setup.ps1 -Python310 C:\Python310\python.exe
$trainerPython = '.\original_training\runtime\env\Scripts\python.exe'
& $trainerPython .\original_training\run.py --check
& $trainerPython .\original_training\run.py --smoke
& $trainerPython .\original_training\run.py
```

For an existing Isaac Lab v2.1.1 environment on Linux:

```bash
python -m pip install -e source/whole_body_tracking
python original_training/run.py --check
python original_training/run.py --smoke
python original_training/run.py
```

Installation reference:
https://isaac-sim.github.io/IsaacLab/v2.1.1/source/setup/installation/pip_installation.html

## Training

The default run uses 8,192 environments: 4,000 motion-imitation iterations, then
100,000 soccer iterations, resuming the first-stage training checkpoint.
`--num-envs N` changes training batch scale. `--smoke` runs two iterations per
stage with 32 environments to check execution; it does not establish learning.
`--plan` prints commands without requiring Isaac Sim.

Checkpoints and TensorBoard events: `logs/rsl_rl/g1_flat/`.
Stage commands/status: `original_training/runs/`.
Source and asset hashes: `FILE_HASHES.json` (independent of this repository's Git history).

This package has passed packaging and launcher checks only. GPU training and
convergence have not been validated. The simulation pipeline is included; no
sim-to-real domain-randomization component is.
