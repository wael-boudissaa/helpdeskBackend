from django.urls import path
from . import views
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("", views.get_routes),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("tickets/", TicketsAPIView.as_view(), name="tickets"),
    path("tickets/<str:pk>", TicketsAPIView.as_view(), name="ticket"),
    path("messages/", MessageAPIView.as_view(), name="messages"),
    path("messages/<str:idTicket>", MessageAPIView.as_view(), name="ticket_messages"),
    path("profiles/",ProfileApiView.as_view(),name="profile" ),
    path("experts/",ExpertsAPIView.as_view(), name="expert"),
    path("notifications/<str:idTicket>",NotificationAPIView.as_view(), name="delete_notifications")
]
