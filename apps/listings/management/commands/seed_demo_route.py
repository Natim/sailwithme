from django.core.management.base import BaseCommand

from apps.listings.models import Port, RoutePage


class Command(BaseCommand):
    help = "Create sample SEO route page Las Palmas → Martinique."

    def handle(self, *args, **options):
        dep = Port.objects.filter(slug="las-palmas").first()
        arr = Port.objects.filter(slug="le-marin").first()
        RoutePage.objects.update_or_create(
            slug="las-palmas-martinique",
            defaults={
                "title": "Las Palmas → Martinique (transatlantique)",
                "meta_description": "Annonces et équipiers pour la traversée des Canaries aux Antilles.",
                "body": (
                    "Fenêtre typique : semaines 46 à 52. "
                    "Retrouvez skippers et équipiers pour l'ARC et les départs indépendants."
                ),
                "departure_port": dep,
                "arrival_port": arr,
            },
        )
        self.stdout.write(self.style.SUCCESS("Route page ready."))
