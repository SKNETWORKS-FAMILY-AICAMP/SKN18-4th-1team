from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveyresponse',
            name='height_cm',
            field=models.PositiveIntegerField(default=170, verbose_name='키(cm)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='weight_kg',
            field=models.DecimalField(decimal_places=2, default=60, max_digits=5, verbose_name='몸무게(kg)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='bmi',
            field=models.DecimalField(blank=True, decimal_places=1, editable=False, max_digits=4, null=True, verbose_name='BMI'),
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='bmi_category',
            field=models.CharField(blank=True, choices=[('UNDERWEIGHT', '저체중'), ('NORMAL', '정상'), ('OVERWEIGHT', '과체중'), ('OBESE', '비만')], editable=False, max_length=20, null=True, verbose_name='비만도'),
        ),
    ]
