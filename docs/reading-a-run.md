# Reading a run

Checkpoints and TensorBoard events land in `logs/rsl_rl/g1_flat/<timestamp>_<run>/`.
Stage commands and their exit status land in `original_training/runs/<run>/manifest.json`,
written before each stage starts and updated when it ends, so an interrupted
run still says how far it got.

```bash
tensorboard --logdir logs/rsl_rl/g1_flat
```

## What the curves mean

**Total reward** rising says little on its own in stage two, where the
imitation prior and the ball terms are summed. Read the terms separately.

**Imitation terms** (`anchor_position`, `body_position`, `body_orientation`,
velocity terms) should climb in stage one and then hold roughly flat in stage
two. A collapse after the switch means the ball rewards are outcompeting the
posture prior and the robot is learning to fall into the ball.

**Ball terms** (`ball_speed`, direction alignment) only become meaningful once
contact happens at all. Before that they sit near zero and carry no gradient
worth reading.

**Vertical ball speed penalty** rising while ball speed rises means the robot
is scooping the ball upward rather than driving it forward.

**Episode length** is the fastest signal of a broken configuration: if it
stays at the termination floor, the robot is falling immediately and no
reward term is being sampled long enough to matter.

**Mean noise std** falling to near zero early means the policy stopped
exploring; with the adaptive learning rate this usually follows a KL target
that is too tight for the batch size.

## Checkpoints

Written every 1,000 iterations as `model_<iteration>.pt`. Stage two resolves
stage one's directory by run name and refuses to start if it finds zero or
more than one match, rather than silently picking one.

## Playing a checkpoint

```bash
python scripts/rsl_rl/play_multi.py --task Tracking-Flat-G1-SoccerMoving-RNN-v0 \
    --motion_path motions/soccer-standard --load_run <run> --num_envs 16
```

Playback is where a policy that trained to a high reward but kicks in the
wrong direction becomes obvious; the reward curve will not tell you that.
