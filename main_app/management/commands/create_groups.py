from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = "Créer les groupes initiaux"

    def handle(self, *args, **kwargs):
        roles = ["SuperAdmin", "Admin", "Staff", "Streamer"]
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Groupe {role} créé avec succès"))
