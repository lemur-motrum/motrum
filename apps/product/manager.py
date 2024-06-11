from datetime import timedelta
from django.db import models
from django.utils import timezone
from simple_history.manager import HistoryManager, HistoricalQuerySet
from simple_history.models import HistoricalRecords

class HistoryQuestionManager(HistoryManager):
    def published(self):
        return self.filter()


class HistoryQuestionQuerySet(HistoricalQuerySet):
    def question_prefixed(self):
        return self.filter()


class Product(models.Model):

    history = HistoricalRecords(
        history_manager=HistoryQuestionManager,
        historical_queryset=HistoryQuestionQuerySet,
    )
