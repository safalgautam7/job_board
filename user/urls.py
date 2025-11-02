from django.urls import path
from .views import UserManagementView, UserLoginView, UserLogOutView


urlpatterns = [
    path('', UserManagementView.as_view(), name='user-management'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogOutView.as_view(), name='logout'),
]