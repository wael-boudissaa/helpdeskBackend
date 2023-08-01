from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from .models import *
from rest_framework import status

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class TicketsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get (self,request,pk=None):
        if (IsApplicant().has_permission(request, self)):
            user = UserSerializer(request.user).data
            queryset = Ticket.objects.filter(applicantId = user.get("id"))
            response = []
            for ticket in queryset:
                response.append(TicketSerializer(ticket).data)
            return Response(response, status=status.HTTP_200_OK)
        if (IsExpert().has_permission(request, self)):
            user = UserSerializer(request.user).data
            queryset = Ticket.objects.filter(expertId = user.get("id"))
            response = []
            for ticket in queryset:
                response.append(TicketSerializer(ticket).data)
            return Response(response, status=status.HTTP_200_OK)
        if (IsAdmin().has_permission(request, self)):
            user = UserSerializer(request.user).data
            queryset = Ticket.objects.all()
            response = []
            for ticket in queryset:
                response.append(TicketSerializer(ticket).data)
            return Response(response, status=status.HTTP_200_OK)
            # queryset = Ticket.objects.filter(applicantId = )
        return Response({"msg": "failed"}, status=status.HTTP_400_BAD_REQUEST)
    # tickets = Ticket.object.all()


@api_view(['GET'])
def get_routes(request):
    """returns a view containing all the possible routes"""
    routes = [
        '/api/token',
        '/api/token/refresh'
    ]

    return Response(routes)