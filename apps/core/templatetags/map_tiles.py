from django import template

from apps.core.map_tiles import openlayers_tile_layer

register = template.Library()


@register.simple_tag
def ol_tile_config():
    return openlayers_tile_layer()
