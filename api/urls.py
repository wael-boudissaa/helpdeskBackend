from django.urls import path
from . import views
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("", views.get_routes),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    #path("token/check-refresh-token/", views.check_refresh_token, name="token_refresh"),
    path("tickets/", TicketsAPIView.as_view(), name="tickets"),
    path("tickets/<str:pk>", TicketsAPIView.as_view(), name="ticket"),

]
