from django.db import migrations


DROP_ALLAUTH_TABLES = """
DROP TABLE IF EXISTS account_emailaddress CASCADE;
DROP TABLE IF EXISTS account_emailconfirmation CASCADE;
DROP TABLE IF EXISTS socialaccount_socialaccount CASCADE;
DROP TABLE IF EXISTS socialaccount_socialapp CASCADE;
DROP TABLE IF EXISTS socialaccount_socialapp_sites CASCADE;
DROP TABLE IF EXISTS socialaccount_socialtoken CASCADE;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0005_merge_20251114_0945'),
    ]

    operations = [
        migrations.RunSQL(
            sql=DROP_ALLAUTH_TABLES,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
