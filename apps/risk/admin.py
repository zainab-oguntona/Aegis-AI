from django.contrib import admin

from .models import RiskAssessment, RiskSignal, Transaction

admin.site.register((Transaction, RiskAssessment, RiskSignal))
