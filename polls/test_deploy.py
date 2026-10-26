"""Exercise deployment commands with an isolated database and minimal PATH."""

import ast
import os
from pathlib import Path
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile

from django.test import SimpleTestCase


class DeploymentCommandTests(SimpleTestCase):
    def test_deployment_commands_use_app_runtime_and_create_poll(self):
        root = Path(__file__).resolve().parent.parent
        commands = [
            ast.literal_eval(line.split("command:", 1)[1].strip())
            for line in (root / ".ebextensions/django.config").read_text().splitlines()
            if line.strip().startswith("command:")
        ]
        activation = shlex.quote(str(Path(sys.executable).parent / "activate"))
        with tempfile.TemporaryDirectory() as folder:
            stage = Path(folder)
            shutil.copy(root / "manage.py", stage)
            for package in ("mysite", "polls"):
                shutil.copytree(
                    root / package,
                    stage / package,
                    ignore=shutil.ignore_patterns("__pycache__"),
                )
            env = os.environ.copy()
            env.update(
                PATH="/usr/bin:/bin",
                DJANGO_DEBUG="true",
                DATABASE_URL=f"sqlite:///{stage}/test.sqlite3",
            )
            for command in commands:
                # Substitute EB's runtime location with the local installed environment.
                command = command.replace("/var/app/venv/*/bin/activate", activation)
                result = subprocess.run(
                    ["/bin/bash", "-c", command],
                    cwd=stage,
                    env=env,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((stage / "staticfiles/polls/style.css").exists())
            with sqlite3.connect(stage / "test.sqlite3") as connection:
                self.assertEqual(
                    connection.execute(
                        "SELECT COUNT(*) FROM polls_question"
                    ).fetchone()[0],
                    1,
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM polls_choice").fetchone()[
                        0
                    ],
                    3,
                )
