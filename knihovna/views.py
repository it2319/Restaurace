from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings
import os

from .models import Restaurace, Oteviraci_doba, Rezervace
from .forms import RegistrationForm, ReservationForm


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

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("restaurant_list")
    else:
        form = RegistrationForm()

    return render(request, "register/register.html", {
        "form": form,
    })

@login_required
def reservation_list(request, pk):
    restaurant = get_object_or_404(Restaurace, pk=pk)
    customer = getattr(request.user, "zakaznik", None)
    if customer is None:
        messages.error(request, "Pro vytvoření rezervace potřebujete zákaznický účet.")
        return redirect("register")

    if request.method == "POST":
        form = ReservationForm(request.POST, restaurant=restaurant)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.zakaznik = customer
            reservation.save()
            return redirect("my_reservations")
    else:
        form = ReservationForm(restaurant=restaurant)

    return render(request, "reservations/rezervace.html", {
        "restaurant": restaurant,
        "form": form,
    })

@login_required
def my_reservations(request):
    customer = getattr(request.user, "zakaznik", None)
    if customer is None:
        reservations = Rezervace.objects.none()
        return render(request, "reservations/moje_rezervace.html", {
            "reservations": reservations,
        })

    reservations = Rezervace.objects.filter(
        zakaznik=customer,
    ).select_related("stul", "stul__Restaurace").order_by("-datum_cas")

    return render(request, "reservations/moje_rezervace.html", {
        "reservations": reservations,
    })
