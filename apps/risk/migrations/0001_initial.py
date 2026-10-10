import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("clients", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transaction_id", models.CharField(max_length=128)),
                ("user_token", models.CharField(max_length=128)),
                ("recipient_token", models.CharField(blank=True, max_length=128)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("currency", models.CharField(max_length=3)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("client", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="clients.client")),
            ],
        ),
        migrations.CreateModel(
            name="RiskAssessment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("enabled_modules", models.JSONField(default=list)),
                ("risk_score", models.PositiveSmallIntegerField()),
                ("risk_level", models.CharField(max_length=10)),
                ("decision", models.CharField(max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("transaction", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assessments", to="risk.transaction")),
            ],
        ),
        migrations.CreateModel(
            name="RiskSignal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=80)),
                ("source", models.CharField(max_length=40)),
                ("score", models.PositiveSmallIntegerField()),
                ("severity", models.CharField(max_length=10)),
                ("confidence", models.DecimalField(decimal_places=3, default=1, max_digits=4)),
                ("description", models.CharField(max_length=255)),
                ("assessment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="signals", to="risk.riskassessment")),
            ],
        ),
        migrations.AddConstraint(
            model_name="transaction",
            constraint=models.UniqueConstraint(fields=("client", "transaction_id"), name="unique_client_transaction"),
        ),
    ]
