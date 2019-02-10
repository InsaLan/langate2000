from django import forms
from .models import Message

class MessageForm(forms.Form):
    title = forms.CharField(label="titre")
    content = forms.CharField(label="message", widget=forms.Textarea)

class AnwserForm(forms.Form):
    content = forms.CharField(label="réponse", widget=forms.Textarea)
