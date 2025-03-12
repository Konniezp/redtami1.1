from django.contrib import admin
from .models import *


class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "id_manychat",
        "Whatsapp",
        "Referencia",
        "AnioNacimiento",
        "Comuna_Usuario",
        "Fecha_Ingreso",
        "edad",
        "fecha_nacimiento"
    )
    search_fields = (
        "id_manychat",
        "Whatsapp",
        "Referencia",
        "AnioNacimiento",
        "Comuna_Usuario",
        "Fecha_Ingreso",
        "edad",
        "fecha_nacimiento"
    )
    list_filter = (
        "id_manychat",
        "Whatsapp",
        "Referencia",
        "AnioNacimiento",
        "Comuna_Usuario",
        "Fecha_Ingreso",
        "edad",
        "fecha_nacimiento"
    )

class PregTamizajeAdmin(admin.ModelAdmin):
    list_display = ("id", "pregunta", "codigo_preguntas")
    search_fields = ("id", "pregunta", "codigo_preguntas")
    list_filter = ("id", "pregunta", "codigo_preguntas")


class RespUsuarioTamizajeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "id_manychat",
        "respuesta_TM",
        "fecha_respuesta",
    )
    search_fields = (
        "id",
        "id_manychat",
        "respuesta_TM",
        "fecha_respuesta",
    )
    list_filter = (
        "id",
        "id_manychat",
        "respuesta_TM",
        "fecha_respuesta",
    )


class OpcTamizajeAdmin(admin.ModelAdmin):
    list_display = ("id", "id_pregunta", "opc_respuesta_TM")
    search_fields = ("id", "id_pregunta", "opc_respuesta_TM")
    list_filter = ("id", "id_pregunta", "opc_respuesta_TM")


class MensajeContenidoAdmin(admin.ModelAdmin):
    list_display = ("id", "texto", "fecha")
    search_fields = ("id", "texto", "fecha")
    list_filter = ("id", "texto", "fecha")

class filtro_mensajeAdmin(admin.ModelAdmin):
    list_display = ("id","opcresTM", "opcresUS", "mensaje_contenido_id")
    search_fields = ("id","opcresTM", "opcresUS", "mensaje_contenido_id")
    list_filter = ("id","opcresTM", "opcresUS", "mensaje_contenido_id")

class ultima_mamografia_anioAdmin(admin.ModelAdmin):
    list_display = ("id", "anio_ult_mamografia","tiempo_transc_ult_mamografia", "fecha_pregunta", "id_manychat")
    search_fields = ("id", "anio_ult_mamografia","tiempo_transc_ult_mamografia", "fecha_pregunta", "id_manychat")
    list_filter = ("id", "anio_ult_mamografia","tiempo_transc_ult_mamografia", "fecha_pregunta", "id_manychat")

class regionAdmin(admin.ModelAdmin):
    list_display =("cod_region", "nombre_region")
    search_fields=("cod_region", "nombre_region")
    list_filter=("cod_region", "nombre_region")

class provinciaAdmin(admin.ModelAdmin):
    list_display=("cod_provincia", "nombre_provincia", "cod_region")
    search_fields=("cod_provincia", "nombre_provincia", "cod_region")
    list_filter=("cod_provincia", "nombre_provincia", "cod_region")

class comunaAdmin(admin.ModelAdmin):
    list_display=("cod_comuna", "nombre_comuna", "cod_provincia")
    search_fields=("cod_comuna", "nombre_comuna", "cod_provincia")
    list_filter=("cod_comuna", "nombre_comuna", "cod_provincia")

class Codigos_pregAdmin (admin.ModelAdmin):
    list_display=("id", "codigo_preguntas")
    search_fields=("id", "codigo_preguntas")
    list_filter=("id", "codigo_preguntas")


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(PregTamizaje, PregTamizajeAdmin)
admin.site.register(RespUsuarioTamizaje, RespUsuarioTamizajeAdmin)
admin.site.register(OpcTamizaje, OpcTamizajeAdmin)
admin.site.register(MensajeContenido, MensajeContenidoAdmin)
admin.site.register(ultima_mamografia_anio, ultima_mamografia_anioAdmin)
admin.site.register(region, regionAdmin)
admin.site.register(provincia, provinciaAdmin)
admin.site.register(comuna, comunaAdmin)
admin.site.register(Codigos_preg, Codigos_pregAdmin)
admin.site.register(filtro_mensaje, filtro_mensajeAdmin)
