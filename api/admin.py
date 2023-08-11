from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Admin)
admin.site.register (Applicant)
admin.site.register(Ticket)
admin.site.register(Expert)
admin.site.register(Message)
admin.site.register(Notification)