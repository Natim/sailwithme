from django.contrib.gis.forms import OSMWidget


class ConfiguredOSMWidget(OSMWidget):
    """Admin map widget using the project's tile source.

    Django's form renderer does not look in the project ``templates/`` directory,
    so a ``gis/openlayers-osm.html`` override there is never used. This widget
    points at a template that lives inside an installed app.
    """

    template_name = "gis/openlayers-sailwithme.html"
