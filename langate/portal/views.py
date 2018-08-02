from django.shortcuts import render
from django.http import HttpResponse
from .forms import LoginForm

# Create your views here.
def index(request):

    f = LoginForm(request.POST or None)

    context = { "page_name": "index", "form": f }
    return render(request, 'portal/index.html', context)

def faq(request):
    context = { "page_name": "faq" }
    return render(request, 'portal/faq.html', context)
