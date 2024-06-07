# Generated by Django 5.0.1 on 2024-05-31 10:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('address', models.CharField(blank=True, max_length=100)),
                ('organization', models.CharField(blank=True, max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('added_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services_added', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services_modified', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('promo_code', models.CharField(blank=True, max_length=100, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('grand_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='services.service')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_quantity', models.IntegerField()),
                ('max_quantity', models.IntegerField()),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='services.service')),
            ],
        ),
    ]