from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.


@staff_member_required
def management(request):
    context = { "page_name": "management" }
    return render(request, 'portal/management.html', context)


@login_required
def connected(request):
    context = {"page_name": "connected"}
    return render(request, 'portal/connected.html', context)


def faq(request):
    context = {"page_name": "faq"}
    return render(request, 'portal/faq.html', context)
