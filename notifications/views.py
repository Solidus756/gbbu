from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.contrib import messages

@login_required
def user_notifications(request):
    notifications = Notification.objects.filter(recipient_user=request.user)
    return render(request, "notifications/dashboard.html", {"notifications": notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient_user=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, "Notification marquée comme lue.")
    return redirect("notifications:dashboard")
