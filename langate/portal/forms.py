from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    wg1 = forms.TextInput(attrs= { "autofocus": True, "placeholder": "name@example.com", "class" : "form-control" })
    wg2 = forms.PasswordInput(attrs= { "class" : "form-control" })
    username = forms.EmailField(required=True, widget=wg1, label="Adresse Mail", label_suffix="")
    password = forms.CharField(max_length=96, widget=wg2, label="Mot de Passe", label_suffix="")
    
    # this is a little workaround to allow django to use bootstrap form validation css rules
    # see https://getbootstrap.com/docs/4.1/components/forms/#server-side and https://stackoverflow.com/a/8256041
    def is_valid(self):

        ret = forms.Form.is_valid(self)
        e = self.errors
        for f in self.errors:
            if f != "__all__":
                self.fields[f].widget.attrs.update({'class': self.fields[f].widget.attrs.get('class', '') + ' is-invalid'})
        return ret
