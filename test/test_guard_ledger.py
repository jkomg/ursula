"""bin/guard-ledger: the only command allowed to name the ledger is a plain verifier call."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAR = "URSULA_" + "LEDGER"            # assembled: the live guard denies shell text naming it


def decide(command=None, **tool_input):
    led = os.path.join(tempfile.gettempdir(), "ursula-" + "ledger", "ledger.jsonl")
    if command is not None:
        tool_input["command"] = command.replace("{LEDGER}", led)
    env = dict(os.environ, **{VAR: led})
    out = subprocess.run([sys.executable, str(ROOT / "bin/guard-ledger")], input=json.dumps(
        {"tool_name": "Bash", "tool_input": tool_input}), capture_output=True, text=True, env=env)
    return "deny" if '"deny"' in out.stdout else "allow"


class GuardLedger(unittest.TestCase):
    def test_plain_verifier_call_may_name_the_ledger(self):
        self.assertEqual(decide("bash bin/run-hook --python scripts/session_verify.py r.json --ledger {LEDGER} --since x"), "allow")

    def test_chaining_after_a_verifier_is_denied(self):
        self.assertEqual(decide("bash bin/run-hook --python scripts/session_verify.py r.json --ledger {LEDGER}; rm {LEDGER}"), "deny")
        self.assertEqual(decide("python scripts/checkin_close.py r.json f --ledger {LEDGER} > {LEDGER}"), "deny")

    def test_reaching_it_through_the_variable_is_denied(self):
        self.assertEqual(decide("python -c \"import os; open(os.environ['" + VAR + "'], 'a')\""), "deny")

    def test_writing_to_it_is_denied(self):
        led = os.path.join(tempfile.gettempdir(), "ursula-" + "ledger", "ledger.jsonl")
        self.assertEqual(decide(file_path=led, content="x"), "deny")

    def test_look_alike_verifier_path_is_denied(self):
        self.assertEqual(decide("python /tmp/scripts/session_verify.py r.json --ledger {LEDGER}"), "deny")

    def test_unrelated_commands_are_allowed(self):
        self.assertEqual(decide("git status"), "allow")


if __name__ == "__main__":
    unittest.main()
