import datetime

from django.test import Client, TestCase
from django.utils import timezone

from .models import Question


class PollIndexTests(TestCase):
    def test_empty_index_is_a_working_page(self):
        response = self.client.get('/polls/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')

    def test_latest_five_questions_have_detail_links(self):
        now = timezone.now()
        for days in range(6):
            Question.objects.create(question_text=f'Question {days}', pub_date=now - datetime.timedelta(days=days))
        response = self.client.get('/polls/')
        self.assertContains(response, 'Question 0')
        self.assertContains(response, 'Question 4')
        self.assertNotContains(response, 'Question 5')
        latest = Question.objects.get(question_text='Question 0')
        self.assertContains(response, f'href="/polls/{latest.pk}/"')

    def test_root_redirects_to_polls(self):
        self.assertRedirects(self.client.get('/'), '/polls/')


class VotingTests(TestCase):
    def setUp(self):
        self.question = Question.objects.create(question_text='How do you study?', pub_date=timezone.now())
        self.choice = self.question.choice_set.create(choice_text='Practice', votes=2)
        self.other_choice = self.question.choice_set.create(choice_text='Read', votes=0)
        self.detail_url = f'/polls/{self.question.pk}/'
        self.vote_url = f'/polls/{self.question.pk}/vote/'
        self.results_url = f'/polls/{self.question.pk}/results/'

    def test_detail_displays_question_choices_and_post_form(self):
        response = self.client.get(self.detail_url)
        self.assertContains(response, 'How do you study?')
        self.assertContains(response, 'Practice')
        self.assertContains(response, 'Read')
        self.assertContains(response, f'action="{self.vote_url}"')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_vote_increments_only_selected_choice_and_redirects(self):
        response = self.client.post(self.vote_url, {'choice': self.choice.pk})
        self.assertRedirects(response, self.results_url)
        self.choice.refresh_from_db()
        self.other_choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 3)
        self.assertEqual(self.other_choice.votes, 0)

    def test_results_show_saved_votes(self):
        self.assertContains(self.client.get(self.results_url), 'Practice — 2 votes')

    def test_missing_choice_does_not_vote(self):
        response = self.client.post(self.vote_url, {})
        self.assertContains(response, "You didn&#x27;t select a choice.")
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 2)

    def test_invalid_choice_does_not_vote(self):
        for value in ('not-a-number', 99999):
            with self.subTest(value=value):
                response = self.client.post(self.vote_url, {'choice': value})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'role="alert"')
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 2)

    def test_choice_from_another_question_cannot_receive_vote(self):
        another = Question.objects.create(question_text='Another poll', pub_date=timezone.now())
        foreign_choice = another.choice_set.create(choice_text='Wrong poll')
        response = self.client.post(self.vote_url, {'choice': foreign_choice.pk})
        self.assertEqual(response.status_code, 200)
        foreign_choice.refresh_from_db()
        self.assertEqual(foreign_choice.votes, 0)

    def test_get_cannot_record_vote(self):
        response = self.client.get(self.vote_url, {'choice': self.choice.pk})
        self.assertEqual(response.status_code, 405)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 2)

    def test_csrf_token_is_required(self):
        response = Client(enforce_csrf_checks=True).post(self.vote_url, {'choice': self.choice.pk})
        self.assertEqual(response.status_code, 403)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 2)

    def test_nonexistent_question_returns_404(self):
        for suffix in ('', 'results/', 'vote/'):
            with self.subTest(suffix=suffix):
                request = self.client.post if suffix == 'vote/' else self.client.get
                response = request(f'/polls/99999/{suffix}')
                self.assertEqual(response.status_code, 404)


class QuestionModelTests(TestCase):
    def test_recent_publication_excludes_old_and_future_dates(self):
        self.assertTrue(hasattr(Question, 'was_published_recently'))
        now = timezone.now()
        for offset, expected in ((-2, False), (-0.5, True), (1, False)):
            with self.subTest(offset=offset):
                question = Question(pub_date=now + datetime.timedelta(days=offset))
                self.assertEqual(question.was_published_recently(), expected)
