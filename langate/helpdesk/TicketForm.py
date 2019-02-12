from django import forms
from .models import Message

class MessageForm(forms.Form):
    title = forms.CharField(label="Titre")
    content = forms.CharField(label="Message", widget=forms.Textarea)

class AnwserForm(forms.Form):
    content = forms.CharField(label="Réponse", widget=forms.Textarea)
