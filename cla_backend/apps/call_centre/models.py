from django.db import models
from model_utils.models import TimeStampedModel


class Operator(TimeStampedModel):
    user = models.OneToOneField('auth.User')
    is_operator_superuser = models.BooleanField(default=False)