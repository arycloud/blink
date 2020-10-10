from django.urls import path
from .views import login_user, logout_user, registration_view, user_profile

app_name = 'users'

urlpatterns = [
    path('login', login_user, name='login'),
    path('logout', logout_user, name='logout'),
    path('profile', user_profile, name='profile'),
    path('register', registration_view, name='register')
]
