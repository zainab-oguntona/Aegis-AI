from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RiskAssessment, Transaction
from .behavioral import evaluate_behavior
from .environment import evaluate_environment
from .facial import evaluate_facial
from .ml_clients import facial_prediction
from .recipient import demo_recipient_context, evaluate_recipient
from .serializers import (EnvironmentRiskRequestSerializer, FacialRiskRequestSerializer, RecipientRiskRequestSerializer, RiskAssessmentRequestSerializer,
                          RiskAssessmentSerializer, TransactionRiskRequestSerializer)
from .services import classify_score, explain_assessment, fuse_scores
from .models import RiskSignal


class RiskAssessmentView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = RiskAssessmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        idempotency_key = request.headers.get("Idempotency-Key")
        modules = list(dict.fromkeys(data["enabled_modules"]))
        score = fuse_scores(data.get("module_scores", {}), modules)
        level, decision = classify_score(score)
        current, _ = Transaction.objects.get_or_create(
            client=request.user,
            transaction_id=data["transaction_id"],
            defaults={
                "user_token": data["user_token"], "recipient_token": data.get("recipient_token", ""),
                "amount": data["amount"], "currency": data["currency"].upper(),
            },
        )
        if idempotency_key:
            existing = RiskAssessment.objects.filter(transaction=current, idempotency_key=idempotency_key).first()
            if existing:
                return Response(RiskAssessmentSerializer(existing).data)
        assessment = RiskAssessment.objects.create(
            transaction=current, enabled_modules=modules, risk_score=score, risk_level=level, decision=decision,
            idempotency_key=idempotency_key,
        )
        status, explanations = explain_assessment({module: data.get("module_scores", {}).get(module, 0) for module in modules}, decision)
        return Response({**RiskAssessmentSerializer(assessment).data, "transaction_status": status, "explanation": explanations}, status=201)


class TransactionRiskView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = TransactionRiskRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        score, signals = evaluate_behavior(data["amount"], data.get("recipient", {}), data.get("sender_profile", {}))
        level, decision = classify_score(score)
        current, _ = Transaction.objects.get_or_create(
            client=request.user, transaction_id=data["transaction_id"],
            defaults={"user_token": data["user_token"], "recipient_token": data.get("recipient_token", ""),
                      "amount": data["amount"], "currency": data["currency"].upper()},
        )
        assessment = RiskAssessment.objects.create(
            transaction=current, enabled_modules=["behavioral"], risk_score=score, risk_level=level, decision=decision
        )
        RiskSignal.objects.bulk_create([
            RiskSignal(assessment=assessment, source="behavioral", **signal) for signal in signals
        ])
        return Response(RiskAssessmentSerializer(assessment).data, status=201)


class RecipientRiskView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = RecipientRiskRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data["recipient"] = {**demo_recipient_context(data["recipient_token"]), **data["recipient"]}
        score, signals = evaluate_recipient(data["recipient"])
        level, decision = classify_score(score)
        current, _ = Transaction.objects.get_or_create(
            client=request.user, transaction_id=data["transaction_id"],
            defaults={"user_token": data["user_token"], "recipient_token": data["recipient_token"],
                      "amount": 0, "currency": data["currency"].upper()},
        )
        assessment = RiskAssessment.objects.create(
            transaction=current, enabled_modules=["recipient"], risk_score=score, risk_level=level, decision=decision
        )
        RiskSignal.objects.bulk_create([RiskSignal(assessment=assessment, source="recipient", **signal) for signal in signals])
        return Response(RiskAssessmentSerializer(assessment).data, status=201)


class EnvironmentRiskView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = EnvironmentRiskRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        score, signals = evaluate_environment(data.get("device", {}), data.get("network", {}), data.get("location", {}),
                                               data.get("telecom", {}), data.get("account_security", {}))
        level, decision = classify_score(score)
        current, _ = Transaction.objects.get_or_create(
            client=request.user, transaction_id=data["transaction_id"],
            defaults={"user_token": data["user_token"], "amount": 0, "currency": "NGN"},
        )
        assessment = RiskAssessment.objects.create(
            transaction=current, enabled_modules=["environment"], risk_score=score, risk_level=level, decision=decision
        )
        RiskSignal.objects.bulk_create([RiskSignal(assessment=assessment, source="environment", **signal) for signal in signals])
        return Response(RiskAssessmentSerializer(assessment).data, status=201)


class FacialRiskView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = FacialRiskRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        prediction = facial_prediction(data["ml_result"])
        score, confidence, signals = evaluate_facial(prediction, data.get("identity_verified"))
        level, decision = classify_score(score)
        current, _ = Transaction.objects.get_or_create(
            client=request.user, transaction_id=data["transaction_id"],
            defaults={"user_token": data["user_token"], "amount": 0, "currency": "NGN"},
        )
        assessment = RiskAssessment.objects.create(
            transaction=current, enabled_modules=["facial"], risk_score=score, risk_level=level, decision=decision
        )
        RiskSignal.objects.bulk_create([RiskSignal(assessment=assessment, source="facial", **signal) for signal in signals])
        return Response({**RiskAssessmentSerializer(assessment).data, "confidence": confidence}, status=201)
