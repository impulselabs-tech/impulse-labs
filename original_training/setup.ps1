param([string]$Python310 = "python3.10")
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$runtime = Join-Path $PSScriptRoot "runtime"
function Invoke-Checked([string]$Exe, [string[]]$Arguments) {
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Exe failed with exit code $LASTEXITCODE" }
}
# Separate interpreter and dependencies: the current CPU demo stays usable.
Invoke-Checked $Python310 @('-c', 'import sys; assert sys.version_info[:2] == (3, 10), "Python 3.10 required"')
New-Item -ItemType Directory -Force -Path $runtime | Out-Null
$envPath = Join-Path $runtime 'env'
if (-not (Test-Path "$envPath/Scripts/python.exe")) {
    Invoke-Checked $Python310 @('-m', 'venv', $envPath)
}
$python = Join-Path $envPath 'Scripts/python.exe'
Invoke-Checked $python @('-m', 'pip', 'install', '--upgrade', 'pip')
Invoke-Checked $python @('-m', 'pip', 'install', 'torch==2.7.0', 'torchvision==0.22.0', '--index-url', 'https://download.pytorch.org/whl/cu128')
Invoke-Checked $python @('-m', 'pip', 'install', 'isaacsim[all,extscache]==4.5.0', '--extra-index-url', 'https://pypi.nvidia.com')
$lab = Join-Path $runtime 'IsaacLab'
if (-not (Test-Path $lab)) {
    Invoke-Checked 'git' @('clone', '--branch', 'v2.1.1', '--depth', '1', 'https://github.com/isaac-sim/IsaacLab.git', $lab)
}
Invoke-Checked 'git' @('-C', $lab, 'diff', '--exit-code', 'v2.1.1', '--', 'source')
$env:VIRTUAL_ENV = $envPath
$env:PATH = "$envPath\Scripts;$env:PATH"
Invoke-Checked (Join-Path $lab 'isaaclab.bat') @('--install', 'rsl_rl')
Invoke-Checked $python @('-m', 'pip', 'install', '-e', (Join-Path $root 'source/whole_body_tracking'))
Invoke-Checked $python @('-m', 'pip', 'check')
Invoke-Checked $python @((Join-Path $PSScriptRoot 'run.py'), '--check')
