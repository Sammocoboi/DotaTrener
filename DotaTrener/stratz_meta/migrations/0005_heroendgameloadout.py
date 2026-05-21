from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stratz_meta", "0004_herometa_avg_stats"),
    ]

    operations = [
        migrations.CreateModel(
            name="HeroEndgameLoadout",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("item0_id", models.PositiveIntegerField(blank=True, null=True)),
                ("item1_id", models.PositiveIntegerField(blank=True, null=True)),
                ("item2_id", models.PositiveIntegerField(blank=True, null=True)),
                ("item3_id", models.PositiveIntegerField(blank=True, null=True)),
                ("item4_id", models.PositiveIntegerField(blank=True, null=True)),
                ("item5_id", models.PositiveIntegerField(blank=True, null=True)),
                ("games", models.PositiveIntegerField(default=0, help_text="Суммарный matchCount по предметам endgame из Stratz")),
                ("win_rate", models.FloatField(default=0.0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "hero_meta",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="endgame_loadout",
                        to="stratz_meta.herometa",
                    ),
                ),
            ],
            options={
                "verbose_name": "Endgame 6 слотов (титаны)",
                "verbose_name_plural": "Endgame 6 слотов (титаны)",
            },
        ),
    ]
