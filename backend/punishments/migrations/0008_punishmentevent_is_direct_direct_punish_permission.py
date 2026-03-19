from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("punishments", "0007_reason_max_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="punishmentevent",
            name="is_direct",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelOptions(
            name="punishmentevent",
            options={
                "permissions": [
                    ("direct_punish", "Can give punishments without a confirmer")
                ]
            },
        ),
    ]
