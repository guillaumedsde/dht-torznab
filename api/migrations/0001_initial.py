# Generated by Django 3.1.5 on 2021-01-09 15:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Torrent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.TextField()),
                ("info_hash", models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name="File",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("path", models.TextField()),
                ("size", models.BigIntegerField()),
                (
                    "torrent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.torrent"
                    ),
                ),
            ],
        ),
    ]
