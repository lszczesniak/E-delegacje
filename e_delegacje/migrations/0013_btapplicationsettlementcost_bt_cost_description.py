# Generated by Django 3.1.7 on 2021-04-12 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_delegacje', '0012_btapplicationsettlementcost_attachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='btapplicationsettlementcost',
            name='bt_cost_description',
            field=models.CharField(default='koszt nr 1', max_length=140),
            preserve_default=False,
        ),
    ]
