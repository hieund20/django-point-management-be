# Generated by Django 4.1.7 on 2023-03-06 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_user_classname'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='courses',
            field=models.ManyToManyField(related_name='users', to='app.course'),
        ),
    ]
