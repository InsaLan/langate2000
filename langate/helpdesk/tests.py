from django.test import TestCase
from django.contrib.auth import get_user
from .models import *
"""
let go make TDD
"""
# Create your tests here.

class ModelsTests(TestCase):
    # Create a ticket and few messages in it
    def setUp(self):
        self.user = User.objects.create_user(username='root', password='root')
        self.user2 = User.objects.create_user(username='root2', password='root2')
        login = self.client.login(username="root", password="root")
        self.test_ticket  = Ticket(owner=self.user2)
        self.test_ticket2 = Ticket(owner=self.user2)
        self.msg = Message(title="title", content="content", sender=self.user, ticket=self.test_ticket)
        self.assertTrue(login)
    

    def test_message_correctness(self):
        self.assertEqual(self.msg.title, "title")


    def test_tickets_count(self):
        self.test_ticket.save()
        self.test_ticket2.save()
        self.assertEqual(Ticket.objects.filter(owner=self.user2).count(), 2)


    def test_ticket_unread(self):
       
        self.test_ticket.save()
        self.user2.save()
        self.msg.save()
        self.assertEquals(self.test_ticket.is_read, False)
    def test_selector(self):
        pass