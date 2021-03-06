from jsonfield import JSONField
from uuidfield import UUIDField
from model_utils.models import TimeStampedModel

from django.db import models

from cla_common.constants import DIAGNOSIS_SCOPE


class DiagnosisTraversalManager(models.Manager):
    def create_eligible(self, category):
        return self.create(
            state=DIAGNOSIS_SCOPE.INSCOPE,
            category=category,
            nodes=[{
                "title": category.name,
                "label": "<p>Diagnosis created by Specialist.</p>"
            }]
        )


class DiagnosisTraversal(TimeStampedModel):
    reference = UUIDField(auto=True, unique=True)
    nodes = JSONField(null=True, blank=True)
    current_node_id = models.CharField(blank=True, max_length=50)
    graph_version = models.CharField(blank=True, max_length=50)

    state = models.CharField(blank=True, null=True, max_length=50, default=DIAGNOSIS_SCOPE.UNKNOWN)
    category = models.ForeignKey('legalaid.Category', null=True, blank=True)

    objects = DiagnosisTraversalManager()

    def is_state_inscope(self):
        return self.state == DIAGNOSIS_SCOPE.INSCOPE

    def is_state_outofscope(self):
        return self.state == DIAGNOSIS_SCOPE.OUTOFSCOPE

    def is_state_unknown(self):
        return self.state == DIAGNOSIS_SCOPE.UNKNOWN
