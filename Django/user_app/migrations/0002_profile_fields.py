from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_app", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="nickname",
        ),
        migrations.AddField(
            model_name="customuser",
            name="address",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="customuser",
            name="disease_history",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="height",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="pregnancy",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="weight",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
