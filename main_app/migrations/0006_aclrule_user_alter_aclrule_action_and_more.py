# Generated by Django 5.1.5 on 2025-01-19 22:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('main_app', '0005_aclrule'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='aclrule',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur'),
        ),
        migrations.AlterField(
            model_name='aclrule',
            name='action',
            field=models.CharField(choices=[('view', 'Afficher'), ('edit', 'Modifier'), ('delete', 'Supprimer')], max_length=50, verbose_name='Action'),
        ),
        migrations.AlterField(
            model_name='aclrule',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group', verbose_name='Groupe'),
        ),
        migrations.AlterField(
            model_name='aclrule',
            name='resource',
            field=models.CharField(choices=[('messagerie', 'Messagerie'), ('profil', 'Profil'), ('twitchwall', 'Twitch Wall')], max_length=50, verbose_name='Ressource'),
        ),
        migrations.AlterUniqueTogether(
            name='aclrule',
            unique_together={('group', 'user', 'resource', 'action')},
        ),
    ]
