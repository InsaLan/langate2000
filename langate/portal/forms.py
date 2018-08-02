from django import forms

class LoginForm(forms.Form):
    wg1 = forms.TextInput(attrs= { "placeholder": "name@example.com", "class" : "form-control" })
    wg2 = forms.PasswordInput(attrs= { "class" : "form-control" })
    email = forms.EmailField(required=True, widget=wg1, label="Adresse Mail", label_suffix="")
    passwd = forms.CharField(max_length=96, widget=wg2, label="Mot de Passe", label_suffix="")

