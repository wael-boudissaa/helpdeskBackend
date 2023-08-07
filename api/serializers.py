from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from .models import *

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        if hasattr(user, 'applicant'):
            token['type'] = 'applicant'
        if hasattr(user, 'admin'):
            token['type'] = 'admin'
        if hasattr(user, 'expert'):
            token['type'] = 'expert'
        return token
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # or specify the fields you want to include

class ExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expert
        fields = '__all__'  # Serialize all fields of the Expert model

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'  # or specify the fields you want to include

class PostTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('priority', 'issue', 'category')

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = '__all__'  # or specify the fields you want to include

class DeleteTicketSerializer (serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
class PostMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('idTicket', 'text')

class UserMessageSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()  # Define a SerializerMethodField

    def get_type(self, user):
        if hasattr(user, 'expert'):
            return 'expert'
        elif hasattr(user, 'applicant'):
            return 'applicant'
        return None  # Handle cases where neither 'expert' nor 'applicant' attribute exists
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'type')


class MessageSerializer(serializers.ModelSerializer):
    source = UserMessageSerializer()
    class Meta:
        model = Message
        fields = '__all__'