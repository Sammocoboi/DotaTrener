from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stratz_meta", "0005_heroendgameloadout"),
    ]

    operations = [
        migrations.AddField(
            model_name="heroendgameloadout",
            name="item0_time",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Секунда покупки (Stratz itemFullPurchase.time)",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="heroendgameloadout",
            name="item1_time",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="heroendgameloadout",
            name="item2_time",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="heroendgameloadout",
            name="item3_time",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="heroendgameloadout",
            name="item4_time",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="heroendgameloadout",
            name="item5_time",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
