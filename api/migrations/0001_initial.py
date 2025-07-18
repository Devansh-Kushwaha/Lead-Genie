# Generated by Django 5.1.4 on 2025-07-03 15:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('domain', models.CharField(max_length=255, unique=True)),
                ('location', models.CharField(blank=True, max_length=155)),
                ('size', models.CharField(blank=True, max_length=100)),
                ('found_in', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('pain_points', models.TextField(blank=True)),
                ('values', models.TextField(blank=True)),
                ('services_suggestions', models.TextField(blank=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('designation', models.CharField(blank=True, max_length=100)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='api.company')),
            ],
        ),
        migrations.CreateModel(
            name='LeadScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('reason', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lead_scores', to='api.company')),
            ],
        ),
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('url', models.URLField()),
                ('published_date', models.DateTimeField()),
                ('summary', models.TextField(blank=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news_articles', to='api.company')),
            ],
        ),
    ]
