from django import forms
from .models import ACLRule

class ACLRuleForm(forms.ModelForm):
    class Meta:
        model = ACLRule
        fields = ['group', 'user', 'resource', 'action']
