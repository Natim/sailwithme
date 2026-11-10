from django import template

register = template.Library()


@register.filter
def public_name(user):
    if user is None:
        return ""
    if not hasattr(user, "profile"):
        full = (user.get_full_name() or "").strip()
        return full or "Marin"
    return user.profile.public_name()
