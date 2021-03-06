# Generated by Django 2.1.7 on 2019-03-04 08:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0002_auto_20190304_0657'),
    ]

    operations = [
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='portfolio/')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('salon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.Salon')),
            ],
        ),
        migrations.AddField(
            model_name='subservice',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='sub_service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ticket.SubService'),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ticket.Tag'),
        ),
    ]
