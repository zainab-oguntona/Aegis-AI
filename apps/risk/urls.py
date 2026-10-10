from django.urls import path

from .views import EnvironmentRiskView, FacialRiskView, RecipientRiskView, RiskAssessmentView, TransactionRiskView

urlpatterns = [
    path("risk-assessment/", RiskAssessmentView.as_view()),
    path("transaction-risk/", TransactionRiskView.as_view()),
    path("recipient-risk/", RecipientRiskView.as_view()),
    path("environment-risk/", EnvironmentRiskView.as_view()),
    path("facial-risk/", FacialRiskView.as_view()),
]
