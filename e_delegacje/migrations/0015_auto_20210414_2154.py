# Generated by Django 3.1.7 on 2021-04-14 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0003_btcurrency'),
        ('e_delegacje', '0014_auto_20210413_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='btapplication',
            name='application_status',
            field=models.CharField(choices=[('saved', 'Zapisany'), ('in_progress', 'W akceptacji'), ('approved', 'Zaakcdptowany'), ('settled', 'Rozliczony'), ('canceled', 'Anulowany')], max_length=30),
        ),
        migrations.AlterField(
            model_name='btapplicationsettlementcost',
            name='bt_cost_VAT_rate',
            field=models.CharField(choices=[('W1', '23 %'), ('W8', '8 %'), ('WN', 'nie dotyczy'), ('W0', 'zwolniony')], max_length=20),
        ),
        migrations.AlterField(
            model_name='btapplicationsettlementcost',
            name='bt_cost_category',
            field=models.CharField(choices=[('accommodation', 'nocleg'), ('transport', 'dojazd'), ('luggage', 'bagaż'), ('other', 'inne')], max_length=40),
        ),
        migrations.AlterField(
            model_name='btapplicationsettlementcost',
            name='bt_cost_currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_application_settlement_costs', to='setup.btcurrency'),
        ),
        migrations.DeleteModel(
            name='BtCurrency',
        ),
    ]