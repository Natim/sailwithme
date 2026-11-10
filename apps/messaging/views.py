from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.billing.services import user_can_initiate_contact

from .models import AbuseReport, Conversation, ConversationParticipant, Message, UserBlock
from .services import mark_conversation_read


@login_required
def inbox(request):
    participations = (
        ConversationParticipant.objects.filter(user=request.user)
        .select_related("conversation", "conversation__listing")
        .order_by("-conversation__updated_at")
    )
    active_id = request.GET.get("c")
    active_conv = None
    thread_messages = []
    if active_id:
        active_conv = get_object_or_404(Conversation, pk=active_id)
        if not active_conv.participants.filter(user=request.user).exists():
            return redirect("messaging:inbox")
        thread_messages = list(active_conv.messages.select_related("author"))
        mark_conversation_read(active_conv, request.user)
    return render(
        request,
        "messaging/inbox.html",
        {
            "participations": participations,
            "active_conversation": active_conv,
            "thread_messages": thread_messages,
        },
    )


@login_required
def send_message(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    if not conversation.participants.filter(user=request.user).exists():
        return HttpResponse(status=403)
    if request.method != "POST":
        return redirect("messaging:inbox", **{"c": conversation_id})
    body = request.POST.get("body", "").strip()
    if not body:
        return redirect(f"/messages/?c={conversation_id}")
    other = conversation.other_participant(request.user)
    if other and conversation.listing is None and conversation.voyage is None:
        if not user_can_initiate_contact(request.user):
            messages.error(request, "Un Crew Pass est requis pour démarrer une conversation.")
            return redirect("billing:pricing")
    msg = Message.objects.create(conversation=conversation, author=request.user, body=body)
    conversation.updated_at = timezone.now()
    conversation.save(update_fields=["updated_at"])
    if request.headers.get("HX-Request"):
        return render(request, "messaging/partials/message.html", {"message": msg})
    return redirect(f"/messages/?c={conversation_id}")


@login_required
def poll_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    if not conversation.participants.filter(user=request.user).exists():
        return HttpResponse(status=403)
    after_id = int(request.GET.get("after", 0))
    qs = conversation.messages.filter(pk__gt=after_id).select_related("author")
    mark_conversation_read(conversation, request.user)
    return render(
        request,
        "messaging/partials/message_list.html",
        {"messages": qs},
    )


@login_required
def unread_count(request):
    from apps.messaging.context_processors import unread_messages

    count = unread_messages(request)["unread_message_count"]
    if count:
        return HttpResponse(
            f'<span id="nav-unread-badge" class="ml-1 rounded-full bg-red-500 px-1.5 text-xs text-white">{count}</span>'
        )
    return HttpResponse("")


@login_required
def block_user(request, user_id):
    UserBlock.objects.get_or_create(blocker=request.user, blocked_id=user_id)
    messages.success(request, "Utilisateur bloqué.")
    return redirect("messaging:inbox")


@login_required
def report_user(request, user_id):
    if request.method == "POST":
        AbuseReport.objects.create(
            reporter=request.user,
            reported_user_id=user_id,
            reason=request.POST.get("reason", ""),
        )
        messages.success(request, "Signalement envoyé.")
    return redirect("messaging:inbox")
