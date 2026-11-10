from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from apps.listings.models import Port

PORTS = [
    ("la-rochelle", "La Rochelle", "France", -1.152, 46.159),
    ("gibraltar", "Gibraltar", "Gibraltar", -5.353, 36.141),
    ("las-palmas", "Las Palmas de Gran Canaria", "Spain", -15.413, 28.124),
    ("mindelo", "Mindelo", "Cape Verde", -24.987, 16.890),
    ("le-marin", "Le Marin", "Martinique", -60.868, 14.467),
    ("pointe-a-pitre", "Pointe-à-Pitre", "Guadeloupe", -61.531, 16.241),
    ("shelter-bay", "Shelter Bay", "Panama", -79.367, 9.381),
    ("galapagos", "Puerto Ayora", "Ecuador", -90.315, -0.739),
    ("papeete", "Papeete", "French Polynesia", -149.566, -17.537),
    ("lorient", "Lorient", "France", -3.366, 47.748),
]


class Command(BaseCommand):
    help = "Load key sailing ports into the database."

    def handle(self, *args, **options):
        for slug, name, country, lng, lat in PORTS:
            Port.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "country": country,
                    "location": Point(lng, lat, srid=4326),
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(PORTS)} ports."))
