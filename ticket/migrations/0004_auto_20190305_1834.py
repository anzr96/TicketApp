# Generated by Django 2.1.7 on 2019-03-05 18:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0003_auto_20190304_0808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='salon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ticket.Salon'),
        ),
    ]
