from django.urls import path, include
from . import views
from .views import *
from django.views.generic import TemplateView
from .views import opcVisualFRM

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'Usuario', views.UsuarioViewSet)
router.register(r'UsuarioRespuesta', views.UsuarioRespuestaViewSet)
router.register(r'MensajeContenido', views.MensajeContenidoViewSet)

urlpatterns = [
    path('', views.home),
    path('home/', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('reportes/', views.reportes, name='reportes'),
    path('logout/', views.logout , name='logout'),
    #path('formulario/', views.formulario, name='formulario'),

    
    # Respuestas
    path('respuestas/', views.respuestasHome, name='respuestasHome'),
    path('datosPerfil/', views.datosPerfil, name='datosPerfil'),
    path('datosPreguntas/', views.datosPreguntas, name='datosPreguntas'),
    path('datosListadoOrdenado/', views.datosListadoOrdenado, name='datosListadoOrdenado'),
    path('opcVisualFRM/', views.opcVisualFRM, name='opcVisualFRM'),
    path('opcVisualFRNM/', views.opcVisualFRNM, name='opcVisualFRNM'),
    path('opcVisualDS/', views.opcVisualDS, name='opcVisualDS'),

    # Preguntas
    path('listarPreguntas/', views.listarPreguntas, name='listarPreguntas'),
    path('modificarPregunta/<id>/', views.modificarPregunta, name='modificarPregunta'),
    path('eliminarPregunta/<id>/', views.eliminarPregunta, name='eliminarPregunta'),
    path('crearPregunta/', views.crearPregunta, name='crearPregunta'),

    # Descargar Excel
    path('descargar_excel/', views.descargar_excel, name='descargar_excel'),
    path('crear_excel_listado_ordenable/', views.crear_excel_listado_ordenable, name='crear_excel_listado_ordenable'),
    path('crear_excel_datos_preguntas/', views.crear_excel_datos_preguntas, name='crear_excel_datos_preguntas'),
   
    # Mensajes
    path('home_mensajes/', views.homeMensajes, name='mensajesHome'),
    path('crearMensaje/', views.crearMensaje, name='crearMensaje'),
    path('modificarMensaje/<id>/', views.modificarMensaje, name='modificarMensaje'),
    path('eliminarMensaje/<id>/', views.eliminarMensaje, name='eliminarMensaje'),

    # API
    path('api/', include(router.urls)),
    path('apiHome/', apiHome, name='apiHome'),
    path('obtener-id/', ObtenerID.as_view(), name='obtener_id'),    
    path('api_usuario/', UsuarioAPIView.as_view(), name='api_usuario'),
    path('api_respuesta/', UsuarioRespuestaAPIView.as_view(), name='api_respuesta'),
    path('api_mensaje/', MensajeContenidoAPIView.as_view(), name='api_mensaje'),


    #ver si respuesta existe
    path('existe-respuesta/', views.consultar_estado_pregunta, name='existe_respuesta'),
    #path('retorna_genero/', views.retorna_genero, name='retorna_genero'),
    path('verificar_usuario/', views.verificar_usuario, name='verificar_usuario'),
]