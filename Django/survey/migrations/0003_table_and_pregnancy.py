from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_bmi_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='surveyresponse',
            old_name='is_pregnant',
            new_name='pregnancy',
        ),
        migrations.AlterField(
            model_name='surveyresponse',
            name='pregnancy',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelTable(
            name='surveyresponse',
            table='survey_response',
        ),
    ]
