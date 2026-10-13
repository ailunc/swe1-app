import os
from pathlib import Path
import subprocess
import sys
from io import StringIO

from django.core.management import call_command, get_commands
from django.test import SimpleTestCase, TestCase

from .models import Question


class SeedTests(TestCase):
    def test_seed_can_be_repeated_without_resetting_votes(self):
        self.assertIn('seed_polls', get_commands())
        call_command('seed_polls', stdout=StringIO())
        self.assertEqual(Question.objects.count(), 1)
        question = Question.objects.get()
        self.assertEqual(question.choice_set.count(), 3)
        choice = question.choice_set.first()
        choice.votes = 7
        choice.save()
        call_command('seed_polls', stdout=StringIO())
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(question.choice_set.count(), 3)
        choice.refresh_from_db()
        self.assertEqual(choice.votes, 7)


class ProductionSettingsTests(SimpleTestCase):
    def run_check(self, **values):
        env = os.environ.copy()
        for key in ('DJANGO_DEBUG', 'DJANGO_SECRET_KEY', 'DATABASE_URL', 'RDS_HOSTNAME'):
            env.pop(key, None)
        env.update(values)
        return subprocess.run(
            [sys.executable, 'manage.py', 'check'],
            cwd=Path(__file__).resolve().parent.parent,
            env=env, text=True, capture_output=True,
        )

    def test_production_requires_a_secret(self):
        result = self.run_check(DJANGO_DEBUG='false')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DJANGO_SECRET_KEY', result.stderr)

    def test_production_settings_accept_external_configuration(self):
        result = self.run_check(
            DJANGO_DEBUG='false', DJANGO_SECRET_KEY='test-only-' + 'x' * 60,
            DJANGO_ALLOWED_HOSTS='app.example.com',
            DATABASE_URL='postgresql://user:password@localhost:5432/polls',
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_requires_a_database(self):
        result = self.run_check(DJANGO_DEBUG='false', DJANGO_SECRET_KEY='test-only-' + 'x' * 60)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DATABASE_URL', result.stderr)
