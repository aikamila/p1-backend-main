# Generated by Django 4.0 on 2022-02-08 00:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts_comments', '0003_post_engagement'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='engagement',
            new_name='engagement_rate',
        ),
    ]