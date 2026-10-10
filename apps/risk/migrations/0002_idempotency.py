from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("risk", "0001_initial")]
    operations = [
        migrations.AddField(model_name="riskassessment", name="idempotency_key", field=models.CharField(blank=True, max_length=255, null=True)),
        migrations.AddConstraint(
            model_name="riskassessment",
            constraint=models.UniqueConstraint(fields=("transaction", "idempotency_key"), name="unique_transaction_idempotency"),
        ),
    ]
