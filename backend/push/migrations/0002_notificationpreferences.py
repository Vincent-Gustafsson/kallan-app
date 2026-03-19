import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("push", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationPreferences",
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
                ("punishment_proposed", models.BooleanField(default=True)),
                ("punishment_confirmed", models.BooleanField(default=True)),
                ("punishment_cancelled", models.BooleanField(default=True)),
                ("punishment_taken", models.BooleanField(default=True)),
                ("fikapinne_given", models.BooleanField(default=True)),
                ("fikapinne_taken", models.BooleanField(default=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_prefs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
