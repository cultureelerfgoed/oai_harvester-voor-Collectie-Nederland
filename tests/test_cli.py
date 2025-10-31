import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "oai_harvester.py"

def run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)

def test_script_exists():
    assert SCRIPT.exists(), "oai_harvester.py ontbreekt"

def test_import_module():
    # Import test zonder side effects
    code = "import importlib.util, sys, pathlib; p=str(pathlib.Path('oai_harvester.py')); spec=importlib.util.spec_from_file_location('oai_harvester', p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('OK')"
    out = run([sys.executable, "-c", code]).stdout
    assert "OK" in out

def test_help_output():
    # --help mag nooit netwerken en moet exitcode 0 geven
    out = run([sys.executable, str(SCRIPT), "--help"]).stdout.lower()
    # Een paar herkenbare woorden
    assert "usage" in out or "gebruik" in out
    assert "--url" in out
    assert "--verb" in out
    assert "--prefix" in out
