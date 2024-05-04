from rest_framework import serializers
from .models import Pacientes, Reservamedica



class PacientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pacientes
        fields = '__all__'

class ReservamedicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservamedica
        fields = '__all__'