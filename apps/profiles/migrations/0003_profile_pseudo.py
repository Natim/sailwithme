from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0002_profile_public_id_photo_upload"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="pseudo",
            field=models.CharField(
                blank=True,
                help_text="Nom affiché publiquement (annonces, avis, annuaire).",
                max_length=32,
            ),
        ),
    ]
