from .models import Notification

ICON_MAP = {
    'info': 'fa-circle-info text-primary',
    'event': 'fa-calendar-days text-success',
    'alert': 'fa-triangle-exclamation text-danger',
}

def notification_context(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient_user=request.user, is_read=False).order_by('-created_at')

        for notification in notifications:
            notification.icon_class = ICON_MAP.get(notification.type, 'fa-bell text-secondary')

        return {'menu_notifications': notifications}
    return {}
