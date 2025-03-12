from django.contrib import admin
from .models import *


class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "id_manychat",
        "Rut",
        "RutHash",
        "Whatsapp",
        "Email",
        "Referencia",
        "AnioNacimiento",
        "Comuna_Usuario",
        "Fecha_Ingreso",
        "edad",
        "fecha_nacimiento"
    )
    search_fields = (
        "id",
        "id_manychat",
        "Rut",
        "RutHash",
        "Whatsapp",
        "Email",
        "Referencia",
        "AnioNacimiento",
        "Comuna_Usuario",
        "Fecha_Ingreso",
        "edad",
        "fecha_nacimiento"
    )
    list_filter = (
        "id",
        "id_manychat",
        "Rut",
        "RutHash",
        "Whatsapp",
        "Email",
        "Referencia",
        "AnioNacimiento",
        "Comuna_Usuario",
        "Fecha_Ingreso",
        "edad",
        "fecha_nacimiento"
    )

class PreguntaAdmin(admin.ModelAdmin):
    list_display = ("id", "pregunta", "codigo_preguntas")
    search_fields = ("id", "pregunta", "codigo_preguntas")
    list_filter = ("id", "pregunta", "codigo_preguntas")


class UsuarioRespuestaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "Rut",
        "RutHash",
        "id_opc_respuesta",
        "fecha_respuesta",
    )
    search_fields = (
        "id",
        "Rut",
        "RutHash",
        "id_opc_respuesta",
        "fecha_respuesta",
    )
    list_filter = (
        "id",
        "Rut",
        "RutHash",
        "id_opc_respuesta",
        "fecha_respuesta",
    )


class PreguntaOpcionRespuestaAdmin(admin.ModelAdmin):
    list_display = ("id", "id_pregunta", "OPC_Respuesta")
    search_fields = ("id", "id_pregunta", "OPC_Respuesta")
    list_filter = ("id", "id_pregunta", "OPC_Respuesta")

class UsuarioTextoPreguntaAdmin(admin.ModelAdmin):
    list_display = ("id", "Rut", "RutHash", "texto_pregunta", "fecha_pregunta", "id_usuario")
    search_fields = ("id", "Rut", "RutHash", "texto_pregunta", "fecha_pregunta", "id_usuario")
    list_filter = ("id", "Rut", "RutHash", "texto_pregunta", "fecha_pregunta", "id_usuario")
    
class MensajeContenidoAdmin(admin.ModelAdmin):
    list_display = ("id", "texto", "fecha")
    search_fields = ("id", "texto", "fecha")
    list_filter = ("id", "texto", "fecha")

class filtro_mensajeAdmin(admin.ModelAdmin):
    list_display = ("id", "opcrespFRNM", "opcrespFRM", "opcrespDS", "opcresTM", "opcresUS", "mensaje_contenido_id")
    search_fields = ("id", "opcrespFRNM", "opcrespFRM", "opcrespDS", "opcresTM", "opcresUS", "mensaje_contenido_id")
    list_filter = ("id", "opcrespFRNM", "opcrespFRM", "opcrespDS", "opcresTM", "opcresUS", "mensaje_contenido_id")

class ultima_mamografia_anioAdmin(admin.ModelAdmin):
    list_display = ("id", "Rut", "RutHash", "anio_ult_mamografia","tiempo_transc_ult_mamografia", "fecha_pregunta", "id_usuario")
    search_fields = ("id", "Rut", "RutHash", "anio_ult_mamografia","tiempo_transc_ult_mamografia", "fecha_pregunta", "id_usuario")
    list_filter = ("id", "Rut", "RutHash", "anio_ult_mamografia","tiempo_transc_ult_mamografia", "fecha_pregunta", "id_usuario")

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

class PregFactorRiesgoModAdmin(admin.ModelAdmin):
    list_display=("id", "pregunta_FRM", "codigo_preguntas")
    search_fields=("id", "pregunta_FRM", "codigo_preguntas")
    list_filter=("id", "pregunta_FRM", "codigo_preguntas")

class OpcFactorRiesgoModAdmin(admin.ModelAdmin):
    list_display=("id", "opc_respuesta_FRM", "id_pregunta_FRM")
    search_fields=("id", "opc_respuesta_FRM", "id_pregunta_FRM")
    list_filter=("id", "opc_respuesta_FRM", "id_pregunta_FRM")

class RespUsuarioFactorRiesgoModAdmin(admin.ModelAdmin):
    list_display=("id", "Rut", "RutHash", "respuesta_FRM", "fecha_respuesta")
    search_fields=("id", "Rut", "RutHash", "respuesta_FRM", "fecha_respuesta")
    list_filter=("id", "Rut", "RutHash", "respuesta_FRM", "fecha_respuesta")

class PregFactorRiesgoNoModAdmin(admin.ModelAdmin):
    list_display=("id", "pregunta_FRNM", "codigo_preguntas")
    search_fields=("id", "pregunta_FRNM", "codigo_preguntas")
    list_filter=("id", "pregunta_FRNM", "codigo_preguntas")

class OpcFactorRiesgoNoModAdmin(admin.ModelAdmin):
    list_display=("id", "opc_respuesta_FRNM", "id_pregunta_FRNM")
    search_fields=("id", "opc_respuesta_FRNM", "id_pregunta_FRNM")
    list_filter=("id", "opc_respuesta_FRNM", "id_pregunta_FRNM")

class RespUsuarioFactorRiesgoNoModAdmin(admin.ModelAdmin):
    list_display=("id", "Rut",  "RutHash", "respuesta_FRNM", "fecha_respuesta")
    search_fields=("id", "Rut", "RutHash", "respuesta_FRNM", "fecha_respuesta")
    list_filter=("id", "Rut", "RutHash", "respuesta_FRNM",  "fecha_respuesta")

class PregDeterSaludAdmin(admin.ModelAdmin):
    list_display =("id", "pregunta_DS", "codigo_preguntas")
    search_fields=("id", "pregunta_DS","codigo_preguntas")
    list_filter=("id", "pregunta_DS","codigo_preguntas")

class OpcDeterSaludAdmin(admin.ModelAdmin):
    list_display =("id", "opc_respuesta_DS", "id_pregunta_DS")
    search_fields=("id", "opc_respuesta_DS", "id_pregunta_DS")
    list_filter=("id", "opc_respuesta_DS", "id_pregunta_DS")

class RespDeterSaludAdmin(admin.ModelAdmin):
    list_display =("id", "Rut", "RutHash", "respuesta_DS", "fecha_respuesta")
    search_fields=("id", "Rut", "RutHash", "respuesta_DS", "fecha_respuesta")
    list_filter=("id", "Rut", "RutHash", "respuesta_DS", "fecha_respuesta")

class RespTextoFRMAdmin (admin.ModelAdmin):
    list_display=("id","Rut", "RutHash", "peso_FRM5", "altura_FRM4", "fecha_respuesta", "id_usuario")
    search_fields=("id","Rut", "RutHash", "peso_FRM5", "altura_FRM4", "fecha_respuesta", "id_usuario")
    list_filter=("id","Rut",  "RutHash", "peso_FRM5", "altura_FRM4", "fecha_respuesta", "id_usuario")

class Codigos_pregAdmin (admin.ModelAdmin):
    list_display=("id", "codigo_preguntas")
    search_fields=("id", "codigo_preguntas")
    list_filter=("id", "codigo_preguntas")

class CalculoFRMAdmin(admin.ModelAdmin):
    list_display=("id", "Rut", "RutHash", "altura_mod", "peso_mod", "imc", "datos_originales")
    search_fields=("id", "Rut", "RutHash", "altura_mod", "peso_mod", "imc", "datos_originales")
    list_filter=("id", "Rut", "RutHash", "altura_mod", "peso_mod", "imc", "datos_originales")


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Pregunta, PreguntaAdmin)
admin.site.register(UsuarioRespuesta, UsuarioRespuestaAdmin)
admin.site.register(PreguntaOpcionRespuesta, PreguntaOpcionRespuestaAdmin)
admin.site.register(UsuarioTextoPregunta, UsuarioTextoPreguntaAdmin)
admin.site.register(MensajeContenido, MensajeContenidoAdmin)
admin.site.register(ultima_mamografia_anio, ultima_mamografia_anioAdmin)
admin.site.register(region, regionAdmin)
admin.site.register(provincia, provinciaAdmin)
admin.site.register(comuna, comunaAdmin)
admin.site.register(PregFactorRiesgoMod, PregFactorRiesgoModAdmin)
admin.site.register(OpcFactorRiesgoMod, OpcFactorRiesgoModAdmin)
admin.site.register(RespUsuarioFactorRiesgoMod, RespUsuarioFactorRiesgoModAdmin)
admin.site.register(PregFactorRiesgoNoMod, PregFactorRiesgoNoModAdmin)
admin.site.register(OpcFactorRiesgoNoMod, OpcFactorRiesgoNoModAdmin)
admin.site.register(RespUsuarioFactorRiesgoNoMod, RespUsuarioFactorRiesgoNoModAdmin)
admin.site.register(PregDeterSalud, PregDeterSaludAdmin)
admin.site.register(OpcDeterSalud, OpcDeterSaludAdmin)
admin.site.register(RespDeterSalud, RespDeterSaludAdmin)
admin.site.register(RespTextoFRM, RespTextoFRMAdmin)
admin.site.register(Codigos_preg, Codigos_pregAdmin)
admin.site.register(CalculoFRM, CalculoFRMAdmin)
admin.site.register(filtro_mensaje, filtro_mensajeAdmin)
