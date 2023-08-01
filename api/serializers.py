from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

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
    