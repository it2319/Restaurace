from django.db import models

class Rezervace(models.Model):
    zakaznik = models.ForeignKey('Zakaznik', on_delete=models.CASCADE)
    stul = models.ForeignKey('Stoly', on_delete=models.CASCADE)
    datum_cas = models.DateTimeField()
    delka_trvani = models.DurationField()
    pocet_osob = models.IntegerField()
    poznamka = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Rezervace pro {self.zakaznik} na stůl {self.stul} dne {self.datum_cas} pro {self.pocet_osob} osob - {self.poznamka}"
class Oteviraci_doba(models.Model):
    Restaurace = models.ForeignKey('Restaurace', on_delete=models.CASCADE)
    den = models.CharField(max_length=20, choices=[
        ('pondeli', 'Pondělí'),
        ('utery', 'Úterý'),
        ('streda', 'Středa'),
        ('ctvrtek', 'Čtvrtek'),
        ('patek', 'Pátek'),
        ('sobota', 'Sobota'),
        ('nedele', 'Neděle')
    ])
    otevreno_od = models.TimeField()
    otevreno_do = models.TimeField()
    
    def __str__(self):
        return f"{self.Restaurace} - {self.get_den_display()}: {self.otevreno_od} - {self.otevreno_do}"

class Stoly(models.Model):
    cislo =models.IntegerField()
    pocet_mist = models.IntegerField()
    Restaurace = models.ForeignKey('Restaurace', on_delete=models.CASCADE)
    stav = models.CharField(max_length=20, choices=[
        ('volny', 'Volný'),
        ('rezervovany', 'Rezervovaný'),
        ('obsazeny', 'Obsazený')
    ])
    
    def __str__(self):
        return f"Stůl {self.cislo} - {self.pocet_mist} míst - {self.get_stav_display()}"
class Telefon(models.Model):
    cislo = models.CharField(max_length=20)
    zakaznik = models.ForeignKey('Zakaznik', on_delete=models.CASCADE)
    restaurace = models.ForeignKey('Restaurace', on_delete=models.CASCADE)

    def __str__(self):
        return self.cislo
class Restaurace(models.Model):
    nazev = models.CharField(max_length=100)
    adresa = models.ForeignKey('Adresa', on_delete=models.CASCADE)

    def __str__(self):
        return self.nazev
class Stat(models.Model):
    nazev = models.CharField(max_length=100)

    def __str__(self):
        return self.nazev

class Mesto(models.Model):
    nazev = models.CharField(max_length=100)
    stat = models.ForeignKey(Stat, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nazev}, {self.stat}"


class Adresa(models.Model):
    ulice = models.CharField(max_length=100)
    psc = models.CharField(max_length=10)
    mesto = models.ForeignKey(Mesto, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.ulice} {self.psc}, {self.mesto}"


class Zakaznik(models.Model):
    jmeno = models.CharField(max_length=100)
    prijmeni = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    adresa = models.ForeignKey(Adresa, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.jmeno} {self.prijmeni} ({self.email}) - {self.adresa}"
