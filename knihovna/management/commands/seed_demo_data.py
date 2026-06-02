import random
from datetime import timedelta, time

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from knihovna.models import (
    Adresa,
    Mesto,
    Oteviraci_doba,
    Restaurace,
    Rezervace,
    Stat,
    Stoly,
    Telefon,
    Zakaznik,
)


FIRST_NAMES = [
    "Jan",
    "Petr",
    "Tomáš",
    "Martin",
    "Pavel",
    "Lukáš",
    "Ondřej",
    "David",
    "Jakub",
    "Filip",
    "Tereza",
    "Lucie",
    "Jana",
    "Eliška",
    "Anna",
    "Kateřina",
    "Veronika",
    "Barbora",
    "Michaela",
    "Adéla",
]

LAST_NAMES = [
    "Novák",
    "Svoboda",
    "Novotný",
    "Dvořák",
    "Černý",
    "Procházka",
    "Kučera",
    "Veselý",
    "Horák",
    "Němec",
    "Pokorný",
    "Marek",
    "Pospíšil",
    "Hájek",
    "Jelínek",
    "Král",
    "Růžička",
    "Beneš",
    "Fiala",
    "Kříž",
]

COUNTRY_NAMES = [
    "Česká republika",
    "Slovensko",
    "Polsko",
    "Rakousko",
    "Německo",
    "Itálie",
    "Španělsko",
    "Francie",
    "Maďarsko",
    "Nizozemsko",
    "Belgie",
    "Portugalsko",
    "Řecko",
    "Chorvatsko",
    "Norsko",
    "Švédsko",
    "Finsko",
    "Dánsko",
    "Švýcarsko",
    "Slovinsko",
]

CITY_NAMES = [
    "Praha",
    "Brno",
    "Ostrava",
    "Plzeň",
    "Liberec",
    "Olomouc",
    "České Budějovice",
    "Hradec Králové",
    "Pardubice",
    "Zlín",
    "Kladno",
    "Teplice",
    "Jihlava",
    "Mladá Boleslav",
    "Karlovy Vary",
    "Ústí nad Labem",
    "Přerov",
    "Frýdek-Místek",
    "Kroměříž",
    "Tábor",
]

STREET_NAMES = [
    "Dlouhá",
    "Masarykova",
    "Hlavní",
    "Jarní",
    "Lípová",
    "Smetanova",
    "Nádražní",
    "Vrchlického",
    "Komenského",
    "Zahradní",
    "Křižíkova",
    "Žižkova",
    "Palackého",
    "Mírová",
    "Na Příkopě",
    "Ostravská",
    "Příčná",
    "Husova",
    "Legionářů",
    "Sportovní",
]

RESTAURANT_ADJECTIVES = [
    "Zlatý",
    "Modrý",
    "Klidný",
    "Starý",
    "Pohodový",
    "Královský",
    "Svěží",
    "Bílý",
    "Červený",
    "Tichý",
    "Rychlý",
    "Veselý",
    "Slunečný",
    "Voňavý",
    "Dobrý",
    "Elegantní",
    "Rodinný",
    "Rustikální",
    "Městský",
    "Dobrodružný",
]

RESTAURANT_NOUNS = [
    "Stůl",
    "Guláš",
    "Pokrm",
    "Kout",
    "Hostinec",
    "Dvorek",
    "Bistro",
    "Pivnice",
    "Gril",
    "Salon",
    "Kuchyně",
    "Talíř",
    "Chalupa",
    "Zahrádka",
    "Sedmý Smysl",
    "Báseň",
    "Řeka",
    "Mlýn",
    "Mlsná",
    "Kavárna",
]


class Command(BaseCommand):
    help = "Populate the database with fake demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="How many rows to create for each model (default: 20).",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Random seed for repeatable output.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data before seeding.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        self.random = random.Random(options["seed"])

        with transaction.atomic():
            if options["clear"]:
                self._clear_database()

            stats = [Stat.objects.create(nazev=self._country_name(index)) for index in range(count)]
            cities = [
                Mesto.objects.create(
                    nazev=self._city_name(index),
                    stat=self.random.choice(stats),
                )
                for index in range(count)
            ]
            addresses = [
                Adresa.objects.create(
                    ulice=self._street_name(index),
                    psc=self._postal_code(),
                    mesto=self.random.choice(cities),
                )
                for index in range(count)
            ]
            restaurants = [
                Restaurace.objects.create(
                    nazev=self._restaurant_name(index),
                    adresa=self.random.choice(addresses),
                )
                for index in range(count)
            ]
            customers = [
                Zakaznik.objects.create(
                    jmeno=self.random.choice(FIRST_NAMES),
                    prijmeni=self.random.choice(LAST_NAMES),
                    email=f"zakaznik{index + 1}@example.com",
                    adresa=self.random.choice(addresses),
                )
                for index in range(count)
            ]

            tables = [
                Stoly.objects.create(
                    cislo=index + 1,
                    pocet_mist=self.random.randint(2, 8),
                    Restaurace=self.random.choice(restaurants),
                    stav=self.random.choice(["volny", "rezervovany", "obsazeny"]),
                )
                for index in range(count)
            ]

            used_phone_numbers = set()
            for customer in customers:
                Telefon.objects.create(
                    cislo=self._phone_number(used_phone_numbers),
                    zakaznik=customer,
                    restaurace=self.random.choice(restaurants),
                )

            # create opening hours for each restaurant: Mon-Fri same hours, weekends different
            weekday_order = [
                "pondeli",
                "utery",
                "streda",
                "ctvrtek",
                "patek",
                "sobota",
                "nedele",
            ]
            for restaurant in restaurants:
                for den in weekday_order:
                    if den in ("pondeli", "utery", "streda", "ctvrtek", "patek"):
                        otevreno_od = time(11, 0)
                        otevreno_do = time(22, 0)
                    elif den == "sobota":
                        otevreno_od = time(10, 0)
                        otevreno_do = time(23, 0)
                    else:  # "nedele"
                        otevreno_od = time(10, 0)
                        otevreno_do = time(21, 0)
                    Oteviraci_doba.objects.create(
                        Restaurace=restaurant,
                        den=den,
                        otevreno_od=otevreno_od,
                        otevreno_do=otevreno_do,
                    )

            for index in range(count):
                table = self.random.choice(tables)
                person_count = self.random.randint(1, table.pocet_mist)
                reservation_start = timezone.now() + timedelta(
                    days=self.random.randint(-14, 30),
                    hours=self.random.randint(0, 12),
                )
                Rezervace.objects.create(
                    zakaznik=self.random.choice(customers),
                    stul=table,
                    datum_cas=reservation_start,
                    delka_trvani=timedelta(hours=self.random.choice([1, 1, 2, 2, 3])),
                    pocet_osob=person_count,
                    poznamka=self.random.choice([
                        "Stůl u okna.",
                        "Prosím tichý kout.",
                        "Bezlepkové menu.",
                        "Oslava narozenin.",
                        "Rodinná večeře.",
                        "Firemní oběd.",
                        "Rezervace potvrzena.",
                        None,
                    ]),
                )

        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} demo rows for each model."))

    def _clear_database(self):
        Rezervace.objects.all().delete()
        Oteviraci_doba.objects.all().delete()
        Telefon.objects.all().delete()
        Stoly.objects.all().delete()
        Zakaznik.objects.all().delete()
        Restaurace.objects.all().delete()
        Adresa.objects.all().delete()
        Mesto.objects.all().delete()
        Stat.objects.all().delete()

    def _country_name(self, index):
        if index < len(COUNTRY_NAMES):
            return COUNTRY_NAMES[index]
        return f"{COUNTRY_NAMES[index % len(COUNTRY_NAMES)]} {index + 1}"

    def _city_name(self, index):
        if index < len(CITY_NAMES):
            return CITY_NAMES[index]
        return f"{CITY_NAMES[index % len(CITY_NAMES)]} {index + 1}"

    def _street_name(self, index):
        street = STREET_NAMES[index % len(STREET_NAMES)]
        return f"{street} {index + 1}"

    def _restaurant_name(self, index):
        adjective = RESTAURANT_ADJECTIVES[index % len(RESTAURANT_ADJECTIVES)]
        noun = RESTAURANT_NOUNS[index % len(RESTAURANT_NOUNS)]
        return f"{adjective} {noun}"

    def _postal_code(self):
        return f"{self.random.randint(10000, 99999)}"

    def _phone_number(self, used_phone_numbers):
        while True:
            phone_number = (
                f"+420 {self.random.randint(100, 999)} "
                f"{self.random.randint(100, 999)} {self.random.randint(100, 999)}"
            )
            if phone_number not in used_phone_numbers:
                used_phone_numbers.add(phone_number)
                return phone_number
