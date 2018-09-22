from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def connected(request):
    context = {"page_name": "connected"}
    return render(request, 'portal/connected.html', context)


def faq(request):
    context = {"page_name": "faq"}
    return render(request, 'portal/faq.html', context)
