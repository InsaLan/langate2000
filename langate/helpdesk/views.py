from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django import template
from django.contrib.auth.decorators import login_required
from .TicketForm import MessageForm, AnwserForm
from .models import Ticket, Message

@login_required
def open_ticket(request):
    new_ticket = Ticket(owner=request.user)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        msg = Message()
        if form.is_valid():
                new_ticket.title = form.cleaned_data['title']
                new_ticket.save()
                msg.ticket = new_ticket
                msg.sender = request.user
                msg.content = form.cleaned_data['content']
                msg.save()
                sent = True
                return redirect('helpdesk')
    else:
        sent = False
        form =  MessageForm()
    return render(request, 'helpdesk.html', {"form": form, "sent": sent})


@staff_member_required
def admin(request):
    return render(request, 'admin_front.html', {"tickets": Ticket.objects.all()})

@login_required
def view_tickets(request):
    if Ticket.objects.filter(owner=request.user).count() == 0:
        return redirect('open-ticket')
    
    return render(request, 'ticket_viewer.html', {"tickets" : Ticket.objects.filter(owner=request.user) })

@login_required
def show_ticket(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    if request.method == 'POST':
        form = AnwserForm(request.POST)
        msg = Message()
        if form.is_valid():
                msg.ticket = ticket
                msg.sender = request.user
                msg.content = form.cleaned_data['content']
                msg.save()
                sent = True
    else:
        sent = False
        form =  AnwserForm()
    
    return render(request, 'ticket_detail.html', {"sent": sent, "form": form, "messages": Message.objects.filter(ticket=ticket.id)})