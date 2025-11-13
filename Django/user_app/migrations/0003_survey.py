from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("user_app", "0002_profile_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Survey",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("gender", models.CharField(blank=True, max_length=10)),
                ("age", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("address", models.TextField(blank=True)),
                (
                    "has_chronic_disease",
                    models.BooleanField(blank=True, null=True),
                ),
                ("is_pregnant", models.BooleanField(blank=True, null=True)),
                ("height_cm", models.FloatField(blank=True, null=True)),
                ("weight_kg", models.FloatField(blank=True, null=True)),
                ("bmi", models.FloatField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="surveys",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "건강 설문",
                "verbose_name_plural": "건강 설문",
                "ordering": ["-created_at"],
            },
        ),
    ]
