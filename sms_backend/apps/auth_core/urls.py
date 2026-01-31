"""
URL configuration for auth_core app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.logout_view, name='logout'),
    
    # User profile
    path('me/', views.me_view, name='me'),
    
    # Password management
    path('password/change/', views.change_password_view, name='change_password'),
    path('password/reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password/reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # User management (admin)
    path('users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail'),
]
