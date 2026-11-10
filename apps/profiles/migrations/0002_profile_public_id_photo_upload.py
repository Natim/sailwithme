import uuid

import apps.profiles.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="public_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="photo",
            field=models.ImageField(blank=True, upload_to=apps.profiles.models.profile_photo_upload_to),
        ),
    ]
