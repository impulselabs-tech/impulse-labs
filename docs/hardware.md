# Hardware

## Minimum

Isaac Sim's published floor is 8 GB of VRAM, and the preflight refuses to
report a machine ready below it. That floor is for the simulator itself; it
says nothing about how many environments will fit.

## Environment count and memory

`--num-envs` is the main lever on both memory and throughput. The default is
8,192 for a real run and 32 for `--smoke`. Memory grows roughly linearly with
the count, while the per-step cost per environment falls as the GPU fills, so
the largest count that fits is usually also the fastest per sample.

The count is not free to change for convenience: it sets the batch together
with 24 steps per environment and four minibatches, and the reward scales in
this package were tuned at 8,192. A run at 1,024 is a different optimization
problem, not a smaller version of the same one.

## Run length

The default schedule is 4,000 imitation iterations followed by 100,000 soccer
iterations. This is a multi-day run on a single GPU. `--plan` prints both
stage commands without importing Isaac Sim, which is the cheapest way to see
exactly what a run will execute before committing the machine to it.

## Disk

Checkpoints are written every 1,000 iterations and kept, so the soccer stage
leaves a hundred of them. Budget for the full sequence rather than for one
file, and prune deliberately: stage two resolves stage one's checkpoint by
directory, and deleting the wrong one breaks a resume.

## CPU and RAM

Physics stepping is on the GPU; the host mostly feeds it. Host RAM matters at
startup, when assets and all reference clips are loaded before the first
iteration, rather than during training.
