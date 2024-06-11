from datetime import timedelta
from django.db import models
from django.utils import timezone
from simple_history.manager import HistoryManager, HistoricalQuerySet
from simple_history.models import HistoricalRecords


# class HistoryQuestionManager(HistoryManager):
#     def published(self):
#         return self.filter(pub_date__lte=timezone.now())


# class HistoryQuestionQuerySet(HistoricalQuerySet):
#     def question_prefixed(self):
#         return self.filter(question__startswith="Question: ")


# class Question(models.Model):
#     pub_date = models.DateTimeField("date published")
#     history = HistoricalRecords(
#         history_manager=HistoryQuestionManager,
#         historical_queryset=HistoryQuestionQuerySet,
#     )