# Generated by Django 3.1.7 on 2021-04-28 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_delegacje', '0021_auto_20210426_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='btapplicationsettlement',
            name='settlement_status',
            field=models.CharField(choices=[('saved', 'Zapisany'), ('in_progress', 'W akceptacji'), ('approved', 'Zaakceptowany'), ('rejected', 'Odrzucony'), ('settlement_in_progress', 'Rozliczany'), ('settled', 'Rozliczony'), ('canceled', 'Anulowany')], default='saved', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='btapplication',
            name='application_status',
            field=models.CharField(choices=[('saved', 'Zapisany'), ('in_progress', 'W akceptacji'), ('approved', 'Zaakceptowany'), ('rejected', 'Odrzucony'), ('settlement_in_progress', 'Rozliczany'), ('settled', 'Rozliczony'), ('canceled', 'Anulowany')], max_length=30),
        ),
    ]
