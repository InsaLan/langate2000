from django import forms


class TicketForm(forms.Form):
    subject = forms.CharField(label="titre", max_length="200")
    content = forms.CharField(label="message", widget=forms.Textarea)