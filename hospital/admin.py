from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Pacientes)
admin.site.register(Doctores)
admin.site.register(Administrador)
admin.site.register(Reservamedica)