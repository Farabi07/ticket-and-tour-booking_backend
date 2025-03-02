# Generated by Django 5.1.6 on 2025-03-02 20:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('member', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('email_body', models.CharField(blank=True, max_length=50000, null=True)),
                ('tour_type', models.CharField(blank=True, max_length=255, null=True)),
                ('group_size', models.CharField(blank=True, max_length=255, null=True)),
                ('seat_quantity', models.IntegerField(blank=True, null=True)),
                ('itinerary', models.CharField(blank=True, max_length=20000, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
                ('adult_seat_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
                ('child_seat_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
                ('youth_seat_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='bbms/BusImage/')),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
                ('starting_point', models.CharField(blank=True, max_length=5000, null=True)),
                ('end_point', models.CharField(blank=True, max_length=5000, null=True)),
                ('seat_plan', models.CharField(blank=True, max_length=255, null=True)),
                ('owner_name', models.CharField(blank=True, max_length=255, null=True)),
                ('primary_phone', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Bus',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='AvailableDates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('bus_data', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='available_dates', to='bbms.bus')),
            ],
            options={
                'verbose_name_plural': 'AvailableTimes',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='BusBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat_no', models.CharField(blank=True, max_length=255, null=True)),
                ('reference_no', models.CharField(blank=True, max_length=255, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('pickup_time', models.CharField(blank=True, max_length=255, null=True)),
                ('meeting_point', models.CharField(blank=True, max_length=1000, null=True)),
                ('booking_time', models.CharField(blank=True, max_length=500, null=True)),
                ('number_of_travellers', models.CharField(blank=True, max_length=500, null=True)),
                ('booking_invoice', models.FileField(blank=True, null=True, upload_to='booking_invoice/')),
                ('email_pdf', models.FileField(blank=True, null=True, upload_to='booking_pdf/')),
                ('total_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_seat_count', models.IntegerField(blank=True, null=True)),
                ('discount_percent', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('discount_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('discount_type', models.CharField(blank=True, choices=[('percentage', 'Percentage'), ('value', 'Value')], default='percentage', max_length=20, null=True)),
                ('payment_type', models.CharField(blank=True, choices=[('bank', 'Bank'), ('cash', 'Cash')], default='bank', max_length=15, null=True)),
                ('account_holder_name', models.CharField(blank=True, max_length=1000, null=True)),
                ('bank_name', models.CharField(blank=True, max_length=1500, null=True)),
                ('txn_no', models.CharField(blank=True, max_length=500, null=True)),
                ('paid_amount', models.CharField(blank=True, max_length=500, null=True)),
                ('ticket_number', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('status', models.CharField(choices=[('booked', 'Booked'), ('available', 'Available'), ('cancelled', 'Cancelled')], default='available', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buses', to='bbms.bus')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member', to='member.member')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Bus Booking',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='BookingSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_discount_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_seat_count', models.IntegerField()),
                ('discount_percent', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('discount_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('value', 'Value')], default='percentage', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_details', to='member.member')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('bus_booking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bus_booking', to='bbms.busbooking')),
            ],
            options={
                'verbose_name_plural': 'Agent Commission',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('primary_phone', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='passenger_member', to='member.member')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Passengers',
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='busbooking',
            name='passenger',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='passenger', to='bbms.passenger'),
        ),
    ]
