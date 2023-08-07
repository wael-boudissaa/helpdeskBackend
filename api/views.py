from django.shortcuts import render
from passlib.hash import pbkdf2_sha256

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
            queryset = Ticket.objects.filter(applicantId=user.get("id")).order_by(
                "-creationDate"
            )
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
            queryset = Ticket.objects.filter(expertId=user.get("id")).order_by(
                "-creationDate"
            )
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
            queryset = Ticket.objects.all().order_by("-creationDate")
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

    def delete(self, request, pk, format=None):
        if IsAdmin().has_permission(request, self):
            try:
                ticket = Ticket.objects.get(idTicket=pk)
                ticket.etat = "archived"
                ticket.save()
                return Response({"msg": "succed"}, status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({"msg": "Err"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk, format=None):
        if IsAdmin().has_permission(request, self):
            try:
                ticket = Ticket.objects.get(idTicket=pk)
            except Ticket.DoesNotExist:
                return Response(
                    {"msg": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND
                )
            expertUsername = request.data.get("expertId")
            if expertUsername is None:
                return Response(
                    {"msg": "Expert Id is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Update the specific field of the ticket
            user = User.objects.get(username=expertUsername)
            ticket.expertId = user.expert  # Replace "value" with the new value
            ticket.save()
            return Response({"msg": "Success"}, status=status.HTTP_200_OK)
        elif IsExpert().has_permission(request, self):
            try:
                ticket = Ticket.objects.get(idTicket=pk)
                ticket.etat = "validated"
                ticket.save()
                return Response({"msg": "succed"}, status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({"msg": "Err"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(
                {"msg": "Not authorised"}, status=status.HTTP_401_UNAUTHORIZED
            )


class ProfileApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if IsAdmin().has_permission(request, self):
            user_id = request.user.id
            users = User.objects.all().order_by("-date_joined")
            user_type = ""
            Job = ""
            userList = []
            for user in users:
                dataUser = UserSerializer(user).data
                userid = dataUser["id"]
                experts = Expert.objects.filter(user_id=userid)
                applicants = Applicant.objects.filter(user_id=userid)
                if len(experts) > 0:
                    Job = ExpertSerializer(experts[0]).data.get("domaine_expertise")
                    user_type = "expert"
                    dataUser.update({"type": user_type, "job": Job})

                elif len(applicants) > 0:
                    Job = ApplicantSerializer(applicants[0]).data.get("job_title")
                    user_type = "applicant"
                    dataUser.update({"type": user_type, "job": Job})
                else:
                    dataUser.update({"type": "", "job": ""})
                userList.append(dataUser)
        else:
            Response({"msg : Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(userList, status=status.HTTP_202_ACCEPTED)

    def post(self, request, pk=None):
        if IsAdmin().has_permission(request, self):
            username = request.data.get("username")
            first_name = request.data.get("first_name")
            second_name = request.data.get("second_name")
            job = request.data.get("job")
            user_type = request.data.get("type")
            email = request.data.get("email")
            password = request.data.get("password")
            # hashed_password = pbkdf2_sha256.using(
            #     rounds=600000, salt="5pBl2k****************"
            # ).hash(password)
      
            user_defaults = {
                "first_name": first_name,
                "last_name": second_name,
                "email": email,
            }
            existing_user, created = User.objects.get_or_create(
                username=username, defaults=user_defaults
            )

            if created:
                existing_user.set_password(password)
                existing_user.save()
                if user_type == "expert":
                    expert = Expert.objects.create(
                        user=existing_user, domaine_expertise=job
                    )
                elif user_type == "applicant":
                    applicant = Applicant.objects.create(
                        user=existing_user, job_title=job
                    )
                else:
                    return Response(
                        {"err": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
                    )

                return Response({"msg": "success"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"err": "Username already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"err": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["GET"])
def get_routes(request):
    """returns a view containing all the possible routes"""
    routes = ["/api/token", "/api/token/refresh"]

    return Response(routes)
