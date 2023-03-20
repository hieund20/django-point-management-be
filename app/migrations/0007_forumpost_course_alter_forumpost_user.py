# Generated by Django 4.1.7 on 2023-03-20 16:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumpost',
            name='course',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='app.course'),
        ),
        migrations.AlterField(
            model_name='forumpost',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
