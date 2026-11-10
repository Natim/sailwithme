# Sails with Me

Plateforme pour mettre en relation skippers et équipiers sur des navigations au long cours.

## Démarrage rapide

**Avec Docker** (recommandé) :

```bash
pip install -e ".[dev]"
cp .env.example .env
docker compose up -d db redis
python manage.py migrate
python manage.py load_ports
python manage.py runserver
```

**Sans Docker** : GDAL + PostGIS requis. Voir `.env` (`DATABASE_URL` ou `USE_SPATIALITE=1`).

## Stack

Django 5, PostGIS, HTMX, Tailwind (CDN), django-allauth, django-q2.
