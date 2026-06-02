from django.shortcuts import render, get_object_or_404
from django.conf import settings
import os

from .models import Restaurace, Oteviraci_doba, Rezervace


def home(request):
	return render(request, "index.html")

def restaurant_list(request):
    restaurants = Restaurace.objects.all().order_by('id')

    return render(request, 'restaurants/restaurace_seznam.html', {
        'restaurants': restaurants
    })

def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurace, pk=pk)

    opening_hours = Oteviraci_doba.objects.filter(Restaurace=restaurant).order_by('den')

    return render(request, 'restaurants/restaurace_detail.html', {
        'restaurant': restaurant,
        'opening_hours': opening_hours,
    })

def reservation_list(request, pk):
    restaurant = get_object_or_404(Restaurace, pk=pk)

    reservations = Rezervace.objects.filter(stul__Restaurace=restaurant)

    return render(request, "reservations/rezervace.html", {
        "restaurant": restaurant,
        "reservations": reservations
    })