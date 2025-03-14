# Generated by Django 5.1.6 on 2025-03-13 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='coupon_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='coupon_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='coupon_start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='coupon_text',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='member',
            name='coupon_type',
            field=models.CharField(choices=[('percentage', 'Percentage'), ('value', 'Value')], default='percentage', max_length=20),
        ),
        migrations.AddField(
            model_name='member',
            name='coupon_value',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
