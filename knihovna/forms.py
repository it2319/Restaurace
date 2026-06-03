from datetime import timedelta

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Adresa, Mesto, Rezervace, Stat, Stoly, Zakaznik


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Jméno", max_length=100)
    last_name = forms.CharField(label="Příjmení", max_length=100)
    email = forms.EmailField(label="E-mail")
    ulice = forms.CharField(label="Ulice", max_length=100)
    psc = forms.CharField(label="PSČ", max_length=10)
    mesto = forms.CharField(label="Město", max_length=100)
    stat = forms.CharField(label="Stát", max_length=100, initial="Česká republika")

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "ulice",
            "psc",
            "mesto",
            "stat",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
            stat, _ = Stat.objects.get_or_create(nazev=self.cleaned_data["stat"])
            mesto, _ = Mesto.objects.get_or_create(
                nazev=self.cleaned_data["mesto"],
                stat=stat,
            )
            adresa = Adresa.objects.create(
                ulice=self.cleaned_data["ulice"],
                psc=self.cleaned_data["psc"],
                mesto=mesto,
            )
            Zakaznik.objects.create(
                user=user,
                jmeno=user.first_name,
                prijmeni=user.last_name,
                email=user.email,
                adresa=adresa,
            )

        return user


class ReservationForm(forms.ModelForm):
    datum_cas = forms.DateTimeField(
        label="Datum a čas",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )
    delka_hodin = forms.ChoiceField(
        label="Délka trvání",
        choices=((1, "1 hodina"), (2, "2 hodiny"), (3, "3 hodiny")),
    )

    class Meta:
        model = Rezervace
        fields = ("stul", "datum_cas", "delka_hodin", "pocet_osob", "poznamka")
        labels = {
            "stul": "Stůl",
            "pocet_osob": "Počet osob",
            "poznamka": "Poznámka",
        }
        widgets = {
            "poznamka": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if restaurant is not None:
            self.fields["stul"].queryset = Stoly.objects.filter(Restaurace=restaurant)

    def save(self, commit=True):
        reservation = super().save(commit=False)
        reservation.delka_trvani = timedelta(hours=int(self.cleaned_data["delka_hodin"]))
        if commit:
            reservation.save()
            reservation.stul.stav = "rezervovany"
            reservation.stul.save()
        return reservation
