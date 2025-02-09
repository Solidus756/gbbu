# charity_streaming/views.py
from django.shortcuts import render
from accounts.forms import StreamerForm, StaffForm

def home(request):
    streamer_form = StreamerForm()
    staff_form = StaffForm()
    return render(request, 'home.html', {
        'streamer_form': streamer_form,
        'staff_form': staff_form,
    })
