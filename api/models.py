from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.core.validators import MaxValueValidator

def generate_unique_ticket_code():
    length = 10

    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if Ticket.objects.filter(idTicket=code).count() == 0:
            break

    return code
def generate_unique_message_code():
    length = 10

    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if Message.objects.filter(idTicket=code).count() == 0:
            break

    return code
def generate_unique_notification_code():
    length = 10

    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if Notification.objects.filter(idTicket=code).count() == 0:
            break

    return code

class Applicant(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='applicant', primary_key=True)
    job_title = models.CharField(max_length=100,default="Undefined Job")
    def __str__ (self):
        return self.user.username

class Admin (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin', primary_key=True)
    def __str__ (self):
        return self.user.username

class Expert (models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='expert', primary_key=True)
    domaine_expertise=models.CharField(max_length=100, null=False)
    def __str__ (self):
        return self.user.username 
    
class Ticket (models.Model):
    idTicket = models.CharField(max_length=15, primary_key=True, default=generate_unique_ticket_code)
    priority = models.IntegerField(
        validators=[MaxValueValidator(3)],  
        help_text="Enter an integer value not exceeding 3.",
        null=False)
    etat=models.CharField(max_length=20,default="waiting")
    issue = models.CharField(max_length=100, null=False)
    category = models.CharField(max_length=50, null=False)
    expertId= models.ForeignKey(Expert,on_delete=models.CASCADE, related_name='tickets', null=True, blank=True)
    applicantId= models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='tickets')
    creationDate=models.DateTimeField(auto_now_add=True)
    def __str__ (self):
        return self.idTicket
    
class Message (models.Model): 
    idMessage = models.CharField(max_length=15,primary_key=True, default=generate_unique_message_code)
    idTicket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    source = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    text =models.CharField(max_length=800, null=False)
    creationDate=models.DateTimeField(auto_now_add=True)
    def __str__ (self):
        return self.idMessage 

class Notification(models.Model): 
    idNotification = models.CharField(max_length=15,primary_key=True, default=generate_unique_notification_code)
    idTicket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='notifications')
    reason = models.CharField(max_length=20,null=False)
    def __str__ (self):
        return self.idNotification

