from django import template
from pfa_projects.models import Message

register = template.Library()

@register.simple_tag
def get_unread_messages_count(user):
    """Retourne le nombre de messages non lus pour un utilisateur"""
    return Message.objects.filter(recipient=user, is_read=False).count() 