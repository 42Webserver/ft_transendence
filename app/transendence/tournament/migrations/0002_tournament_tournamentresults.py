# Generated by Django 4.2.16 on 2024-10-24 13:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tournament_id', models.CharField(max_length=50, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TournamentResults',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField(default=1)),
                ('games', models.IntegerField(default=0)),
                ('won', models.IntegerField(default=0)),
                ('lost', models.IntegerField(default=0)),
                ('goals_for', models.IntegerField(default=0)),
                ('goals_against', models.IntegerField(default=0)),
                ('diff', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                ('tournament_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_results', to='tournament.tournament')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_tournament_results', to='tournament.gamestatsuser')),
            ],
        ),
    ]