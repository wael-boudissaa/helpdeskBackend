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
                ticketAlone = TicketSerializer(ticket).data
                users = User.objects.filter(id = ticketAlone.get("expertId"))
                experts = Expert.objects.filter(user_id = ticketAlone.get("expertId"))
                if (len(experts) > 0):
                 expertName = UserSerializer(users[0]).data.get("username")
                 expertJob = ExpertSerializer(experts[0]).data.get("domaine_expertise")
                 ticketAlone.update({"username" : expertName, "jobtitle":expertJob})
                 
                else : 
                 ticketAlone.update({"username" : "Ticket not Affected Yet"})
                response.append(ticketAlone)
            return Response(response, status=status.HTTP_200_OK)
        if (IsExpert().has_permission(request, self)):
            user = UserSerializer(request.user).data
            queryset = Ticket.objects.filter(expertId = user.get("id"))
            response = []
            for ticket in queryset:
                ticketAlone = TicketSerializer(ticket).data
                users =User.objects.filter(id=ticketAlone.get("applicantId"))
                applicants =Applicant.objects.filter(user_id = ticketAlone.get("applicantId"))
                username =UserSerializer(users[0]).data.get("username")
                jobtitle=ApplicantSerializer(applicants[0]).data.get("job_title")
                ticketAlone.update({"username":username,"jobtitle":jobtitle})
                response.append(ticketAlone)
            return Response(response, status=status.HTTP_200_OK)
        if (IsAdmin().has_permission(request, self)):
            user = UserSerializer(request.user).data
            queryset = Ticket.objects.all()
            response = []
            for ticket in queryset:
                ticketAlone = TicketSerializer(ticket).data
                expertUsers = User.objects.filter(id = ticketAlone.get("expertId"))
                experts = Expert.objects.filter(user_id = ticketAlone.get("expertId"))
                users =User.objects.filter(id=ticketAlone.get("applicantId"))
                applicants =Applicant.objects.filter(user_id = ticketAlone.get("applicantId"))
                username =UserSerializer(users[0]).data.get("username")
                jobtitle=ApplicantSerializer(applicants[0]).data.get("job_title")
                if (len(experts) > 0):
                 expertName = UserSerializer(expertUsers[0]).data.get("username")
                 expertJob = ExpertSerializer(experts[0]).data.get("domaine_expertise")
                 ticketAlone.update({"username": username, "jobtitle": jobtitle, "expertname": expertName, "expertjob": expertJob })
                else : 
                 ticketAlone.update({"expertname" : "Ticket not Affected Yet","username": username, "jobtitle": jobtitle,})
                response.append(ticketAlone)
            return Response(response, status=status.HTTP_200_OK)
        return Response({"msg": "failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_routes(request):
    """returns a view containing all the possible routes"""
    routes = [
        '/api/token',
        '/api/token/refresh'
    ]

    return Response(routes)