from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReservamedicaViewSet, PacientesViewSet
from . import views

router = DefaultRouter()
router.register(r'reservamedica', ReservamedicaViewSet)
router.register(r'pacientes', PacientesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reservamedica/<int:cita_id>/', views.cancelar_cita, name='cancelar_cita'),
    path('reservamedica/<int:cita_id>/editar/', views.editar_cita, name='editar_cita'),
    
]