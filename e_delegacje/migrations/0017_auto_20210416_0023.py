# Generated by Django 3.1.7 on 2021-04-15 22:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('e_delegacje', '0016_auto_20210415_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='btapplicationsettlementfeeding',
            name='bt_application_settlement',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application_settlement_feeding', to='e_delegacje.btapplicationsettlement'),
        ),
    ]
