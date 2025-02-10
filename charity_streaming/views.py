# charity_streaming/views.py
from django.shortcuts import render
from accounts.forms import StreamerForm, StaffApplicationForm, SocialAccountFormSet

def home(request):
    streamer_form = StreamerForm()
    staff_form = StaffApplicationForm()
    social_formset = SocialAccountFormSet(prefix="socialaccount_set")
    return render(request, 'home.html', {
        'streamer_form': streamer_form,
        'staff_form': staff_form,
        'social_formset': social_formset,
    })
