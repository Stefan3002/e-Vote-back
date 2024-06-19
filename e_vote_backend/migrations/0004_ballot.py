# Generated by Django 4.2.13 on 2024-06-19 20:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('e_vote_backend', '0003_alter_appuser_challenge_issued'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ballot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('year', models.IntegerField()),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('eligible_people', models.CharField(max_length=100)),
            ],
        ),
    ]