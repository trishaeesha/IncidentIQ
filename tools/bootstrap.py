"""Prepare a local IncidentIQ environment from VS Code."""
from __future__ import annotations
import argparse
import os
import subprocess
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"
REQ = ROOT / "requirements.txt"
REQ_NLP = ROOT / "requirements-nlp.txt"

def run(*args: str) -> None:
    subprocess.check_call(list(args), cwd=ROOT)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nlp", action="store_true", help="also install optional NLP/NLI dependencies")
    args = parser.parse_args()

    if not VENV.exists():
        print("Creating IncidentIQ virtual environment...")
        venv.create(VENV, with_pip=True)

    python = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        raise SystemExit("Could not create .venv. Install Python 3.11+ and retry.")

    print("Installing core dependencies...")
    run(str(python), "-m", "pip", "install", "--upgrade", "pip")
    run(str(python), "-m", "pip", "install", "-r", str(REQ))

    if args.nlp:
        print("Installing optional NLP/NLI dependencies...")
        run(str(python), "-m", "pip", "install", "-r", str(REQ_NLP))

    print()
    print("IncidentIQ environment is ready.")
    print(f"Python: {python}")
    if args.nlp:
        print("NLP/NLI dependencies: installed")
    else:
        print("NLP/NLI dependencies: optional; use --nlp when needed")
    print("Next: run the IncidentIQ: Test task, then the IncidentIQ: Run task or press F5.")

if __name__ == "__main__":
    main()
