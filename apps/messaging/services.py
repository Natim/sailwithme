import uuid

from django.db import models, transaction
from django.utils import timezone

from .models import Conversation, ConversationParticipant, Message, UserBlock


def users_blocked(a_id: uuid.UUID, b_id: uuid.UUID) -> bool:
    return UserBlock.objects.filter(
        models.Q(blocker_id=a_id, blocked_id=b_id) | models.Q(blocker_id=b_id, blocked_id=a_id)
    ).exists()


@transaction.atomic
def start_conversation(user_a, user_b, listing=None, voyage=None, first_message: str = ""):
    if users_blocked(user_a.id, user_b.id):
        raise PermissionError("Users are blocked")

    conv = None
    if listing and not voyage:
        conv = Conversation.objects.filter(listing=listing, is_group=False).prefetch_related("participants").first()
        if conv:
            part_ids = set(conv.participants.values_list("user_id", flat=True))
            if user_a.id in part_ids and user_b.id in part_ids:
                if first_message:
                    Message.objects.create(conversation=conv, author=user_a, body=first_message)
                conv.updated_at = timezone.now()
                conv.save(update_fields=["updated_at"])
                return conv

    conv = Conversation.objects.create(
        listing=listing,
        voyage=voyage,
        is_group=bool(voyage),
        title=listing.title if listing else (voyage.title if voyage else ""),
    )
    for user in {user_a, user_b}:
        ConversationParticipant.objects.create(conversation=conv, user=user)
    if first_message:
        Message.objects.create(conversation=conv, author=user_a, body=first_message)
    return conv


def mark_conversation_read(conversation, user):
    part = ConversationParticipant.objects.filter(conversation=conversation, user=user).first()
    if part:
        part.last_read_at = timezone.now()
        part.save(update_fields=["last_read_at"])
