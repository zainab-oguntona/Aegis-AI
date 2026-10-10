import uuid

from django.db import models


class Transaction(models.Model):
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="transactions")
    transaction_id = models.CharField(max_length=128)
    user_token = models.CharField(max_length=128)
    recipient_token = models.CharField(max_length=128, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("client", "transaction_id"), name="unique_client_transaction")]


class RiskAssessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="assessments")
    enabled_modules = models.JSONField(default=list)
    risk_score = models.PositiveSmallIntegerField()
    risk_level = models.CharField(max_length=10)
    decision = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)
    idempotency_key = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("transaction", "idempotency_key"), name="unique_transaction_idempotency")]


class RiskSignal(models.Model):
    assessment = models.ForeignKey(RiskAssessment, on_delete=models.CASCADE, related_name="signals")
    code = models.CharField(max_length=80)
    source = models.CharField(max_length=40)
    score = models.PositiveSmallIntegerField()
    severity = models.CharField(max_length=10)
    confidence = models.DecimalField(max_digits=4, decimal_places=3, default=1)
    description = models.CharField(max_length=255)
