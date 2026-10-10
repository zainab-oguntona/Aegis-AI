from decimal import Decimal

from rest_framework import serializers

from .models import RiskAssessment, RiskSignal


class RiskAssessmentRequestSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=128)
    user_token = serializers.CharField(max_length=128)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal("0.01"))
    currency = serializers.RegexField(r"^[A-Za-z]{3}$", max_length=3)
    recipient_token = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enabled_modules = serializers.ListField(child=serializers.ChoiceField(choices=("facial", "behavioral", "environment")), allow_empty=False)
    module_scores = serializers.DictField(child=serializers.IntegerField(min_value=0, max_value=100), required=False)


class TransactionRiskRequestSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=128)
    user_token = serializers.CharField(max_length=128)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal("0.01"))
    currency = serializers.RegexField(r"^[A-Za-z]{3}$", max_length=3)
    recipient_token = serializers.CharField(max_length=128, required=False, allow_blank=True)
    recipient = serializers.DictField(required=False)
    sender_profile = serializers.DictField(required=False)


class RecipientRiskRequestSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=128)
    user_token = serializers.CharField(max_length=128)
    recipient_token = serializers.CharField(max_length=128)
    currency = serializers.RegexField(r"^[A-Za-z]{3}$", max_length=3, required=False, default="NGN")
    recipient = serializers.DictField()


class EnvironmentRiskRequestSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=128)
    user_token = serializers.CharField(max_length=128)
    device = serializers.DictField(required=False)
    network = serializers.DictField(required=False)
    location = serializers.DictField(required=False)
    telecom = serializers.DictField(required=False)
    account_security = serializers.DictField(required=False)


class FacialRiskRequestSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=128)
    user_token = serializers.CharField(max_length=128)
    identity_verified = serializers.BooleanField(required=False, allow_null=True)
    ml_result = serializers.DictField(required=False, default=dict)

    def validate_ml_result(self, value):
        allowed = {"neutral", "happy", "sad", "angry", "fear"}
        if not set(value).issubset(allowed):
            raise serializers.ValidationError("ml_result contains an unsupported emotion")
        if any(not isinstance(probability, (int, float)) or probability < 0 or probability > 1 for probability in value.values()):
            raise serializers.ValidationError("emotion probabilities must be between 0 and 1")
        if sum(value.values()) > 1.01:
            raise serializers.ValidationError("emotion probabilities cannot sum above 1")
        return value


class RiskSignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskSignal
        fields = ("code", "source", "score", "severity", "confidence", "description")


class RiskAssessmentSerializer(serializers.ModelSerializer):
    signals = RiskSignalSerializer(many=True, read_only=True)

    class Meta:
        model = RiskAssessment
        fields = ("id", "transaction_id", "enabled_modules", "risk_score", "risk_level", "decision", "signals", "created_at")
