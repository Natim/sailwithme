from django import template

register = template.Library()


@register.filter
def public_name(user):
    if user is None:
        return ""
    profile = getattr(user, "profile", None)
    if profile is None:
        return "Marin"
    return profile.public_name()
