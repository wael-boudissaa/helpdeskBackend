from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from .models import *
from rest_framework import status
import json
from django.core.serializers import serialize


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


from rest_framework_simplejwt.tokens import RefreshToken


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def check_refresh_token(request):
    token = RefreshToken(request.data["refresh"])
    is_blacklisted = token.blacklisted

    return Response({"blacklisted": is_blacklisted}, status=status.HTTP_200_OK)


class TicketsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if IsApplicant().has_permission(request, self):
            user = UserSerializer(request.user).data
            queryset = Ticket.objects.filter(applicantId=user.get("id")).order_by('-creationDate')
            response = []
            for ticket in queryset:
                ticketAlone = TicketSerializer(ticket).data
                users = User.objects.filter(id=ticketAlone.get("expertId"))
                experts = Expert.objects.filter(user_id=ticketAlone.get("expertId"))
                if len(experts) > 0:
                    expertName = UserSerializer(users[0]).data.get("username")
                    expertJob = ExpertSerializer(experts[0]).data.get(
                        "domaine_expertise"
                    )
                    ticketAlone.update({"username": expertName, "jobtitle": expertJob})

                else:
                    ticketAlone.update({"username": "Ticket not Affected Yet"})
                response.append(ticketAlone)
            return Response(response, status=status.HTTP_200_OK)
        if IsExpert().has_permission(request, self):
            user = UserSerializer(request.user).data
            queryset = Ticket.objects.filter(expertId=user.get("id")).order_by('-creationDate')
            response = []
            for ticket in queryset:
                ticketAlone = TicketSerializer(ticket).data
                users = User.objects.filter(id=ticketAlone.get("applicantId"))
                applicants = Applicant.objects.filter(
                    user_id=ticketAlone.get("applicantId")
                )
                username = UserSerializer(users[0]).data.get("username")
                jobtitle = ApplicantSerializer(applicants[0]).data.get("job_title")
                ticketAlone.update({"username": username, "jobtitle": jobtitle})
                response.append(ticketAlone)
            return Response(response, status=status.HTTP_200_OK)
        if IsAdmin().has_permission(request, self):
            user = UserSerializer(request.user).data
            queryset = Ticket.objects.all().order_by('-creationDate')
            response = []
            for ticket in queryset:
                ticketAlone = TicketSerializer(ticket).data
                expertUsers = User.objects.filter(id=ticketAlone.get("expertId"))
                experts = Expert.objects.filter(user_id=ticketAlone.get("expertId"))
                users = User.objects.filter(id=ticketAlone.get("applicantId"))
                applicants = Applicant.objects.filter(
                    user_id=ticketAlone.get("applicantId")
                )
                username = UserSerializer(users[0]).data.get("username")
                jobtitle = ApplicantSerializer(applicants[0]).data.get("job_title")
                if len(experts) > 0:
                    expertName = UserSerializer(expertUsers[0]).data.get("username")
                    expertJob = ExpertSerializer(experts[0]).data.get(
                        "domaine_expertise"
                    )
                    ticketAlone.update(
                        {
                            "username": username,
                            "jobtitle": jobtitle,
                            "expertname": expertName,
                            "expertjob": expertJob,
                        }
                    )
                else:
                    ticketAlone.update(
                        {
                            "expertname": "Ticket not Affected Yet",
                            "username": username,
                            "jobtitle": jobtitle,
                        }
                    )
                response.append(ticketAlone)
            return Response(response, status=status.HTTP_200_OK)
        return Response({"msg": "failed"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk=None):
        if IsApplicant().has_permission(request, self):
            serializer = PostTicketSerializer(data=request.data)
            if serializer.is_valid():
                users = User.objects.filter(username=request.user.username)
                Ticket.objects.create(
                    priority=serializer.data.get("priority"),
                    issue=serializer.data.get("issue"),
                    category=serializer.data.get("category"),
                    applicantId=users[0].applicant,
                )
                return Response({"msg": "success"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"msg": "A required field missing"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"msg": "Unauthorised"}, status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Start here ----------------------------------------
    def delete (self,request,deletedTicket,format=None):
        if IsAdmin().has_permission(request,self):
           
            try : 
                ticket =Ticket.objects.get(idTicket=deletedTicket)
                ticket.etat="archived"
                ticket.save()
                return Response({"msg":"succed"},status=status.HTTP_204_NO_CONTENT)
            except: 
                return Response({"msg" : "Err" } , status=status.HTTP_404_NOT_FOUND)



@api_view(["GET"])
def get_routes(request):
    """returns a view containing all the possible routes"""
    routes = ["/api/token", "/api/token/refresh"]

    return Response(routes)
