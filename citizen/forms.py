from django import forms
from core.models import Issue

class IssueForm(forms.ModelForm):
    image = forms.ImageField(required=True, help_text="Upload an image of the issue")

    class Meta:
        model = Issue
        fields = ['title', 'description', 'category', 'address']
