from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from .models import *
from django.contrib.auth import authenticate, logout, login
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
import requests
from django.http import JsonResponse
import datetime
from rest_framework import generics
from .models import Pacientes, Doctores



# Create your views here.

def homepage(request):
    # Realizar las solicitudes a la API para obtener los tipos de cambio
    url_usd_to_clp = "https://currency-exchange.p.rapidapi.com/exchange"
    querystring_usd_to_clp = {"to": "CLP", "from": "USD", "q": "1.0"}

    url_eur_to_clp = "https://currency-exchange.p.rapidapi.com/exchange"
    querystring_eur_to_clp = {"to": "CLP", "from": "EUR", "q": "1.0"}

    url_gbp_to_clp = "https://currency-exchange.p.rapidapi.com/exchange"
    querystring_gbp_to_clp = {"to": "CLP", "from": "GBP", "q": "1.0"}

    headers = {
        'x-rapidapi-key': "41f470e399msh6bdef2065df4998p1d1699jsn19afd236e8dc",
        'x-rapidapi-host': "currency-exchange.p.rapidapi.com"
    }

    # Obtener el tipo de cambio de USD a CLP
    response_usd_to_clp = requests.get(url_usd_to_clp, headers=headers, params=querystring_usd_to_clp)
    exchange_data_usd_to_clp = response_usd_to_clp.json() if response_usd_to_clp.status_code == 200 else None

    # Obtener el tipo de cambio de EUR a CLP
    response_eur_to_clp = requests.get(url_eur_to_clp, headers=headers, params=querystring_eur_to_clp)
    exchange_data_eur_to_clp = response_eur_to_clp.json() if response_eur_to_clp.status_code == 200 else None

    # Obtener el tipo de cambio de GBP a CLP
    response_gbp_to_clp = requests.get(url_gbp_to_clp, headers=headers, params=querystring_gbp_to_clp)
    exchange_data_gbp_to_clp = response_gbp_to_clp.json() if response_gbp_to_clp.status_code == 200 else None

    # Realizar la solicitud a la API de World Clock
    url_world_clock = "https://world-clock.p.rapidapi.com/json/est/now"
    headers_world_clock = {
        "x-rapidapi-key": "41f470e399msh6bdef2065df4998p1d1699jsn19afd236e8dc",
        "x-rapidapi-host": "world-clock.p.rapidapi.com"
    }
    response_world_clock = requests.get(url_world_clock, headers=headers_world_clock)
    
    # Verificar si la solicitud fue exitosa y si hay datos
    if response_world_clock.status_code == 200:
        world_clock_data = response_world_clock.json()
        # Mapear las claves del diccionario de la API de World Clock a nombres más fáciles de usar
        mapped_world_clock_data = {
            "currentDateTime": world_clock_data.get("currentDateTime", ""),
            "utcOffset": world_clock_data.get("utcOffset", ""),
            "isDayLightSavingsTime": world_clock_data.get("isDayLightSavingsTime", ""),
            "dayOfTheWeek": world_clock_data.get("dayOfTheWeek", ""),
            "timeZoneName": world_clock_data.get("timeZoneName", "")
        }
    else:
        mapped_world_clock_data = {
            "currentDateTime": "N/A",
            "utcOffset": "N/A",
            "isDayLightSavingsTime": "N/A",
            "dayOfTheWeek": "N/A",
            "timeZoneName": "N/A"
        }

    return render(request, 'homepage.html', {
        'exchange_data_usd_to_clp': exchange_data_usd_to_clp,
        'exchange_data_eur_to_clp': exchange_data_eur_to_clp,
        'exchange_data_gbp_to_clp': exchange_data_gbp_to_clp,
        'world_clock_data': mapped_world_clock_data
    })


def aboutpage(request):
	return render(request, 'about.html')


def createaccountpage(request):
    d = {}
    error = ""
    user = "none"
    if request.method == 'POST':
        nombre = request.POST['nombre']
        email = request.POST['email']
        password = request.POST['password']
        repeatpassword = request.POST['repeatpassword']
        sexo = request.POST['sexo']
        telefono = request.POST['telefono']
        direccion = request.POST['direccion']
        fechanac = request.POST['fechanac']
        gruposanguineo = request.POST['gruposanguineo']

        try:
            if password == repeatpassword:
                Pacientes.objects.create(nombre=nombre, email=email, sexo=sexo, telefono=telefono,
                                         direccion=direccion, fechanac=fechanac, gruposanguineo=gruposanguineo)
                user = User.objects.create_user(
                    first_name=nombre, email=email, password=password, username=email)
                pat_group = Group.objects.get(name='Pacientes')
                pat_group.user_set.add(user)
                d['error'] = "no"
            else:
                d['error'] = "yes"
        except Exception as e:
            d['error'] = "yes"
            # Aquí puedes imprimir o registrar la excepción si es necesario
            print(e)

    return render(request, 'createaccount.html', d)

def login_recovery(request):
	    return render(request, 'login_recovery.html')

def loginpage(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        # Verificar si el email existe en la base de datos de doctores
        doctor = Doctores.objects.filter(email=email).first()
        if doctor and doctor.password == password:
            # Autenticar al usuario como doctor
            user = authenticate(request, username=email, password=password)
            if user is None:
                # Verificar si el usuario ya existe en la base de datos de Django
                if not User.objects.filter(email=email).exists():
                    # Crear un nuevo usuario de Django si el doctor existe en la base de datos pero no en la de usuarios
                    user = User.objects.create_user(username=email, email=email, password=password)
                else:
                    # Si el usuario ya existe, obtenerlo
                    user = User.objects.get(email=email)
                # Asociar el usuario con el doctor
                doctor.user = user
                doctor.save()
            # Iniciar sesión al usuario
            login(request, user)
            # Redirigir al usuario a la página de inicio de doctores
            return redirect('doctorhome')
        
        # Verificar si el email existe en la base de datos de pacientes
        paciente = Pacientes.objects.filter(email=email).first()
        if paciente and paciente.password == password:
            # Autenticar al usuario como paciente
            user = authenticate(request, username=email, password=password)
            if user is None:
                # Verificar si el usuario ya existe en la base de datos de Django
                if not User.objects.filter(email=email).exists():
                    # Crear un nuevo usuario de Django si el paciente existe en la base de datos pero no en la de usuarios
                    user = User.objects.create_user(username=email, email=email, password=password)
                else:
                    # Si el usuario ya existe, obtenerlo
                    user = User.objects.get(email=email)
            # Iniciar sesión al usuario
            login(request, user)
            # Redirigir al usuario a la página de inicio de pacientes
            return redirect('patienthomepage')

        # Contraseña incorrecta o email no encontrado en ninguna base de datos
        messages.error(request, 'Credenciales inválidas. Por favor, inténtalo de nuevo o regístrate si eres un nuevo usuario.')

    return render(request, 'login.html')


    
   
       

def patienthomepage(request):
    if request.user.is_authenticated:
        paciente = Pacientes.objects.filter(email=request.user.email).first()
        if paciente:
            return render(request, 'patienthomepage.html', {'paciente': paciente})
        else:
            messages.error(request, 'No se encontró un paciente con este correo electrónico.')
            return redirect('loginpage')
    else:
        return redirect('loginpage')





def patientprofile(request):
    
    paciente = Pacientes.objects.get(email=request.user.email)

    if request.method == 'POST':
        # Actualizar los datos del paciente
        paciente.nombre = request.POST.get('nombre', paciente.nombre)
        paciente.password = request.POST.get('password', paciente.password)
        paciente.sexo = request.POST.get('sexo', paciente.sexo)
        paciente.telefono = request.POST.get('telefono', paciente.telefono)
        paciente.direccion = request.POST.get('direccion', paciente.direccion)
        paciente.fechanac = request.POST.get('fechanac', paciente.fechanac)
        paciente.gruposanguineo = request.POST.get('gruposanguineo', paciente.gruposanguineo)
        paciente.save()
        return redirect('patientprofile')

    # Obtener el detalle del paciente
    return render(request, 'patientprofile.html', {'patient_details': paciente})


def patientmakeappointments(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        doctoremail = request.POST.get('doctoremail')
        doctorspecialization = request.POST.get('doctorspecialization')
        patientname = request.POST.get('patientname')
        patientemail = request.POST.get('patientemail')
        appointmentdate = request.POST.get('appointmentdate')
        appointmenttime = request.POST.get('appointmenttime')
        symptoms = request.POST.get('symptoms')

        try:
            # Obtener el nombre del doctor utilizando su correo electrónico
            doctor = Doctores.objects.get(email=doctoremail)
            doctornombre = doctor.nombre

            # Crear una nueva reserva médica
            reservation = Reservamedica.objects.create(
                doctornombre=doctornombre,
                doctoremail=doctoremail,
                pacientenombre=patientname,
                pacienteemail=patientemail,
                citamedicafecha=appointmentdate,
                citamedicahora=appointmenttime,
                sintomas=symptoms,
                status=False  # Por defecto, la cita no está confirmada
            )
            messages.success(request, 'Cita médica creada exitosamente.')
            return redirect('patientmakeappointments')  # Redirigir a la misma página después de enviar el formulario
        except Exception as e:
            messages.error(request, 'Ocurrió un error al crear la cita médica.')
            print(e)  # Imprimir el error en la consola para debug

    # Obtener la lista de todos los doctores para mostrar en el formulario
    alldoctors = Doctores.objects.all()
    return render(request, 'patientmakeappointments.html', {'alldoctors': alldoctors})


def patientviewappointments(request):
    # Obtener todas las citas médicas
    citas = Reservamedica.objects.all()
    return render(request, 'patientviewappointments.html', {'citas': citas})

def doctorhome(request):
    if request.user.is_authenticated:
        # Obtener el doctor basado en el correo electrónico del usuario autenticado
        doctor = Doctores.objects.filter(email=request.user.email).first()
        if doctor:
            return render(request, 'doctorhome.html', {'doctor_details': doctor})
        else:
            messages.error(request, 'No se encontró un doctor con este correo electrónico.')
            return redirect('loginpage')
 

def doctorprofile(request):
	return render(request, 'doctorprofile.html')

def doctorviewappointments(request):
	return render(request, 'doctorviewappointments.html')


def recuperar_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Verificar si el correo electrónico existe en la base de datos
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Si el correo electrónico no existe, devuelve un mensaje de error
            return JsonResponse({'success': False, 'message': 'El correo electrónico proporcionado no está registrado.'})

        # Verificar si las contraseñas coinciden
        if new_password1 != new_password2:
            return JsonResponse({'success': False, 'message': 'Las contraseñas no coinciden. Por favor, vuelve a ingresarlas.'})

        # Actualizar la contraseña directamente en el campo 'password'
        user.password = new_password1
        user.save()

        # Devolver una respuesta exitosa
        return JsonResponse({'success': True, 'message': 'La contraseña se ha cambiado correctamente.'})

    return JsonResponse({'success': False, 'message': 'El método de solicitud no es válido.'})


