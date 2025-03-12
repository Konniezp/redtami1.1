from django.urls import path, include
from . import views
from .views import *
from django.views.generic import TemplateView
from .views import opcVisualFRM

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'Usuario', views.UsuarioViewSet)
router.register(r'UsuarioRespuesta', views.UsuarioRespuestaViewSet)
router.register(r'UsuarioTextoPregunta', views.UsuarioTextoPreguntaViewSet)
router.register(r'MensajeContenido', views.MensajeContenidoViewSet)
router.register(r'FRNM', views.FRNMViewSet)
router.register(r'FRM', views.FRMViewSet)
router.register(r'DS', views.DSViewSet)
router.register(r'RespTextoFRM', views.RespTextoFRMViewSet)


urlpatterns = [
    path('', views.home),
    path('home/', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('reportes/', views.reportes, name='reportes'),
    path('formulario/', views.formulario, name='formulario'),
    
    # Respuestas
    path('respuestas/', views.respuestasHome, name='respuestasHome'),
    path('datosPerfil/', views.datosPerfil, name='datosPerfil'),
    path('datosPreguntas/', views.datosPreguntas, name='datosPreguntas'),
    path('datosTextoPreguntas/', views.datosTextoPreguntas, name='datosTextoPreguntas'),
    path('datosListadoOrdenado/', views.datosListadoOrdenado, name='datosListadoOrdenado'),
    path('datosFRM/', views.datosFRM, name='datosFRM'),
    path('datosFRM2/', views.datosFRM2, name='datosFRM2'),
    path('datosFRNM/', views.datosFRNM, name='datosFRNM'),
    path('datosFRNM2/', views.datosFRNM2, name='datosFRNM2'),
    path('datosDS/', views.datosDS, name ='datosDS'),
    path('datosDS2/', views.datosDS2, name ='datosDS2'),
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
    path('crear_excel_mod_V1/', views.crear_excel_mod_V1, name='crear_excel_mod_V1'),
    path('crear_excel_mod_V2/', views.crear_excel_mod_V2, name='crear_excel_mod_V2'),
    path('crear_excel_no_mod_V1/', views.crear_excel_no_mod_V1, name='crear_excel_no_mod_V1'),
    path('crear_excel_no_mod_V2/', views.crear_excel_no_mod_V2, name='crear_excel_no_mod_V2'),
    path('crear_excel_DS1/', views.crear_excel_DS1, name="crear_excel_DS1"),
    path('crear_excel_DS2/', views.crear_excel_DS2, name="crear_excel_DS2"),
    path('crear_excel_datos_preguntas/', views.crear_excel_datos_preguntas, name='crear_excel_datos_preguntas'),
    path('crear_excel_preguntas_esp/', views.crear_excel_preguntas_esp, name='crear_excel_preguntas_esp'),
   
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
    path('api_pregunta/', UsuarioTextoPreguntaAPIView.as_view(), name='api_pregunta'),
    path('api_respuesta/', UsuarioRespuestaAPIView.as_view(), name='api_respuesta'),
    path('api_mensaje/', MensajeContenidoAPIView.as_view(), name='api_mensaje'),


    #ver si respuesta existe
    path('existe-respuesta/', views.consultar_estado_pregunta, name='existe_respuesta'),
    path('retorna_genero/', views.retorna_genero, name='retorna_genero'),
    path('verificar_usuario/', views.verificar_usuario, name='verificar_usuario'),
]