from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.

class Pacientes(models.Model):
    nombre = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=16)
    sexo = models.CharField(max_length=10)
    telefono = models.CharField(max_length=10)
    direccion = models.CharField(max_length=100)
    fechanac = models.DateField()
    gruposanguineo = models.CharField(max_length=5)
    

    def __str__(self):
        return self.nombre
    
class Doctores(models.Model):
	nombre = models.CharField(max_length=50)
	email = models.EmailField(unique=True)
	password = models.CharField(max_length=16)
	sexo = models.CharField(max_length=10)
	telefono = models.CharField(max_length=10)
	direccion = models.CharField(max_length=100)
	fechanac = models.DateField()
	especialidad = models.CharField(max_length=50)

	def __str__(self):
		return self.nombre

class Administrador(models.Model):
	nombre = models.CharField(max_length=50)
	email = models.EmailField(unique=True)
	password = models.CharField(max_length=16)
	sexo = models.CharField(max_length=10)
	telefono = models.CharField(max_length=10)
	direccion = models.CharField(max_length=100)
	fechanac = models.DateField()
	
	def __str__(self):
		return self.nombre


class Reservamedica(models.Model):
    doctornombre = models.CharField(max_length=50)
    doctoremail = models.EmailField(max_length=50)
    pacientenombre = models.CharField(max_length=50)
    pacienteemail = models.EmailField(max_length=50)
    citamedicafecha = models.DateField(max_length=10)
    citamedicahora = models.TimeField(max_length=10)
    sintomas = models.CharField(max_length=100)
    status = models.BooleanField()
	
def __str__(self):
		return self.pacientenombre+" tienes una cita con"+self.doctornombre

