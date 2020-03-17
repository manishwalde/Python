import datetime
import pytest
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
        path = reverse('polls:detail', kwargs={'pk': 1})
        request = RequestFactory().get(path)
        obj = DetailView()
        response = HttpResponse(obj.get_queryset())
        assert response.status_code == 200
