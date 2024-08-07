# Generated by Django 5.0.4 on 2024-07-06 17:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dictionary", "0003_remove_user_is_admin_user_date_joined_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Language",
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
                ("code", models.CharField(max_length=5, unique=True)),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Translation",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Dictionary",
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
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "source_language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="dictionary.language",
                    ),
                ),
                (
                    "target_language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="dictionary.language",
                    ),
                ),
                (
                    "translations",
                    models.ManyToManyField(
                        related_name="+", to="dictionary.translation"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Word",
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
                ("word", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dictionary.language",
                    ),
                ),
                (
                    "translations",
                    models.ManyToManyField(
                        related_name="translated_words",
                        through="dictionary.Translation",
                        to="dictionary.word",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="translation",
            name="from_word",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="source_word",
                to="dictionary.word",
            ),
        ),
        migrations.AddField(
            model_name="translation",
            name="to_word",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="target_word",
                to="dictionary.word",
            ),
        ),
        migrations.AddConstraint(
            model_name="word",
            constraint=models.UniqueConstraint(
                fields=("word", "language"), name="unique_word_language"
            ),
        ),
        migrations.AddConstraint(
            model_name="translation",
            constraint=models.UniqueConstraint(
                fields=("to_word", "from_word"), name="unique_translation_pair_reverse"
            ),
        ),
    ]
