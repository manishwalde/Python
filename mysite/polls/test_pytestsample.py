import datetime
import pytest
from polls.views import IndexView
from polls.views import DetailView
import mysite.settings
from mixer.backend.django import mixer
from polls.models import Question
from django.utils import timezone
from django.test import RequestFactory
from django.urls import reverse, resolve
from django.test import TestCase
from django.http import HttpResponse


class TestUrls:

    def test_index_url(self):
        path = reverse('polls:index')
        assert resolve(path).view_name == 'polls:index'

    def test_detail_url(self):
        path = reverse('polls:detail', kwargs={'pk': 1})
        assert resolve(path).view_name == 'polls:detail'

    def test_results_url(self):
        path = reverse('polls:results', kwargs={'pk': 1})
        assert resolve(path).view_name == 'polls:results'


@pytest.mark.django_db
class TestQuestionModel:

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for question whose
        Pub_date is olded than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        # old_question = mixer.blend('polls.Question', pub_date=time)
        old_question = Question(pub_date=time)
        assert old_question.was_published_recently() == False

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for question whose
        pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        assert future_question.was_published_recently() == False

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() return True for question whose
        Pub_date is within the last day
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        assert recent_question.was_published_recently() == True


def create_question(question_text, days):
    """
    Create a question with the given 'question_text' and published the
    given number of 'days' offset to now (negative for questions published
    in the past, positive for question that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


@pytest.mark.django_db
class TestQuestionIndexView(TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     super(TestQuestionIndexView, cls).setUpClass
    #     cls.factory = RequestFactory()

    def test_no_question(self):
        """
        If no question exists, an appropriate message is displayed.
        """
        path = reverse('polls:index')
        print(path)
        request = RequestFactory().get(path)
        response = IndexView.as_view()(request).render()
        assert response.status_code == 200
        assert 'No polls are available.' in str(response)

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        path = reverse('polls:index')
        request = RequestFactory().get(path)
        create_question(question_text="Past question.", days=-30)
        response = IndexView.as_view()(request).render()
        assert response.status_code == 200
        assert 'Past question.' in str(response.content)

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        path = reverse('polls:index')
        request = RequestFactory().get(path)
        create_question(question_text="Future question.", days=30)
        response = IndexView.as_view()(request).render()
        assert response.status_code == 200
        assert 'No polls are available.' in str(response.content)

    def test_future_question_and_past_question(self):
        """
            Even if both past and future questions exist, only past questions
            are displayed.
            """
        path = reverse('polls:index')
        request = RequestFactory().get(path)
        create_question(question_text='Future question.', days=30)
        create_question(question_text='Past question.', days=-30)
        response = IndexView.as_view()(request).render()
        assert response.status_code == 200
        assert 'Past question.' in str(response.content)

    def test_two_past_question(self):
        """
        The questions index page may display multiple questions.
        """
        path = reverse('polls:index')
        request = RequestFactory().get(path)
        create_question(question_text='Past question 1.', days=-30)
        create_question(question_text='Past question 2.', days=-2)
        response = IndexView.as_view()(request).render()
        assert response.status_code == 200
        assert 'Past question 1.' in str(response.content)
        assert 'Past question 2.' in str(response.content)


# class QuestionDetailViewTests(TestCase):
    # def test_future_question(self):
    #     """
    #     The detail view of a question with a pub_date in the future
    #     returns a 404 not found.
    #     """
    #     future_question = create_question(
    #         question_text='Future question.', days=5)
    #     # path = reverse('polls:index', kwargs={'pk': 1})
    #     path = reverse('polls:detail', kwargs={'pk': future_question.id})
    #     request = RequestFactory().get(path)
    #     print('------------path-------------'+str(request))
    #     # url = reverse('polls:detail', args=(future_question.id,))
    #     response = DetailView.as_view()(
    #         request, pk=future_question.id).render()
    #     assert response.status_code == 404

    # def test_past_question(self):
    #     """
    #     The detail view of a question with a pub_date in the past
    #     displays the question's text.
    #     """
    #     past_question = create_question(
    #         question_text='Past Question.', days=-5)
    #     url = reverse('polls:detail', args=(past_question.id,))
    #     response = self.client.get(url)
    #     self.assertContains(response, past_question.question_text)
