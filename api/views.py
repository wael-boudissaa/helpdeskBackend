import json

from django.core.serializers import serialize
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import *
from .permissions import *
from .serializers import *


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


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
                notifications = Notification.objects.filter(idTicket=ticketAlone.get("idTicket"), reason="expert to applicant")
                if (len(notifications)>0): ticketAlone.update({"newMessage": True})
                else: ticketAlone.update({"newMessage": False})
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
                notifications = Notification.objects.filter(idTicket=ticketAlone.get("idTicket"),reason="applicant to expert")
                if (len(notifications)>0): ticketAlone.update({"newMessage": True})
                else: ticketAlone.update({"newMessage": False})
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
                createdTicket = Ticket.objects.create(
                                    priority=serializer.data.get("priority"),
                                    issue=serializer.data.get("issue"),
                                    category=serializer.data.get("category"),
                                    applicantId=users[0].applicant,
                                )
                Notification.objects.create(
                         idTicket =  createdTicket,
                         reason = "ticket added"

                )
                return Response({"idTicket": createdTicket.idTicket}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"msg": "A required field missing"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"msg": "Unauthorised"}, status=status.HTTP_403_FORBIDDEN
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
        else: return Response({"msg": "unauthorised"}, status=status.HTTP_403_FORBIDDEN)

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
                {"msg": "Not authorised"}, status=status.HTTP_403_FORBIDDEN
            )


class MessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, resquest, idTicket=None, format=None):
        if IsAdmin().has_permission(resquest, self):
            return Response(
                {"msg": "Not authorised"}, status=status.HTTP_403_FORBIDDEN
            )
        serializer = PostMessageSerializer(data=resquest.data)
        if serializer.is_valid():
            try:
                ticket = Ticket.objects.get(
                    idTicket=serializer.validated_data.get("idTicket")
                )
            except Ticket.DoesNotExist:
                return Response(
                    {"msg": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND
                )
            try:
                user = User.objects.get(username=resquest.user.username)
            except User.DoesNotExist:
                return Response(
                    {"msg": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
            Message.objects.create(
                idTicket=ticket, text=serializer.data.get("text"), source=user
            )
            
            if (hasattr(resquest.user, "applicant")):
                Notification.objects.create(
                    idTicket = serializer.validated_data.get("idTicket"),
                    reason = "applicant to expert"
                ) 
            else:
                Notification.objects.create(
                    idTicket = serializer.validated_data.get("idTicket"),
                    reason = "expert to applicant"
                )
            return Response(
                {"msg": "message well saved"}, status=status.HTTP_201_CREATED
            )
        return Response({"msg": "Unvalid data"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, idTicket=None, format=None):
        if idTicket is not None:
            queryset = Message.objects.filter(idTicket=idTicket).order_by(
                "creationDate"
            )
            return Response(
                MessageSerializer(queryset, many=True).data, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"msg": "Ticket Id is required"}, status=status.HTTP_400_BAD_REQUEST
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
            Response({"msg : Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

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
                        {"err": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN
                    )

                return Response({"msg": "success"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"err": "Username already exists"},
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
        else:
            return Response(
                {"err": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN
            )


class NotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, idTicket=None):
        if IsAdmin().has_permission(request, self):
         return Response({"msg": "unauthorised"}, status=status.HTTP_403_FORBIDDEN)
        elif (IsExpert().has_permission(request,self)) : 
            try:
                notifications = Notification.objects.filter(idTicket=idTicket,reason="applicant to expert")
                for notification in notifications : 
                    notification.delete()
                return Response({"msg": "succed"}, status=status.HTTP_200_OK)
            except:
                return Response({"msg": "Err"}, status=status.HTTP_404_NOT_FOUND)
        else: 
            try:
                notifications = Notification.objects.filter(idTicket=idTicket,reason="expert to applicant")
                for notification in notifications : 
                    notification.delete()
                return Response({"msg": "succed"}, status=status.HTTP_200_OK)
            except:
                return Response({"msg": "Err"}, status=status.HTTP_404_NOT_FOUND)

class ExpertsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if IsAdmin().has_permission(request, self):
            users = User.objects.all().order_by("-date_joined")
            domaine_expertise = ""
            userList = []
            for user in users:
                dataUser = UserSerializer(user).data
                userid = dataUser["id"]
                experts = Expert.objects.filter(user_id=userid)
                if len(experts) > 0:
                    domaine_expertise = ExpertSerializer(experts[0]).data.get("domaine_expertise")
                    dataUser.update({"domaine_expertise": domaine_expertise})
                    userList.append(dataUser)
                else : 
                    pass 
        else:
            return Response({"msg : Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        return Response(userList, status=status.HTTP_202_ACCEPTED)     
@api_view(["GET"])
def get_routes(request):
    """returns a view containing all the possible routes"""
    routes = ["/api/token", "/api/token/refresh"]

    return Response(routes)
