from pfa_projects.models import Message

def unread_messages_count(request):
    """Ajoute le nombre de messages non lus au contexte global"""
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_messages_count': unread_count}
    return {'unread_messages_count': 0} 