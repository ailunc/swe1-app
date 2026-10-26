from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from polls.models import Question


class Command(BaseCommand):
    help = "Create one example poll without resetting existing votes."

    @transaction.atomic
    def handle(self, *args, **options):
        question, created = Question.objects.get_or_create(
            question_text="What helps you learn a new programming concept?",
            defaults={"pub_date": timezone.now()},
        )
        for text in (
            "Building a small project",
            "Reading the documentation",
            "Discussing it with classmates",
        ):
            question.choice_set.get_or_create(choice_text=text)
        self.stdout.write(
            self.style.SUCCESS(
                "Example poll created."
                if created
                else "Example poll already exists; votes preserved."
            )
        )
