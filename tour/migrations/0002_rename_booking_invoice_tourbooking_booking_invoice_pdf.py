# Generated by Django 5.1.6 on 2025-03-07 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tour', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tourbooking',
            old_name='booking_invoice',
            new_name='booking_invoice_pdf',
        ),
    ]
