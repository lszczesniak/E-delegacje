# Generated by Django 3.1.7 on 2021-04-07 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_delegacje', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='btcostcenter',
            name='cost_center_number',
            field=models.CharField(default='4811119204', max_length=10),
            preserve_default=False,
        ),
    ]
