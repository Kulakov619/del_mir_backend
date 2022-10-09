# Generated by Django 4.0.8 on 2022-10-08 17:20

import authcore.managers
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=254, unique=True, verbose_name='User name')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('mobile', models.CharField(blank=True, max_length=150, null=True, unique=True, verbose_name='mobile number')),
                ('last_name', models.CharField(blank=True, max_length=500, verbose_name='lastname')),
                ('name', models.CharField(max_length=500, verbose_name='name')),
                ('o_name', models.CharField(blank=True, max_length=500, verbose_name='o_name')),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='user_images', verbose_name='Profile Photo')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='дата рождения')),
                ('is_man', models.BooleanField(blank=True, null=True, verbose_name='male')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='Date Joined')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name='Date Modified')),
                ('is_active', models.BooleanField(default=False, verbose_name='Activated')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Staff Status')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            managers=[
                ('objects', authcore.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='OTPValidation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.CharField(max_length=10, verbose_name='OTP code')),
                ('destination', models.CharField(max_length=254, unique=True, verbose_name='destination Address (mobile/email)')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='create Date')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('is_validated', models.BooleanField(default=False, verbose_name='is validated')),
                ('validate_attempt', models.IntegerField(default=3, verbose_name='attempted validation')),
                ('prop', models.CharField(choices=[('E', 'EMail Address'), ('M', 'Mobile Number')], default='E', max_length=3, verbose_name='destination property')),
                ('send_counter', models.IntegerField(default=0, verbose_name='OTP sent counter')),
                ('sms_id', models.CharField(blank=True, max_length=254, null=True, verbose_name='SMS ID')),
                ('reactive_at', models.DateTimeField(verbose_name='ReActivate sending OTP')),
            ],
            options={
                'verbose_name': 'OTP Validation',
                'verbose_name_plural': 'OTP Validations',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='DopMobile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_column='created')),
                ('updated', models.DateTimeField(auto_now=True, db_column='updated')),
                ('mobile', models.CharField(blank=True, max_length=150, null=True, unique=True, verbose_name='mobile number')),
                ('confirmed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user phone',
                'verbose_name_plural': 'user phones',
            },
        ),
        migrations.CreateModel(
            name='AuthTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('token', models.TextField(verbose_name='JWT Access Token')),
                ('session', models.TextField(verbose_name='Session Passed')),
                ('refresh_token', models.TextField(blank=True, verbose_name='JWT Refresh Token')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Expires At')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date/Time')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name='Date/Time Modified')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Authentication Transaction',
                'verbose_name_plural': 'Authentication Transactions',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_column='created')),
                ('updated', models.DateTimeField(auto_now=True, db_column='updated')),
                ('address', models.CharField(max_length=255, verbose_name='адрес')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'address',
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The roles this user belongs to. A user will get all permissions granted to each of their roles.', related_name='user_set', related_query_name='user', to='authcore.role', verbose_name='Roles'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
