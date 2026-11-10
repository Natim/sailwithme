from django.urls import path

from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("<int:conversation_id>/send/", views.send_message, name="send"),
    path("<int:conversation_id>/poll/", views.poll_messages, name="poll"),
    path("unread/", views.unread_count, name="unread_count"),
    path("block/<int:user_id>/", views.block_user, name="block"),
    path("report/<int:user_id>/", views.report_user, name="report"),
]
