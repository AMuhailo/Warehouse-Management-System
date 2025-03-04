from django.urls import path
from . import views

app_name = 'emp'

urlpatterns = [
    path('profile/update/<username>/', views.ProfileUpdateView.as_view(), name = 'profile_update_url')
]
