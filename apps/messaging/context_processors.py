def unread_messages(request):
    if not request.user.is_authenticated:
        return {"unread_message_count": 0}

    from apps.messaging.models import ConversationParticipant

    unread = 0
    qs = ConversationParticipant.objects.filter(user=request.user).select_related("conversation")
    for part in qs:
        last_msg = part.conversation.messages.order_by("-created_at").first()
        if last_msg and last_msg.author_id != request.user.id:
            if not part.last_read_at or part.last_read_at < last_msg.created_at:
                unread += 1
    return {"unread_message_count": unread}
