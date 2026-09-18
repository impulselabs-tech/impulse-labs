# Training stages

Training runs in two stages. The second one starts from the checkpoint the
first one produced; running it from scratch gives a robot that kicks from a
posture it cannot hold.

## Stage one — motion imitation

Task: `Tracking-Terrain-G1-RNN-v0`

The policy is rewarded for reproducing a reference clip: anchor position and
orientation, per-body position and orientation relative to the anchor, and
linear and angular body velocities. Each term is an exponential of the error,
so the reward stays bounded and a single badly tracked body cannot dominate.

Ball rewards are absent here. The stage exists to produce a gait and a posture
that survive contact, not to score.

Default length: 4,000 iterations.

## Stage two — kicking

Task: `Tracking-Flat-G1-SoccerMoving-RNN-v0`

A ball is added to the scene and the imitation rewards stay on as a posture
prior, at lower weight. On top of them: ball speed, alignment of the ball's
velocity with the target direction, a penalty on vertical ball speed, and
proximity of the striking foot to the ball.

The stage resumes from stage one with `--load_run <run> --resume True`. The
launcher resolves the run directory itself and fails if stage one left no
unambiguous checkpoint.

Default length: 100,000 iterations.

## Policy and optimizer

Both stages use the same recurrent actor-critic:

| Setting | Value |
| --- | --- |
| Network | LSTM, 2 layers, hidden 128 |
| MLP head | 128 / 64 / 32, ELU |
| Steps per environment | 24 |
| Minibatches | 4 |
| Learning epochs | 5 |
| Learning rate | 1e-3, adaptive to a KL target of 0.01 |
| Discount / GAE lambda | 0.99 / 0.95 |
| Clip | 0.2 |
| Entropy coefficient | 0.005 |
| Observation normalization | empirical, running |

The adaptive schedule moves the learning rate to hold the measured KL near
0.01, so the printed rate changing during a run is expected.

## Environment count

The default is 8,192 environments. The number sets the batch size together
with the 24 steps per environment and the four minibatches, so changing it
changes the effective batch the reward scales were tuned against. Fewer than
four environments cannot fill the minibatches and the launcher refuses to
start.

## Other registered tasks

Beyond the two stages the launcher uses, the package registers flat and
terrain variants without the recurrent policy, a blind variant that drops
ball observations, a low-frequency control variant, and a distillation task
used to train a proprioception-only student.
