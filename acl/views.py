from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import ACLRule

@user_passes_test(lambda u: u.is_superuser)
def manage_acl(request):
    acl_rules = ACLRule.objects.all()
    return render(request, 'acl/manage_acl.html', {'acl_rules': acl_rules})
