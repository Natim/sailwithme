# Sail with Me

Plateforme pour mettre en relation skippers et équipiers sur des navigations au long cours.

## Démarrage rapide

**Avec Docker** (recommandé) :

```bash
pip install -e ".[dev]"
pre-commit install   # Ruff check + format on each commit (same as CI)
cp .env.example .env
docker compose up -d db redis
python manage.py migrate
python manage.py load_ports
python manage.py runserver
```

**Sans Docker** : GDAL + PostGIS requis. Voir `.env` (`DATABASE_URL` ou `USE_SPATIALITE=1`).

## Stack

Django 5, PostGIS, HTMX, Tailwind (CDN), django-allauth, django-q2.

## Licence

Le code source est publié sous la **GNU Affero General Public License v3.0** ([LICENSE](LICENSE)). Copyright SAS CLOUDY.

Si vous exploitez une version modifiée accessible sur le réseau, l’AGPL impose d’offrir aux utilisateurs le code source correspondant à cette version.

L’AGPL ne couvre pas le nom **Sail with Me**, les logos ni la charte graphique du site, qui restent la propriété de SAS CLOUDY. Les conditions d’utilisation du service sont accessibles à l’URL `/legal/cgu/` du site déployé.
