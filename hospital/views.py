from django.shortcuts import render, redirect,get_object_or_404
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
from rest_framework import viewsets
from .models import Reservamedica, Pacientes
from .serializer import ReservamedicaSerializer, PacientesSerializer
from json.decoder import JSONDecodeError
import json


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

    try:
        # Obtener el tipo de cambio de USD a CLP
        response_usd_to_clp = requests.get(url_usd_to_clp, headers=headers, params=querystring_usd_to_clp)
        exchange_data_usd_to_clp = response_usd_to_clp.json() if response_usd_to_clp.status_code == 200 else None
    except Exception as e:
        print("Error de decodificación JSON en USD a CLP:", e)
        exchange_data_usd_to_clp = None

    try:
        # Obtener el tipo de cambio de EUR a CLP
        response_eur_to_clp = requests.get(url_eur_to_clp, headers=headers, params=querystring_eur_to_clp)
        exchange_data_eur_to_clp = response_eur_to_clp.json() if response_eur_to_clp.status_code == 200 else None
    except Exception as e:
        print("Error de decodificación JSON en EUR a CLP:", e)
        exchange_data_eur_to_clp = None

    try:
        # Obtener el tipo de cambio de GBP a CLP
        response_gbp_to_clp = requests.get(url_gbp_to_clp, headers=headers, params=querystring_gbp_to_clp)
        exchange_data_gbp_to_clp = response_gbp_to_clp.json() if response_gbp_to_clp.status_code == 200 else None
    except Exception as e:
        print("Error de decodificación JSON en GBP a CLP:", e)
        exchange_data_gbp_to_clp = None

    # Realizar la solicitud a la API de World Clock
    url_world_clock = "https://world-clock.p.rapidapi.com/json/est/now"
    headers_world_clock = {
        "x-rapidapi-key": "41f470e399msh6bdef2065df4998p1d1699jsn19afd236e8dc",
        "x-rapidapi-host": "world-clock.p.rapidapi.com"
    }

    try:
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
    except Exception as e:
        print("Error al obtener la hora del mundo:", e)
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
    error = ""
    success = False  # Inicialmente el registro no ha sido exitoso
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repeatpassword = request.POST.get('repeatpassword')
        sexo = request.POST.get('sexo')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        fechanac = request.POST.get('fechanac')
        gruposanguineo = request.POST.get('gruposanguineo')

        try:
            # Validar la longitud de la contraseña
            if len(password) < 8 or len(password) > 16:
                raise ValueError("La contraseña debe tener entre 8 y 16 caracteres")

            # Validar que las contraseñas coincidan
            if password != repeatpassword:
                raise ValueError("Las contraseñas no coinciden")

            # Crear el objeto Paciente y guardarlo en la base de datos
            paciente = Pacientes(nombre=nombre, email=email, password=password, sexo=sexo,
                                 telefono=telefono, direccion=direccion, fechanac=fechanac,
                                 gruposanguineo=gruposanguineo)
            paciente.save()

            success = True  # Marcar el registro como exitoso
            return render(request, 'createaccount.html', {'success': success})  # Renderizar con éxito

        except Exception as e:
            error = str(e)

    return render(request, 'createaccount.html', {'error': error, 'success': success})



def login_recovery(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        nueva_contrasena = request.POST.get('new_password1') 
        
         # Verificar si el correo electrónico pertenece a un paciente
        try:
            paciente = Pacientes.objects.get(email=email)
            paciente.password = nueva_contrasena
            paciente.save()
            messages.success(request, 'Contraseña actualizada exitosamente para el perfil de paciente.')
            return render(request, 'login_recovery.html', {'login_recovery': paciente})
        except Pacientes.DoesNotExist:
            pass

        # Verificar si el correo electrónico pertenece a un administrador
        try:
            administrador = Administrador.objects.get(email=email)
            administrador.password = nueva_contrasena
            administrador.save()
            messages.success(request, 'Contraseña actualizada exitosamente para el perfil de administrador.')
            return render(request, 'login_recovery.html', {'login_recovery': administrador})
        except Administrador.DoesNotExist:
            pass

        # Verificar si el correo electrónico pertenece a un doctor
        try:
            doctor = Doctores.objects.get(email=email)
            doctor.password = nueva_contrasena
            doctor.save()
            messages.success(request, 'Contraseña actualizada exitosamente para el perfil de doctor.')
            return render(request, 'login_recovery.html', {'login_recovery': doctor})
        except Doctores.DoesNotExist:
            pass

        # Si el correo electrónico no corresponde a ningún perfil, mostrar un mensaje de error
        messages.error(request, 'El correo electrónico no está registrado en la base de datos.')

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
        
        
         # Verificar si el email existe en la base de datos de pacientes
        administrador = Administrador.objects.filter(email=email).first()
        if administrador and administrador.password == password:
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
            return redirect('adminhome')

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


from django.shortcuts import redirect, render

def patientprofile(request):
    paciente = Pacientes.objects.get(email=request.user.email)
    success = False  # Inicializa la variable de éxito como False

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
        success = True  # Establece la variable de éxito como True después de guardar los datos
        return redirect('patientprofile')

    # Obtener el detalle del paciente
    return render(request, 'patientprofile.html', {'patient_details': paciente, 'success': success})



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
    usuario_actual = request.user
    # Obtener todas las citas médicas
    citas = Reservamedica.objects.filter(pacienteemail=usuario_actual.email)
    # Consultar todos los doctores en la base de datos
    doctores = Doctores.objects.all()
    return render(request, 'patientviewappointments.html', {'citas': citas, 'doctores': doctores})

def doctorhome(request):
    if request.user.is_authenticated:
        # Obtener el doctor basado en el correo electrónico del usuario autenticado
        doctor = Doctores.objects.filter(email=request.user.email).first()
        if doctor:
            return render(request, 'doctorhome.html', {'doctor_details': doctor})
        else:
            messages.error(request, 'No se encontró un doctor con este correo electrónico.')
            return redirect('loginpage')
    else:
        return redirect('loginpage')
 
 
def doctorprofile(request):
    doctor = Doctores.objects.get(email=request.user.email)
    return render(request, 'doctorprofile.html', {'doctor_details': doctor})

def doctorviewappointments(request):
    usuario_actual = request.user
    # Obtener todas las citas médicas
    citas = Reservamedica.objects.filter(doctoremail=usuario_actual.email)
    # Consultar todos los doctores en la base de datos
    doctores = Doctores.objects.all()
    return render(request, 'doctorviewappointments.html', {'citas': citas, 'doctores': doctores})
	


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


class ReservamedicaViewSet(viewsets.ModelViewSet):
    queryset = Reservamedica.objects.all()
    serializer_class = ReservamedicaSerializer

class PacientesViewSet(viewsets.ModelViewSet):
    queryset = Pacientes.objects.all()
    serializer_class = PacientesSerializer


def cancelar_cita(request, cita_id):
    if request.method == 'DELETE':
        # Obtener la cita médica
        cita = get_object_or_404(Reservamedica, id=cita_id)
        # Eliminar la cita médica
        cita.delete()
        # Devolver una respuesta JSON indicando éxito
        return JsonResponse({'message': 'Cita cancelada exitosamente'}, status=200)
    else:
        # Devolver una respuesta JSON indicando error si el método de solicitud no es DELETE
        return JsonResponse({'error': 'Método de solicitud no permitido'}, status=405)
    
 

def editar_cita(request, cita_id):
    cita = get_object_or_404(Reservamedica, id=cita_id)
    
     # Consulta todos los doctores en la base de datos
    doctores = Doctores.objects.all()

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            cita.doctornombre = data.get('doctornombre', cita.doctornombre)
            cita.pacientenombre = data.get('pacientenombre', cita.pacientenombre)
            cita.citamedicafecha = data.get('citamedicafecha', cita.citamedicafecha)
            cita.citamedicahora = data.get('citamedicahora', cita.citamedicahora)
            cita.sintomas = data.get('sintomas', cita.sintomas)
            cita.save()
            return JsonResponse({'message': 'Cita actualizada exitosamente'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Los datos recibidos no son válidos'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Método de solicitud no permitido'}, status=405)
    
    
def adminhome(request):
    if request.user.is_authenticated:
        # Obtener el doctor basado en el correo electrónico del usuario autenticado
        administrador = Administrador.objects.filter(email=request.user.email).first()
        if administrador:
            return render(request, 'adminhome.html', {'admin_details': administrador})
        else:
            messages.error(request, 'No se encontró un doctor con este correo electrónico.')
            return redirect('adminpage')
    else:
        return redirect('adminhome.html')


def adminviewappointments(request):
    # Obtener la fecha actual
    today = timezone.now()
    
    # Obtener todas las citas médicas del año actual y del siguiente
    citas = Reservamedica.objects.filter(citamedicafecha__year__gte=today.year - 1).order_by('-citamedicafecha')

    
    # Obtener una lista de años únicos presentes en las citas médicas
    años = citas.values_list('citamedicafecha__year', flat=True).distinct()
    
    # Consultar todos los doctores en la base de datos
    doctores = Doctores.objects.all()
    
    return render(request, 'adminviewappointments.html', {'citas': citas, 'años': años, 'doctores': doctores})


def adminviewdoctors(request):
    if request.method == 'POST':
        # Verificar si se está realizando una solicitud de eliminación
        if 'doctor_id' in request.POST and 'doctor_email' in request.POST:
            doctor_id = request.POST.get('doctor_id')
            doctor_email = request.POST.get('doctor_email')
            try:
                doctor = Doctores.objects.get(id=doctor_id, email=doctor_email)
                doctor.delete()
                return JsonResponse({'message': 'Doctor eliminado correctamente'}, status=200)
            except Doctores.DoesNotExist:
                return JsonResponse({'error': 'No se encontró el doctor'}, status=404)
        
    # Si no es una solicitud de eliminación POST, simplemente mostrar la página con todos los doctores
    doctors = Doctores.objects.all()
    return render(request, 'adminviewdoctors.html', {'doctors': doctors})


def adminadddoctor(request):
    error = ""
    success = False

    if request.method == 'POST':
        try:
            # Procesar los datos del formulario para agregar un nuevo doctor
            nombre = request.POST.get('nombre')
            email = request.POST.get('email')
            password = request.POST.get('password')
            sexo = request.POST.get('gender')
            telefono = request.POST.get('phonenumber')
            direccion = request.POST.get('address')
            fechanac = request.POST.get('dateofbirth')
            especialidad = request.POST.get('especialidad')

            # Validar la longitud de la contraseña
            if len(password) < 8 or len(password) > 16:
                raise ValueError("La contraseña debe tener entre 8 y 16 caracteres")

            # Validar que las contraseñas coincidan
            repeatpassword = request.POST.get('repeatpassword')
            if password != repeatpassword:
                raise ValueError("Las contraseñas no coinciden")

            # Crear el objeto Doctor y guardarlo en la base de datos
            doctor = Doctores(nombre=nombre, email=email, password=password,
                                              sexo=sexo, telefono=telefono, direccion=direccion,
                                              fechanac=fechanac, especialidad=especialidad)

            doctor.save()
            success = True  # Marcar el registro como exitoso
            return render(request, 'adminadddoctor.html', {'success': success})
        except Exception as e:
            error = str(e)

    return render(request, 'adminadddoctor.html', {'error': error, 'success': success})
    



           

    