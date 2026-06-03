"""
URL configuration for Pujcovna project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from knihovna.views import home, my_reservations, register, restaurant_list, restaurant_detail, reservation_list

urlpatterns = [
    path('', home, name='home'),
    path('restaurace/', restaurant_list, name='restaurant_list'),
    path('restaurace/<int:pk>/', restaurant_detail, name='restaurant_detail'),
    path("rezervace/<int:pk>/", reservation_list, name="rezervace"),
    path("moje-rezervace/", my_reservations, name="my_reservations"),
    path("registrace/", register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="register/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="restaurant_list"), name="logout"),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
