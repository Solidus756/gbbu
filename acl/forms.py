from django import forms
from .models import ACLRule

class ACLRuleForm(forms.ModelForm):
    class Meta:
        model = ACLRule
        fields = ['group', 'user', 'resource', 'action']
        widgets = {
            'group': forms.CheckboxSelectMultiple(),
            # Pour 'user', on peut utiliser un widget standard; le widget checkbox multiple ne s'applique pas directement ici
        }
