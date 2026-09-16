"""Launch the two training stages without replacing their training code."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
TASKS = ["Tracking-Terrain-G1-RNN-v0", "Tracking-Flat-G1-SoccerMoving-RNN-v0"]


def check():
    problems = []
    if sys.version_info[:2] != (3, 10):
        problems.append("Isaac Sim 4.5 requires a separate Python 3.10 environment.")
    # The v2.1.1 repository tag declares isaaclab extension/package 0.41.3.
    for package, version in [("isaacsim", "4.5.0"), ("isaaclab", "0.41.3")]:
        try:
            actual = importlib.metadata.version(package)
            if actual != version:
                problems.append(f"{package}: expected {version}, found {actual}")
        except importlib.metadata.PackageNotFoundError:
            problems.append(f"Missing {package}=={version}")
    try:
        import torch
        if not torch.cuda.is_available():
            problems.append("CUDA PyTorch cannot access a GPU.")
    except ImportError:
        problems.append("Missing CUDA PyTorch.")
    try:
        result = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"], text=True
        ).strip()
        print(result)
        if all(int(line.rsplit(",", 1)[1]) < 8192 for line in result.splitlines()):
            problems.append("GPU VRAM is below Isaac Sim's published 8 GB minimum.")
    except (OSError, ValueError, subprocess.CalledProcessError):
        problems.append("Cannot inspect NVIDIA GPU.")
    print(json.dumps({"ready": not problems, "problems": problems}, indent=2))
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--plan", action="store_true", help="Print commands without launching Isaac Sim")
    parser.add_argument("--smoke", action="store_true", help="Two updates per stage; validates execution, not learning")
    parser.add_argument("--num-envs", type=int, default=None)
    args = parser.parse_args()
    if args.check:
        return int(bool(check()))
    num_envs = args.num_envs or (32 if args.smoke else 8192)
    if num_envs < 4:
        parser.error("Use at least 4 environments for the original four minibatches.")
    name = ("original_smoke_" if args.smoke else "original_") + uuid.uuid4().hex[:12]
    commands = []
    for stage, task in enumerate(TASKS):
        command = [sys.executable, "scripts/rsl_rl/train_multi.py", "--task", task,
                   "--motion_path", "motions/soccer-standard", "--run_name", name,
                   "--num_envs", str(num_envs), "--headless", "--logger", "tensorboard"]
        if stage == 0 or args.smoke:
            command += ["--max_iterations", "2" if args.smoke else "4000"]
        if stage == 1:
            command += ["--load_run", "<stage-one-run>", "--resume", "True"]
        commands.append(command)
    if args.plan:
        print(json.dumps({"smoke": args.smoke, "commands": commands}, indent=2))
        return 0
    if check():
        return 1
    hashes = json.loads((ROOT / "FILE_HASHES.json").read_text(encoding="utf-8"))
    for relative, expected in hashes.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"Training source or asset changed: {relative}")
    artifacts = ROOT / "original_training" / "runs" / name
    artifacts.mkdir(parents=True, exist_ok=False)
    manifest = {"smoke": args.smoke, "num_envs": num_envs,
                "dashboard_connected": False, "stages": []}
    for stage, command in enumerate(commands):
        if stage == 1:
            runs = list((ROOT / "logs/rsl_rl/g1_flat").glob("*_" + name))
            if len(runs) != 1 or not list(runs[0].glob("model_*.pt")):
                raise RuntimeError("Stage one did not produce an unambiguous training checkpoint.")
            command[command.index("<stage-one-run>")] = runs[0].name
        record = {"task": TASKS[stage], "command": command, "status": "running"}
        manifest["stages"].append(record)
        report = artifacts / "manifest.json"
        report.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        # Offline local telemetry. No account or cloud logging is required.
        env = dict(os.environ, WANDB_MODE="offline")
        result = subprocess.run(command, cwd=ROOT, env=env)
        record.update(status="completed" if result.returncode == 0 else "failed", exit_code=result.returncode)
        report.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
