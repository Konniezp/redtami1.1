import base64
from datetime import datetime, date
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
import requests
import numpy as np

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, F, Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone


from openpyxl import Workbook

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import JSONParser

from .forms import *
from .models import *
from .serializer import *

from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill

from django.views.decorators.csrf import csrf_exempt
import json
import locale 

import logging

locale.setlocale(locale.LC_TIME, 'es_ES')
    
@login_required
def home(request):
    return render(request, "home.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("home")
        else:
            return render(request, "registration/login.html")

    return render(request, "registration/login.html")

# --------------------- Respuestas de Usuario --------------------- #

#Home
@login_required
def respuestasHome(request):
    return render(request, "respuestas/respuestasHome.html")

@login_required
def opcVisualFRM(request):
    return render(request, "respuestas/opcVisualFRM.html")

@login_required
def opcVisualFRNM(request):
    return render(request, "respuestas/opcVisualFRNM.html")

@login_required
def opcVisualDS(request):
    return render(request, "respuestas/opcVisualDS.html")

# Base de datos
@login_required
def datosPerfil(request):
    Datos = Usuario.objects.all().order_by("-Fecha_Ingreso")
    data = {
        "Datos": Datos,
    }
    return render(request, "respuestas/datosPerfil.html", data)

@login_required
def datosPreguntas(request):
    Datos = UsuarioRespuesta.objects.select_related(
        "id_opc_respuesta", "id_opc_respuesta__id_pregunta").values("id",
        "id_opc_respuesta__id_pregunta__pregunta", "id_opc_respuesta__OPC_Respuesta",
        "fecha_respuesta", "RutHash").order_by("-fecha_respuesta")
    data = {
        "Datos": Datos,
    }
    return render(request, "respuestas/datosPreguntas.html", data)

@login_required
def datosTextoPreguntas(request):
    Datos = UsuarioTextoPregunta.objects.all().order_by("-fecha_pregunta")
    data = {
        "Datos": Datos,
    }
    return render(request, "respuestas/datosPreguntasEspecialistas.html", data)

@login_required
def datosFRM(request):
    Datos = RespUsuarioFactorRiesgoMod.objects.select_related().values(
        "id",
        "RutHash",
        "respuesta_FRM__id_pregunta_FRM_id__pregunta_FRM",
        "respuesta_FRM__opc_respuesta_FRM",
        "fecha_respuesta"
    ).order_by("-RutHash")
    data = {
        "Datos": Datos,
    }
    return render(request, "respuestas/datosFRM.html", data)

@login_required
def datosFRM2(request):
    preguntas = PregFactorRiesgoMod.objects.all()
    usuarios_respuestas = RespUsuarioFactorRiesgoMod.objects.select_related(
        "respuesta_FRM", "respuesta_FRM__id_pregunta_FRM"
    ).values( "RutHash", "fecha_respuesta", "respuesta_FRM__id_pregunta_FRM__pregunta_FRM", "respuesta_FRM__opc_respuesta_FRM")

    dict_respuestas = {}

    for respuesta in usuarios_respuestas:
        rut = respuesta["RutHash"]
        pregunta = respuesta["respuesta_FRM__id_pregunta_FRM__pregunta_FRM"]
        respuesta_usuario = respuesta["respuesta_FRM__opc_respuesta_FRM"]
        
        if rut not in dict_respuestas:
            dict_respuestas[rut] = {"fecha": respuesta["fecha_respuesta"], "respuestas": {}}
        dict_respuestas[rut]["respuestas"][pregunta] = respuesta_usuario

    # Convertir el diccionario a una lista de listas para facilitar la renderización en HTML
    tabla_respuestas = []
    for rut, data in dict_respuestas.items():
        fila = [rut] + [data["respuestas"].get(p.pregunta_FRM, "-") for p in preguntas] + [data["fecha"]]
        tabla_respuestas.append(fila)

    return render(request, "respuestas/datosFRM2.html", {
        "preguntas": preguntas,
        "tabla_respuestas": tabla_respuestas,
    })

@login_required
def datosFRNM(request):
    Datos = RespUsuarioFactorRiesgoNoMod.objects.select_related().values(
        "id",
        "RutHash",
        "respuesta_FRNM_id__id_pregunta_FRNM_id__pregunta_FRNM",
        "respuesta_FRNM_id__opc_respuesta_FRNM",
        "fecha_respuesta"
    ).order_by("-RutHash")
    data = {
        "Datos": Datos,
    }
    return render(request, "respuestas/datosFRNM.html", data)

@login_required
def datosFRNM2(request):
    preguntas = PregFactorRiesgoNoMod.objects.all()
    usuarios_respuestas = RespUsuarioFactorRiesgoNoMod.objects.select_related(
        "respuesta_FRNM", "respuesta_FRM__id_pregunta_FRNM"
    ).values( "RutHash", "fecha_respuesta", "respuesta_FRNM__id_pregunta_FRNM__pregunta_FRNM", "respuesta_FRNM__opc_respuesta_FRNM")

    dict_respuestas = {}

    for respuesta in usuarios_respuestas:
        rut = respuesta[ "RutHash"]
        pregunta = respuesta["respuesta_FRNM__id_pregunta_FRNM__pregunta_FRNM"]
        respuesta_usuario = respuesta["respuesta_FRNM__opc_respuesta_FRNM"]
        
        if rut not in dict_respuestas:
            dict_respuestas[rut] = {"fecha": respuesta["fecha_respuesta"], "respuestas": {}}
        dict_respuestas[rut]["respuestas"][pregunta] = respuesta_usuario

    # Convertir el diccionario a una lista de listas para facilitar la renderización en HTML
    tabla_respuestas = []
    for rut, data in dict_respuestas.items():
        fila = [rut] + [data["respuestas"].get(p.pregunta_FRNM, "-") for p in preguntas] + [data["fecha"]]
        tabla_respuestas.append(fila)

    return render(request, "respuestas/datosFRNM2.html", {
        "preguntas": preguntas,
        "tabla_respuestas": tabla_respuestas,
    })

@login_required
def datosDS(request):
    Datos = RespDeterSalud.objects.select_related().values(
        "id",
        "RutHash",
        "respuesta_DS_id__id_pregunta_DS_id__pregunta_DS",
        "respuesta_DS_id__opc_respuesta_DS",
        "fecha_respuesta"
    ).order_by("-RutHash")
    data = {
        "Datos": Datos,
    }
    return render(request,"respuestas/datosDS.html", data)

@login_required
def datosDS2(request):
    preguntas = PregDeterSalud.objects.all()
    usuarios_respuestas = RespDeterSalud.objects.select_related(
        "respuesta_DS", "respuesta_DS__id_pregunta_DS"
    ).values("RutHash", "fecha_respuesta", "respuesta_DS__id_pregunta_DS__pregunta_DS", "respuesta_DS__opc_respuesta_DS")

    dict_respuestas = {}

    for respuesta in usuarios_respuestas:
        rut = respuesta[ "RutHash"]
        pregunta = respuesta["respuesta_DS__id_pregunta_DS__pregunta_DS"]
        respuesta_usuario = respuesta["respuesta_DS__opc_respuesta_DS"]
        
        if rut not in dict_respuestas:
            dict_respuestas[rut] = {"fecha": respuesta["fecha_respuesta"], "respuestas": {}}
        dict_respuestas[rut]["respuestas"][pregunta] = respuesta_usuario

    # Convertir el diccionario a una lista de listas para facilitar la renderización en HTML
    tabla_respuestas = []
    for rut, data in dict_respuestas.items():
        fila = [rut] + [data["respuestas"].get(p.pregunta_DS, "-") for p in preguntas] + [data["fecha"]]
        tabla_respuestas.append(fila)

    return render(request, "respuestas/datosDS2.html", {
        "preguntas": preguntas,
        "tabla_respuestas": tabla_respuestas,
    })

@login_required
def datosListadoOrdenado(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT us.id, us.Rut, Whatsapp, Email, edad,  
            COALESCE(opc_respuesta_FRNM, 'No aplica') AS Antecedentes_familiares,
            COALESCE(ult.tiempo_transc_ult_mamografia, 1000) AS Ult_mamografia
            FROM botApp_usuario us LEFT JOIN botApp_respusuariofactorriesgonomod rnm ON us.RutHash = rnm.RutHash
            LEFT JOIN botApp_ultima_mamografia_anio ult ON us.RutHash = ult.RutHash  
            LEFT JOIN botApp_opcfactorriesgonomod opc ON  opc.id = rnm.respuesta_FRNM_id
            WHERE opc.id IN(4,5,6) OR rnm.respuesta_FRNM_id IS NULL
            ORDER BY ult.tiempo_transc_ult_mamografia DESC;
        """)
        columns = [col[0] for col in cursor.description]
        datos = cursor.fetchall()

    #Descifra datos 
    datos_descifrados=[]
    for row in datos:
        id, Rut, Whatsapp, Email, edad, antecedentes, ultima_mamografia = row
    
        #Intenta descifrar cada campo encriptado
        try:
            Rut_descifrado = decrypt_data(Rut) if Rut else "No disponible"
        except:
            Rut_descifrado = "Error al descifrar Rut"
        
        try:
            Whatsapp_descifrado = decrypt_data(Whatsapp) if Whatsapp else "No disponible"
        except:
            Whatsapp_descifrado = "Error al descifrar Whatsapp"

        try:
            Email_descifrado = decrypt_data(Email) if Email else "No disponible"
        except:
            Email_descifrado = "Error al descifrar Email"
        
        datos_descifrados.append({
            "id": id,
            "Rut": Rut_descifrado,
            "Whatsapp": Whatsapp_descifrado,
            "Email": Email_descifrado,
            "edad": edad,
            "Antecedentes_familiares": antecedentes,
            "Ult_mamografia": ultima_mamografia,
        })
    return render(request, "respuestas/datosListadoOrdenado.html", {"Datos": datos_descifrados})
#Se agregan los datos descifrados a la lista

#Ajustar anchos de columnas según el largo de la celda
def ajustar_ancho_columnas(ws):
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)

        for cell in col:
            try:
                if cell.value: 
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        
        ws.column_dimensions[col_letter].width = max_length + 2  

# Aplica color a la primera fila de encabezados 
def background_colors(ws):
    color = "00a0b3a8" 
    fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

    for cell in ws[1]: 
        cell.fill = fill

def crear_excel_desde_db():
    wb = Workbook()

    # Hoja 1: Respuestas Usuario
    ws_respuestas_usuario = wb.active
    ws_respuestas_usuario.title = 'Respuestas Usuario'

    preguntas = Pregunta.objects.all()
    lista_preguntas = [ "RutHash"] + [pregunta.pregunta for pregunta in preguntas]
    ws_respuestas_usuario.append(lista_preguntas)

    usuarios_respuestas = UsuarioRespuesta.objects.select_related('id_opc_respuesta', 'id_opc_respuesta__id_pregunta').values(
         'RutHash', 'id_opc_respuesta__id_pregunta__pregunta', 'id_opc_respuesta__OPC_Respuesta'
    )

    dict_respuestas = {}

    for respuesta in usuarios_respuestas:
        rut = respuesta[ 'RutHash']
        pregunta = respuesta['id_opc_respuesta__id_pregunta__pregunta']
        respuesta_usuario = respuesta['id_opc_respuesta__OPC_Respuesta']
        if rut not in dict_respuestas:
            dict_respuestas[rut] = {}
        dict_respuestas[rut][pregunta] = respuesta_usuario

    for rut, respuestas_usuario in dict_respuestas.items():
        fila = [rut]
        for pregunta in preguntas:
            respuesta = respuestas_usuario.get(pregunta.pregunta, '')
            fila.append(respuesta)
        ws_respuestas_usuario.append(fila)

    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_respuestas_usuario)
    background_colors(ws_respuestas_usuario)

    # Hoja 2: Datos Perfil
    ws_datos_perfil = wb.create_sheet(title='Datos Perfil')
    campos_usuario = [field.name for field in Usuario._meta.fields if field.name not in ['Comuna_Usuario']]
    ws_datos_perfil.append(campos_usuario)

    for usuario in Usuario.objects.all():
        datos_usuario = [str(getattr(usuario, campo)) for campo in campos_usuario]
        ws_datos_perfil.append(datos_usuario)

    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_datos_perfil)
    background_colors(ws_datos_perfil)

    # Hoja 3: Preguntas Especialista
    ws_preguntas_especialista = wb.create_sheet(title='Preguntas al especialista')
    campos_preguntas_especialista = [field.name for field in UsuarioTextoPregunta._meta.fields if field.name != 'id']
    ws_preguntas_especialista.append(campos_preguntas_especialista)

    for pregunta in UsuarioTextoPregunta.objects.all():
        datos_pregunta = [str(getattr(pregunta, campo)) for campo in campos_preguntas_especialista]
        ws_preguntas_especialista.append(datos_pregunta)

    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_preguntas_especialista)
    background_colors(ws_preguntas_especialista)

    # Hoja 4: Factores riesgo modificables 

    ws_FRM = wb.create_sheet(title='Factores riesgo modificables')

    preguntas =PregFactorRiesgoMod.objects.all()
    lista_preguntas = ['RutHash'] + [pregunta.pregunta_FRM for pregunta in preguntas]
    ws_FRM.append(lista_preguntas)

    usuarios_respuestas = RespUsuarioFactorRiesgoMod.objects.select_related(
    "respuesta_FRM", "respuesta_FRM__id_pregunta_FRM").values("RutHash", "fecha_respuesta",  "respuesta_FRM__id_pregunta_FRM__pregunta_FRM", "respuesta_FRM__opc_respuesta_FRM")

    dict_respuestas = {}

    for respuesta in usuarios_respuestas:
        rut = respuesta['RutHash']
        pregunta = respuesta['respuesta_FRM__id_pregunta_FRM__pregunta_FRM']
        respuesta_usuario = respuesta['respuesta_FRM__opc_respuesta_FRM']
        if rut not in dict_respuestas:
            dict_respuestas[rut] = {}
        dict_respuestas[rut][pregunta] = respuesta_usuario

    for rut, respuestas_usuario in dict_respuestas.items():
        fila = [rut]
        for pregunta in preguntas:
            respuesta = respuestas_usuario.get(pregunta.pregunta_FRM, '')
            fila.append(respuesta)
        ws_FRM.append(fila) 
   
    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_FRM)
    background_colors(ws_FRM)

    #OPCIÓN 2: 

    ws_FRM_2 = wb.create_sheet(title='Factores Riesgo modificables 2')

    preguntas =PregFactorRiesgoMod.objects.all()
    lista_preguntas = ['RutHash', 'Preguntas', 'Respuestas', 'Fecha Respuesta'] 
    ws_FRM_2.append(lista_preguntas)

    usuarios_respuestas = RespUsuarioFactorRiesgoMod.objects.select_related(
    "respuesta_FRM", "respuesta_FRM__id_pregunta_FRM").values( "RutHash", "fecha_respuesta",  "respuesta_FRM__id_pregunta_FRM__pregunta_FRM", "respuesta_FRM__opc_respuesta_FRM").order_by('Rut')

    for respuesta in usuarios_respuestas:

        pregunta = respuesta['respuesta_FRM__id_pregunta_FRM__pregunta_FRM']
        respuesta_usuario = respuesta['respuesta_FRM__opc_respuesta_FRM']
        fecha_respuesta = respuesta['fecha_respuesta'].replace(tzinfo=None) if respuesta['fecha_respuesta'] else ''
        fila = [
            respuesta['RutHash'],
            pregunta,  
            respuesta_usuario, 
            fecha_respuesta,  
        ]
        ws_FRM_2.append(fila)
    
    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_FRM_2)
    background_colors(ws_FRM_2)

    # Hoja 5: Factores riesgo No modificables 

    ws_FRNM = wb.create_sheet(title='Factores Riesgo No Mod')

    preguntas =PregFactorRiesgoNoMod.objects.all()
    lista_preguntas = ['RutHash'] + [pregunta.pregunta_FRNM for pregunta in preguntas]
    ws_FRNM.append(lista_preguntas)

    usuarios_respuestas = RespUsuarioFactorRiesgoNoMod.objects.select_related(
    "respuesta_FRNM", "respuesta_FRNM__id_pregunta_FRNM").values("RutHash", "fecha_respuesta",  "respuesta_FRNM__id_pregunta_FRNM__pregunta_FRNM", "respuesta_FRNM__opc_respuesta_FRNM")

    dict_respuestas = {}

    for respuesta in usuarios_respuestas:
        rut = respuesta['RutHash']
        pregunta = respuesta['respuesta_FRNM__id_pregunta_FRNM__pregunta_FRNM']
        respuesta_usuario = respuesta['respuesta_FRNM__opc_respuesta_FRNM']
        if rut not in dict_respuestas:
            dict_respuestas[rut] = {}
        dict_respuestas[rut][pregunta] = respuesta_usuario

    for rut, respuestas_usuario in dict_respuestas.items():
        fila = [rut]
        for pregunta in preguntas:
            respuesta = respuestas_usuario.get(pregunta.pregunta_FRNM, '')
            fila.append(respuesta)
        ws_FRNM.append(fila) 
   
    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_FRNM)
    background_colors(ws_FRNM)

    #OPCIÓN 2: 

    ws_FRNM_2 = wb.create_sheet(title='Factores Riesgo No Mod 2')

    preguntas =PregFactorRiesgoNoMod.objects.all()
    lista_preguntas = ['RutHash', 'Preguntas', 'Respuestas', 'Fecha Respuesta'] 
    ws_FRNM_2.append(lista_preguntas)

    usuarios_respuestas = RespUsuarioFactorRiesgoNoMod.objects.select_related(
    "respuesta_FRNM", "respuesta_FRNM__id_pregunta_FRNM").values( "RutHash", "fecha_respuesta",  "respuesta_FRNM__id_pregunta_FRNM__pregunta_FRNM","respuesta_FRNM__opc_respuesta_FRNM").order_by('RutHash')

    for respuesta in usuarios_respuestas:

        pregunta = respuesta['respuesta_FRNM__id_pregunta_FRNM__pregunta_FRNM']
        respuesta_usuario = respuesta['respuesta_FRNM__opc_respuesta_FRNM']
        fecha_respuesta = respuesta['fecha_respuesta'].replace(tzinfo=None) if respuesta['fecha_respuesta'] else ''
        fila = [
            respuesta['RutHash'],
            pregunta,
            respuesta_usuario,
            fecha_respuesta, 
        ]
        ws_FRNM_2.append(fila)

    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_FRNM_2)
    background_colors(ws_FRNM_2)

    # Hoja 6: Determinantes de Salud 
    ws_DS = wb.create_sheet(title='Determinantes de Salud')
    preguntas =PregDeterSalud.objects.all()
    lista_preguntas = ['RutHash'] + [pregunta.pregunta_DS for pregunta in preguntas]
    ws_DS.append(lista_preguntas)

    usuarios_respuestas = RespDeterSalud.objects.select_related(
    "respuesta_DS", "respuesta_DS__id_pregunta_DS").values( "RutHash", "fecha_respuesta",  "respuesta_DS__id_pregunta_DS__pregunta_DS", "respuesta_DS__opc_respuesta_DS")

    dict_respuestas = {}

    for respuesta in usuarios_respuestas:
        rut = respuesta['RutHash']
        pregunta = respuesta['respuesta_DS__id_pregunta_DS__pregunta_DS']
        respuesta_usuario = respuesta['respuesta_DS__opc_respuesta_DS']
        if rut not in dict_respuestas:
            dict_respuestas[rut] = {}
        dict_respuestas[rut][pregunta] = respuesta_usuario

    for rut, respuestas_usuario in dict_respuestas.items():
        fila = [rut]
        for pregunta in preguntas:
            respuesta = respuestas_usuario.get(pregunta.pregunta_DS, '')
            fila.append(respuesta)
        ws_DS.append(fila) 
   
    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_DS)
    background_colors(ws_DS)

    #OPCIÓN 2: 

    ws_DS_2 = wb.create_sheet(title='Determinantes de Salud 2')

    preguntas =PregDeterSalud.objects.all()
    lista_preguntas = ['RutHash', 'Preguntas', 'Respuestas', 'Fecha Respuesta'] 
    ws_DS_2.append(lista_preguntas)

    usuarios_respuestas = RespDeterSalud.objects.select_related(
    "respuesta_DS", "respuesta_DS__id_pregunta_DS").values( "RutHash", "fecha_respuesta",  "respuesta_DS__id_pregunta_DS__pregunta_DS","respuesta_DS__opc_respuesta_DS").order_by('RutHash')

    for respuesta in usuarios_respuestas:

        pregunta = respuesta['respuesta_DS__id_pregunta_DS__pregunta_DS']
        respuesta_usuario = respuesta['respuesta_DS__opc_respuesta_DS']
        fecha_respuesta = respuesta['fecha_respuesta'].replace(tzinfo=None) if respuesta['fecha_respuesta'] else ''
        fila = [
            respuesta['RutHash'],
            pregunta,
            respuesta_usuario,
            fecha_respuesta, 
        ]
        ws_DS_2.append(fila) 

    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_DS_2)
    background_colors(ws_DS_2)


    # Guardar el archivo
    nombre_archivo = 'reporte_respuestas.xlsx'
    wb.save(nombre_archivo)

    return nombre_archivo

def descargar_excel(request):
    # Llama a la función para crear el Excel
    nombre_archivo = crear_excel_desde_db()

    # Abre el archivo Excel y lo envía como una respuesta de descarga
    with open(nombre_archivo, 'rb') as excel_file:
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={nombre_archivo}'
        return response

def crear_excel_listado_ordenable(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT us.id, us.Rut, Whatsapp, Email, edad,                        
            COALESCE(opc_respuesta_FRNM, 'No aplica') AS Antecedentes_familiares,
            COALESCE(ult.tiempo_transc_ult_mamografia, 1000) AS Ult_mamografia
            FROM botApp_usuario us 
            JOIN botApp_respusuariofactorriesgonomod rnm ON us.RutHash = rnm.RutHash
            LEFT JOIN botApp_ultima_mamografia_anio ult ON us.RutHash = ult.RutHash  
            LEFT JOIN botApp_opcfactorriesgonomod opc ON opc.id = rnm.respuesta_FRNM_id
            WHERE opc.id IN (4,5,6) OR rnm.respuesta_FRNM_id IS NULL
            ORDER BY ult.tiempo_transc_ult_mamografia DESC;
        """)
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()

    # Crear un archivo Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Listado Ordenable"

    # Agregar encabezados
    ws.append(columns)

    # Agregar los datos fila por fila
    datos_descifrados = []
    for row in data:
        id, Rut, Whatsapp, Email, edad, antecedentes, ultima_mamografia = row

        # Intenta descifrar los datos
        try:
            Rut_descifrado = decrypt_data(Rut) if Rut else "No disponible"
        except:
            Rut_descifrado = "Error al descifrar Rut"

        try:
            Whatsapp_descifrado = decrypt_data(Whatsapp) if Whatsapp else "No disponible"
        except:
            Whatsapp_descifrado = "Error al descifrar Whatsapp"

        try:
            Email_descifrado = decrypt_data(Email) if Email else "No disponible"
        except:
            Email_descifrado = "Error al descifrar Email"

        # Agregar los datos descifrados a la lista y a la hoja de Excel
        fila_descifrada = (id, Rut_descifrado, Whatsapp_descifrado, Email_descifrado, edad, antecedentes, ultima_mamografia)
        datos_descifrados.append(fila_descifrada)
        ws.append(fila_descifrada) 

    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws)
    background_colors(ws)

    # Preparar la respuesta HTTP
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="ListadoOrdenable.xlsx"'

    # Guardar el archivo en la respuesta HTTP
    wb.save(response)
    return response

def crear_excel_datos_preguntas(resquest):
    wb = Workbook()
    ws_datos_preg = wb.active
    ws_datos_preg.title = "Preguntas generales"

    preguntas =Pregunta.objects.all()
    lista_preguntas = ['RutHash', 'Preguntas', 'Respuestas', 'Fecha Respuesta'] 
    ws_datos_preg.append(lista_preguntas)

    usuarios_respuestas = UsuarioRespuesta.objects.select_related(
        "id_opc_respuesta", "id_opc_respuesta__id_pregunta").values("id",
        "id_opc_respuesta__id_pregunta__pregunta", "id_opc_respuesta__OPC_Respuesta",
        "fecha_respuesta",  "RutHash").order_by("-fecha_respuesta")
    

    for respuesta in usuarios_respuestas:

        pregunta = respuesta['id_opc_respuesta__id_pregunta__pregunta']
        respuesta_usuario = respuesta['id_opc_respuesta__OPC_Respuesta']
        fecha_respuesta = respuesta['fecha_respuesta'].replace(tzinfo=None) if respuesta['fecha_respuesta'] else ''
        fila = [
            respuesta['RutHash'],
            pregunta,  
            respuesta_usuario, 
            fecha_respuesta,  
        ]
        ws_datos_preg.append(fila)
    
    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_datos_preg)
    background_colors(ws_datos_preg)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="Datos preguntas.xlsx"'

    # Guardar el archivo en la respuesta HTTP
    wb.save(response)
    return response

def crear_excel_preguntas_esp(resquest):
    wb = Workbook()
    ws_preg_esp = wb.active
    ws_preg_esp.title = "Preguntas especialistas"

    lista_preguntas = ['RutHash', 'Preguntas', 'Fecha Pregunta'] 
    ws_preg_esp.append(lista_preguntas)

    preguntas = UsuarioTextoPregunta.objects.all()

    for pregunta in preguntas:
        fila = [
            pregunta.RutHash,  
            pregunta.texto_pregunta,
            pregunta.fecha_pregunta.replace(tzinfo=None) if pregunta.fecha_pregunta else ''
        ]
        ws_preg_esp.append(fila)
    
    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_preg_esp)
    background_colors(ws_preg_esp)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="Preguntas Especialista.xlsx"'

    # Guardar el archivo en la respuesta HTTP
    wb.save(response)
    return response

def crear_excel_mod_V1(resquest):
    wb = Workbook()
    ws_FRM_V1 = wb.active
    ws_FRM_V1.title = "Factores de riesgo mod"

    preguntas =PregFactorRiesgoMod.objects.all()
    lista_preguntas = ['RutHash', 'Preguntas', 'Respuestas', 'Fecha Respuesta'] 
    ws_FRM_V1.append(lista_preguntas)

    usuarios_respuestas = RespUsuarioFactorRiesgoMod.objects.select_related(
    "respuesta_FRM", "respuesta_FRM__id_pregunta_FRM").values( "RutHash", "fecha_respuesta",  "respuesta_FRM__id_pregunta_FRM__pregunta_FRM", "respuesta_FRM__opc_respuesta_FRM").order_by('RutHash')

    for respuesta in usuarios_respuestas:

        pregunta = respuesta['respuesta_FRM__id_pregunta_FRM__pregunta_FRM']
        respuesta_usuario = respuesta['respuesta_FRM__opc_respuesta_FRM']
        fecha_respuesta = respuesta['fecha_respuesta'].replace(tzinfo=None) if respuesta['fecha_respuesta'] else ''
        fila = [
            respuesta['RutHash'],
            pregunta,  
            respuesta_usuario, 
            fecha_respuesta,  
        ]
        ws_FRM_V1.append(fila)
    
    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_FRM_V1)
    background_colors(ws_FRM_V1)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="FactoresMod_V1.xlsx"'

    # Guardar el archivo en la respuesta HTTP
    wb.save(response)
    return response

def crear_excel_mod_V2(request):

    wb = Workbook()
    ws_FRM_V2 = wb.active
    ws_FRM_V2.title = "Factores de riesgo mod 2"
    
    preguntas =PregFactorRiesgoMod.objects.all()
    lista_preguntas = ['RutHash'] + [pregunta.pregunta_FRM for pregunta in preguntas]
    ws_FRM_V2.append(lista_preguntas)

    usuarios_respuestas = RespUsuarioFactorRiesgoMod.objects.select_related(
    "respuesta_FRM", "respuesta_FRM__id_pregunta_FRM").values( "RutHash", "fecha_respuesta",  "respuesta_FRM__id_pregunta_FRM__pregunta_FRM", "respuesta_FRM__opc_respuesta_FRM")

    dict_respuestas = {}

    for respuesta in usuarios_respuestas:
        rut = respuesta['RutHash']
        pregunta = respuesta['respuesta_FRM__id_pregunta_FRM__pregunta_FRM']
        respuesta_usuario = respuesta['respuesta_FRM__opc_respuesta_FRM']
        if rut not in dict_respuestas:
            dict_respuestas[rut] = {}
        dict_respuestas[rut][pregunta] = respuesta_usuario

    for rut, respuestas_usuario in dict_respuestas.items():
        fila = [rut]
        for pregunta in preguntas:
            respuesta = respuestas_usuario.get(pregunta.pregunta_FRM, '')
            fila.append(respuesta)
        ws_FRM_V2.append(fila) 
   
    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_FRM_V2)
    background_colors(ws_FRM_V2)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="FactoresMod_V2.xlsx"'

    # Guardar el archivo en la respuesta HTTP
    wb.save(response)
    return response

def crear_excel_no_mod_V1(resquest):

    wb = Workbook()
    ws_FRNM_V1 = wb.active
    ws_FRNM_V1.title = "Factores de riesgo No mod"

    preguntas =PregFactorRiesgoNoMod.objects.all()
    lista_preguntas = ['RutHash', 'Preguntas', 'Respuestas', 'Fecha Respuesta'] 
    ws_FRNM_V1.append(lista_preguntas)

    usuarios_respuestas = RespUsuarioFactorRiesgoNoMod.objects.select_related(
    "respuesta_FRNM", "respuesta_FRNM__id_pregunta_FRNM").values( "RutHash", "fecha_respuesta",  "respuesta_FRNM__id_pregunta_FRNM__pregunta_FRNM","respuesta_FRNM__opc_respuesta_FRNM").order_by('RutHash')

    for respuesta in usuarios_respuestas:

        pregunta = respuesta['respuesta_FRNM__id_pregunta_FRNM__pregunta_FRNM']
        respuesta_usuario = respuesta['respuesta_FRNM__opc_respuesta_FRNM']
        fecha_respuesta = respuesta['fecha_respuesta'].replace(tzinfo=None) if respuesta['fecha_respuesta'] else ''
        fila = [
            respuesta['RutHash'],
            pregunta,
            respuesta_usuario,
            fecha_respuesta, 
        ]
        ws_FRNM_V1.append(fila)

    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_FRNM_V1)
    background_colors(ws_FRNM_V1)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="Factores No Mod_V1.xlsx"'

    # Guardar el archivo en la respuesta HTTP
    wb.save(response)
    return response

def crear_excel_no_mod_V2(resquest):

    wb = Workbook()
    ws_FRNM_V2 = wb.active
    ws_FRNM_V2.title = "Factores de riesgo no mod"

    preguntas =PregFactorRiesgoNoMod.objects.all()
    lista_preguntas = ['RutHash'] + [pregunta.pregunta_FRNM for pregunta in preguntas]
    ws_FRNM_V2.append(lista_preguntas)

    usuarios_respuestas = RespUsuarioFactorRiesgoNoMod.objects.select_related(
    "respuesta_FRNM", "respuesta_FRNM__id_pregunta_FRNM").values( "RutHash", "fecha_respuesta",  "respuesta_FRNM__id_pregunta_FRNM__pregunta_FRNM", "respuesta_FRNM__opc_respuesta_FRNM")

    dict_respuestas = {}

    for respuesta in usuarios_respuestas:
        rut = respuesta['RutHash']
        pregunta = respuesta['respuesta_FRNM__id_pregunta_FRNM__pregunta_FRNM']
        respuesta_usuario = respuesta['respuesta_FRNM__opc_respuesta_FRNM']
        if rut not in dict_respuestas:
            dict_respuestas[rut] = {}
        dict_respuestas[rut][pregunta] = respuesta_usuario

    for rut, respuestas_usuario in dict_respuestas.items():
        fila = [rut]
        for pregunta in preguntas:
            respuesta = respuestas_usuario.get(pregunta.pregunta_FRNM, '')
            fila.append(respuesta)
        ws_FRNM_V2.append(fila) 
   
    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_FRNM_V2)
    background_colors(ws_FRNM_V2)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="Factores No Mod_V2.xlsx"'

    # Guardar el archivo en la respuesta HTTP
    wb.save(response)
    return response

def crear_excel_DS1(request):
    wb = Workbook()
    ws_DSV1 = wb.active
    ws_DSV1.title = "Determinante Salud"

    preguntas =PregDeterSalud.objects.all()
    lista_preguntas = ['RutHash', 'Preguntas', 'Respuestas', 'Fecha Respuesta'] 
    ws_DSV1.append(lista_preguntas)

    usuarios_respuestas = RespDeterSalud.objects.select_related(
    "respuesta_DS", "respuesta_DS__id_pregunta_DS").values("RutHash", "fecha_respuesta",  "respuesta_DS__id_pregunta_DS__pregunta_DS","respuesta_DS__opc_respuesta_DS").order_by('RutHash')

    for respuesta in usuarios_respuestas:

        pregunta = respuesta['respuesta_DS__id_pregunta_DS__pregunta_DS']
        respuesta_usuario = respuesta['respuesta_DS__opc_respuesta_DS']
        fecha_respuesta = respuesta['fecha_respuesta'].replace(tzinfo=None) if respuesta['fecha_respuesta'] else ''
        fila = [
            respuesta['RutHash'],
            pregunta,
            respuesta_usuario,
            fecha_respuesta, 
        ]
        ws_DSV1.append(fila) 

    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_DSV1)
    background_colors(ws_DSV1)

    # Preparar la respuesta HTTP
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="reporte_DS_V1.xlsx"'

    # Guardar el archivo
    wb.save(response)
    return response

def crear_excel_DS2(request):
    wb = Workbook()
    ws_DSV2 = wb.active
    ws_DSV2.title = "Determinante Salud"

    preguntas =PregDeterSalud.objects.all()
    lista_preguntas = ['RutHash'] + [pregunta.pregunta_DS for pregunta in preguntas]
    ws_DSV2.append(lista_preguntas)

    usuarios_respuestas = RespDeterSalud.objects.select_related(
    "respuesta_DS", "respuesta_DS__id_pregunta_DS").values("RutHash", "fecha_respuesta",  "respuesta_DS__id_pregunta_DS__pregunta_DS", "respuesta_DS__opc_respuesta_DS")

    dict_respuestas = {}

    for respuesta in usuarios_respuestas:
        rut = respuesta['RutHash']
        pregunta = respuesta['respuesta_DS__id_pregunta_DS__pregunta_DS']
        respuesta_usuario = respuesta['respuesta_DS__opc_respuesta_DS']
        if rut not in dict_respuestas:
            dict_respuestas[rut] = {}
        dict_respuestas[rut][pregunta] = respuesta_usuario

    for rut, respuestas_usuario in dict_respuestas.items():
        fila = [rut]
        for pregunta in preguntas:
            respuesta = respuestas_usuario.get(pregunta.pregunta_DS, '')
            fila.append(respuesta)
        ws_DSV2.append(fila) 
   
    # Ajustar ancho de columnas y color de fondo 
    ajustar_ancho_columnas(ws_DSV2)
    background_colors(ws_DSV2)

    # Preparar la respuesta HTTP
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="reporte_DS_V2.xlsx"'

    # Guardar el archivo
    wb.save(response)
    return response

# --------------------- Reporteria --------------------- #

# Configuración global para fuentes de gráficos
plt.rcParams['font.family'] = 'sans-serif'  
plt.rcParams['font.sans-serif'] = 'Calibri' 
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] =20
plt.rcParams['axes.labelsize']= 13
plt.rcParams['axes.labelpad']=10

def generar_grafico_usuario_por_edad():

    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT edad, COUNT(*) 
            FROM botApp_usuario u JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1)
            GROUP BY edad 
            ORDER BY edad; """
        )
        resultados = cursor.fetchall()

    edades = []
    cantidades = []

    for resultado in resultados:
        edad, cantidad = resultado
        edades.append(edad)
        cantidades.append(cantidad)
    
    plt.figure(figsize=[18, 8])
    plt.bar(edades, cantidades, color="#79addc")
    plt.xlabel("Edad")
    plt.ylabel("Número de Usuarias")
    plt.title("Usuarias por edad", pad=20)
    plt.xticks(range(min(edades), max(edades) + 1, 1))
    

    # Agregar etiquetas en las barras
    for edad, cantidad in zip(edades, cantidades):
        plt.text(edad, cantidad, str(cantidad), ha='center', va='bottom')

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64


def generar_grafico_anio_nacimiento():
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT YEAR(AnioNacimiento) as anio, COUNT(*) 
            FROM botApp_usuario u JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1)
            GROUP BY YEAR(AnioNacimiento) ORDER BY anio ASC;"""
        )
        resultados = cursor.fetchall()

    anios = []
    cantidades = []

    for resultado in resultados:
        anio, cantidad = resultado
        anios.append(anio)
        cantidades.append(cantidad)

    
    plt.figure(figsize=[18, 8])
    plt.bar(anios, cantidades, color="#79addc")
    plt.xlabel("Año de Nacimiento")
    plt.ylabel("Número de Usuarios")
    plt.title("Usuarias por Año de Nacimiento", pad=20)
    plt.xticks(range(min(anios), max(anios)+1,1), rotation = 90)

    # Agregar etiquetas en las barras
    for anio, cantidad in zip(anios, cantidades):
        plt.text(anio, cantidad, str(cantidad), ha='center', va='bottom')

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def generar_grafico_respuestas_por_dia():
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT DATE(Fecha_Ingreso), COUNT(*) 
            FROM botApp_usuario u JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1)
            GROUP BY DATE(Fecha_Ingreso); """
        )
        resultados = cursor.fetchall()

    fechas = []
    cantidades = []

    for resultado in resultados:
        fecha, cantidad = resultado
        fechas.append(datetime.strftime(fecha, "%d-%m-%Y"))
        cantidades.append(cantidad)

 
    plt.plot(fechas, cantidades, marker="o", linestyle="-", color="#79addc")
    plt.xlabel("Fecha de Respuesta")
    plt.ylabel("Número de Respuestas")
    plt.title("Respuestas por Día", pad=20)
    plt.xticks(rotation = 90)
    plt.tight_layout() 
    
    # Agregar los valores de cada punto
    for fecha, cantidad in zip(fechas, cantidades):
        plt.annotate(f"{cantidad}", (fecha, cantidad), textcoords="offset points", xytext=(0,10), ha='center')

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def generar_grafico_personas_por_genero_NUEVO():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT respuesta_FRNM_id, Count(*)
            FROM botApp_respusuariofactorriesgonomod
            WHERE respuesta_FRNM_id IN(1,2,3)
            group by respuesta_FRNM_id; """
            
        )
        resultados = cursor.fetchall()

    generos = []
    cantidades = []

    for resultado in resultados:
        genero_id, cantidad = resultado
        genero = OpcFactorRiesgoNoMod.objects.get(id=genero_id)
        generos.append(genero.opc_respuesta_FRNM)
        cantidades.append(cantidad)

    # Crear gráfico de barras con diferentes colores para cada barra
    colores = {'Masculino': '#79addc', 'Femenino': '#EFB0C9', 'Otro': '#A5F8CE'}
    plt.bar(generos, cantidades, color=[colores[genero] for genero in generos])

    # Agregar los valores de cada barra
    for i in range(len(generos)):
        plt.text(i, cantidades[i], str(cantidades[i]), ha='center', va='bottom')
   
    plt.xlabel("Género")
    plt.ylabel("Número de Personas")
    plt.title("Ingresos por Género", pad=20)

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64
    
def generar_grafico_ingresos_por_comuna():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT c.nombre_comuna, COUNT(*) AS TotalIngresos 
            FROM botApp_comuna c JOIN botApp_usuario u ON u.Comuna_Usuario_id = c.cod_comuna 
            JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1)
            GROUP BY c.nombre_comuna
            """
        )
        resultados = cursor.fetchall()

    comunas = [result[0] for result in resultados]
    total_ingresos = [result[1] for result in resultados]

    # Configurar el gráfico circular
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(total_ingresos, labels=comunas, autopct=lambda pct: f"{pct:.1f}%\n{int(pct/100 * sum(total_ingresos)+ 0.5)} ingresos", startangle=90)
    ax.axis('equal')  # Asegura que el gráfico sea un círculo en lugar de una elipse
    ax.set_title('Distribución de Ingresos por Comuna', pad=20)

    # Ajustar el tamaño de la fuente en los textos
    for text, autotext in zip(texts, autotexts):
        text.set(size=8)
        autotext.set(size=8)

    # Convertir el gráfico a base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return imagen_base64

def generar_grafico_referencias():
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT u.Referencia, COUNT(*) AS TotalIngresos 
            FROM botApp_usuario u JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
             WHERE respuesta_FRNM_id IN (1)
            GROUP BY u.Referencia;"""
        )
        resultados = cursor.fetchall()

    referencias = [result[0] for result in resultados]
    total_ingresos = [result[1] for result in resultados]

    # Configurar el gráfico circular
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(total_ingresos, labels=referencias, autopct=lambda pct: f"{pct:.1f}%\n{int(pct/100 * sum(total_ingresos))} ingresos", startangle=90)
    ax.axis('equal')  # Asegura que el gráfico sea un círculo en lugar de una elipse
    ax.set_title('Distribución de Ingresos por Referencia', pad=20)

    # Ajustar el tamaño de la fuente en los textos
    for text, autotext in zip(texts, autotexts):
        text.set(size=8)
        autotext.set(size=8)

    # Convertir el gráfico a base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return imagen_base64

def generar_grafico_pregunta1():
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT id_opc_respuesta_id, COUNT(*) 
            FROM botApp_usuariorespuesta u JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND id_opc_respuesta_id IN (1, 2, 3) 
            GROUP BY id_opc_respuesta_id;"""
        )
        resultados = cursor.fetchall()

    labels = []
    sizes = []
    counts = []

    for resultado in resultados:
        id_opc_respuesta, cantidad = resultado
        opcion_respuesta = PreguntaOpcionRespuesta.objects.get(id=id_opc_respuesta)
        labels.append(opcion_respuesta.OPC_Respuesta)
        sizes.append(cantidad)
        counts.append(f"{opcion_respuesta.OPC_Respuesta} - {cantidad}")

    # Configurar el gráfico circular
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=['#79addc', '#EFB0C9', '#A5F8CE'])
    
    # Configurar las etiquetas del gráfico
    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Mostrar el gráfico
    plt.title('¿Te has realizado una mamografía?', pad=20)

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def generar_grafico_pregunta2():
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT id_opc_respuesta_id, COUNT(*) 
            FROM botApp_usuariorespuesta u JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND id_opc_respuesta_id IN (7, 8, 9) 
            GROUP BY id_opc_respuesta_id;"""
        )
        resultados = cursor.fetchall()

    labels = []
    sizes = []
    counts = []

    for resultado in resultados:
        id_opc_respuesta, cantidad = resultado
        opcion_respuesta = PreguntaOpcionRespuesta.objects.get(id=id_opc_respuesta)
        labels.append(opcion_respuesta.OPC_Respuesta)
        sizes.append(cantidad)
        counts.append(f"{opcion_respuesta.OPC_Respuesta} - {cantidad}")

    # Configurar el gráfico circular
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=['#79addc', '#EFB0C9', '#DEB3EB'])
    
    # Configurar las etiquetas del gráfico
    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Mostrar el gráfico
    plt.title('¿Recuerdas cuando fue tu última mamografía?', pad=20)

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def generar_grafico_pregunta3():
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT id_opc_respuesta_id, COUNT(*) 
            FROM botApp_usuariorespuesta u JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND id_opc_respuesta_id IN (10,11,12,13) 
            GROUP BY id_opc_respuesta_id;"""
        )
        resultados = cursor.fetchall()

    labels = []
    sizes = []
    counts = []

    for resultado in resultados:
        id_opc_respuesta, cantidad = resultado
        opcion_respuesta = PreguntaOpcionRespuesta.objects.get(id=id_opc_respuesta)
        labels.append(opcion_respuesta.OPC_Respuesta)
        sizes.append(cantidad)
        counts.append(f"{opcion_respuesta.OPC_Respuesta} - {cantidad}")

    # Configurar el gráfico circular
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=['#DE8F5F', '#FFB26F', '#FFB38E', '#DEB3EB'])
    
    # Configurar las etiquetas del gráfico
    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Mostrar el gráfico
    plt.title('Fecha de la última mamografía', pad=20)

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def generar_grafico_pregunta4():
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT id_opc_respuesta_id, COUNT(*) 
            FROM botApp_usuariorespuesta u JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND id_opc_respuesta_id IN (14, 15, 16, 17) 
            GROUP BY id_opc_respuesta_id;"""
        )
        resultados = cursor.fetchall()

    labels = []
    sizes = []
    counts = []

    for resultado in resultados:
        id_opc_respuesta, cantidad = resultado
        opcion_respuesta = PreguntaOpcionRespuesta.objects.get(id=id_opc_respuesta)
        labels.append(opcion_respuesta.OPC_Respuesta)
        sizes.append(cantidad)
        counts.append(f"{opcion_respuesta.OPC_Respuesta} - {cantidad}")

    # Configurar el gráfico circular
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=['#79addc', '#EFB0C9','#A5F8CE', '#DEB3EB'])
    
    # Configurar las etiquetas del gráfico
    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Mostrar el gráfico
    plt.title('¿Tienes los archivos e informe \nde tu última mamografía?', pad=20)

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def generar_grafico_pregunta5():
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT id_opc_respuesta_id, COUNT(*) 
            FROM botApp_usuariorespuesta u JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND id_opc_respuesta_id IN (18, 19, 20) 
            GROUP BY id_opc_respuesta_id;"""
        )
        resultados = cursor.fetchall()

    labels = []
    sizes = []
    counts = []

    for resultado in resultados:
        id_opc_respuesta, cantidad = resultado
        opcion_respuesta = PreguntaOpcionRespuesta.objects.get(id=id_opc_respuesta)
        labels.append(opcion_respuesta.OPC_Respuesta)
        sizes.append(cantidad)
        counts.append(f"{opcion_respuesta.OPC_Respuesta} - {cantidad}")

    # Configurar el gráfico circular
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=['#79addc', '#EFB0C9', '#A5F8CE'])
    
    # Configurar las etiquetas del gráfico
    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Mostrar el gráfico
    plt.title('¿Te gustaría recibir más información \nsobre el cuidado y prevención del cáncer de mama?', pad=20)

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def generar_grafico_pregunta6():
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT respuesta_FRNM_id, COUNT(*) 
               FROM botApp_respusuariofactorriesgonomod
               WHERE RutHash IN (
               SELECT RutHash
               FROM botApp_respusuariofactorriesgonomod
               WHERE respuesta_FRNM_id = 1
            )
               AND respuesta_FRNM_id IN (4, 5, 6)
               GROUP BY respuesta_FRNM_id;"""
        )
        resultados = cursor.fetchall()

    labels = []
    sizes = []
    counts = []

    for resultado in resultados:
        id_opc_respuesta, cantidad = resultado
        opcion_respuesta = OpcFactorRiesgoNoMod.objects.get(id=id_opc_respuesta)
        labels.append(opcion_respuesta.opc_respuesta_FRNM)
        sizes.append(cantidad)
        counts.append(f"{opcion_respuesta.opc_respuesta_FRNM} - {cantidad}")

    # Configurar el gráfico circular
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=['#79addc', '#EFB0C9', '#A5F8CE'])
    
    # Configurar las etiquetas del gráfico
    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Mostrar el gráfico
    plt.title('¿Tienes un familiar directo con cáncer de mama?\n(hermana, mama, tía, abuela)', pad=20)

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def generar_grafico_mamografia_si_por_edad():

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT us.edad, COUNT(*) as Cantidad 
            FROM botApp_usuariorespuesta ur JOIN botApp_usuario us ON ur.RutHash = us.RutHash 
            JOIN botApp_respusuariofactorriesgonomod r ON us.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND id_opc_respuesta_id IN (1)
            GROUP BY us.edad ORDER BY edad ASC;
            """
        )
        resultados = cursor.fetchall()

    edades = []
    cantidades = []

    for resultado in resultados:
        edad, cantidad = resultado
        edades.append(edad)
        cantidades.append(cantidad)

    if not edades: 
        return None
    
    plt.figure(figsize=[18, 8])
    plt.bar(edades, cantidades, color="#79addc")
    plt.xlabel("Edad")
    plt.ylabel("Número de Usuarias")
    plt.title("Mamografías por edad Respuesta Si", pad=20)
    plt.xticks(range(min(edades), max(edades) + 1, 1))
    plt.yticks(range(0,11,1))

    # Agregar etiquetas en las barras
    for edad, cantidad in zip(edades, cantidades):
        plt.text(edad, cantidad, str(cantidad), ha='center', va='bottom')

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def generar_grafico_mamo_si_por_familiar_directo():
    
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT r.respuesta_FRNM_id, COUNT(DISTINCT r.RutHash) AS cantidad_respuestas
            FROM botApp_respusuariofactorriesgonomod r 
            JOIN botApp_usuariorespuesta ur_mamo ON r.RutHash = ur_mamo.RutHash
            WHERE r.respuesta_FRNM_id IN (4, 5, 6)
            AND r.RutHash IN (
            SELECT DISTINCT r2.RutHash
            FROM botApp_respusuariofactorriesgonomod r2
            WHERE r2.respuesta_FRNM_id = 1
            )
            AND ur_mamo.id_opc_respuesta_id = 1  
            GROUP BY r.respuesta_FRNM_id;
            """
        )
        resultados = cursor.fetchall()

    labels = []
    sizes = []
    counts = []

    for resultado in resultados:
        id_opc_respuesta, cantidad = resultado
        opcion_respuesta = OpcFactorRiesgoNoMod.objects.get(id=id_opc_respuesta)
        labels.append(opcion_respuesta.opc_respuesta_FRNM)
        sizes.append(cantidad)
        counts.append(f"{opcion_respuesta.opc_respuesta_FRNM} - {cantidad}")

    # Configurar el gráfico circular
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=['#79addc', '#EFB0C9', '#A5F8CE'])
    
    # Configurar las etiquetas del gráfico
    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Mostrar el gráfico
    plt.title('Cantidad de usuarias que si se han realizado mamografías y tiene antecedentes familiares', pad=20)

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64


def generar_grafico_mamografia_no_por_edad():

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT us.edad, COUNT(*) as Cantidad 
            FROM botApp_usuariorespuesta ur JOIN botApp_usuario us ON ur.RutHash = us.RutHash
            JOIN botApp_respusuariofactorriesgonomod r ON us.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND id_opc_respuesta_id IN (2)
            GROUP BY edad ORDER BY edad ASC;
            """
        )
        resultados = cursor.fetchall()

    edades = []
    cantidades = []

    for resultado in resultados:
        edad, cantidad = resultado
        edades.append(edad)
        cantidades.append(cantidad)

    plt.figure(figsize=[18, 8])
    plt.bar(edades, cantidades, color="#EFB0C9")
    plt.xlabel("Edad")
    plt.ylabel("Número de Usuarias")
    plt.title("Mamografías por edad Respuesta No", pad=20)
    plt.xticks(range(min(edades), max(edades) + 1, 1))
 
    # Agregar etiquetas en las barras
    for edad, cantidad in zip(edades, cantidades):
        plt.text(edad, cantidad, str(cantidad), ha='center', va='bottom')

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def generar_grafico_mamo_no_por_familiar_directo():
    
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT r.respuesta_FRNM_id, COUNT(DISTINCT r.RutHash) AS cantidad_respuestas
            FROM botApp_respusuariofactorriesgonomod r 
            JOIN botApp_usuariorespuesta ur_mamo ON r.RutHash = ur_mamo.RutHash
            WHERE r.respuesta_FRNM_id IN (4, 5, 6)
            AND r.RutHash IN (
            SELECT DISTINCT r2.RutHash
            FROM botApp_respusuariofactorriesgonomod r2
            WHERE r2.respuesta_FRNM_id = 1
            )
            AND ur_mamo.id_opc_respuesta_id = 2
            GROUP BY r.respuesta_FRNM_id;

           """

        )
        resultados = cursor.fetchall()

    labels = []
    sizes = []
    counts = []

    for resultado in resultados:
        id_opc_respuesta, cantidad = resultado
        opcion_respuesta = OpcFactorRiesgoNoMod.objects.get(id=id_opc_respuesta)
        labels.append(opcion_respuesta.opc_respuesta_FRNM)
        sizes.append(cantidad)
        counts.append(f"{opcion_respuesta.opc_respuesta_FRNM} - {cantidad}")

    # Configurar el gráfico circular
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=['#79addc', '#EFB0C9', '#A5F8CE'])
    
    # Configurar las etiquetas del gráfico
    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Mostrar el gráfico
    plt.title('Cantidad de usuarias que no se han realizado mamografías y tiene antecedentes familiares', pad=20)

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def mamografia_por_edad_si_no():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT us.edad, COUNT(*) as Cantidad, ur.id_opc_respuesta_id
            FROM botApp_usuariorespuesta ur 
            JOIN botApp_usuario us ON ur.RutHash = us.RutHash JOIN botApp_respusuariofactorriesgonomod r ON us.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND id_opc_respuesta_id IN (1,2) 
            GROUP BY edad, ur.id_opc_respuesta_id 
            ORDER BY edad ASC;
            """
        )
        resultados = cursor.fetchall()

    edades = []
    cantidades_si = []
    cantidades_no = []

    # Iteramos sobre los resultados
    for resultado in resultados:
        edad, cantidad, respuesta = resultado

        # Si la edad no está en la lista, la agregamos con inicialización de cantidades
        if edad not in edades:
            edades.append(edad)
            cantidades_si.append(0)  
            cantidades_no.append(0)  

        # Obtenemos el índice correspondiente a la edad
        index = edades.index(edad)

        if respuesta == 1:
            cantidades_si[index] += cantidad
        elif respuesta == 2: 
            cantidades_no[index] += cantidad

    # Crear el gráfico
    plt.figure(figsize=[18, 8])
    plt.bar(edades, cantidades_si, color="#79addc", label="Cantidad Sí")
    plt.bar(edades, cantidades_no, color="#EFB0C9", bottom=cantidades_si, label="Cantidad No")
    plt.xlabel("Edad")
    plt.ylabel("Número de Usuarias")
    plt.title("Mamografías por Edad", pad=20)
    plt.xticks(range(min(edades), max(edades) + 1, 1)) 
    plt.legend()

    # Agregar etiquetas para las barras de cantidades_si
    for edad, cantidad_si, cantidad_no in zip(edades, cantidades_si, cantidades_no):
        if cantidad_si > 0:
            plt.text(edad, cantidad_si - cantidad_si / 2,  
                 str(cantidad_si), ha='center', va='bottom', color='black')

    # Agregar etiquetas para las barras de cantidades_no
    for edad, cantidad_si, cantidad_no in zip(edades, cantidades_si, cantidades_no):
        if cantidad_no > 0:
            plt.text(edad, cantidad_si + cantidad_no - cantidad_no / 2,  
                str(cantidad_no), ha='center', va='top', color='black')

   # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def generar_grafico_tiempo_trascurrido():

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT tiempo_transc_ult_mamografia, COUNT(*) 
            FROM botApp_ultima_mamografia_anio u JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) 
            GROUP BY tiempo_transc_ult_mamografia ORDER BY tiempo_transc_ult_mamografia ASC;
            """
        )
        resultados = cursor.fetchall()

    rango_uno_etiqueta = "1"
    rango_dos_etiqueta = "2"
    rango_tres_etiqueta = "Más de 3"

    opciones_anios = [rango_uno_etiqueta, rango_dos_etiqueta, rango_tres_etiqueta]
    cantidades = [0, 0, 0]

    for resultado in resultados:
        anio, cantidad = resultado
        if anio == 1:
            cantidades[0] += cantidad
        elif anio == 2:
            cantidades[1] += cantidad
        elif anio == 3:
            cantidades[2] += cantidad

    plt.figure(figsize=[18, 8])
    plt.bar(opciones_anios, cantidades, color="#79addc")
    plt.xlabel("Años transcurridos")
    plt.ylabel("Cantidad de usuarias")
    plt.title("Tiempo transcurrido desde última mamografía", pad=20)

    # Agregar etiquetas en las barras
    for i, cantidad in enumerate(cantidades):
        plt.text(i, cantidad, str(cantidad), ha='center', va='bottom')

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64


def generar_grafico_por_rango_edad():

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT edad, COUNT(*) 
            FROM botApp_usuario  u JOIN botApp_respusuariofactorriesgonomod r ON u.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) 
            GROUP BY edad ORDER BY edad;
            """
        )
        resultados = cursor.fetchall()

    r_uno_edad_eti = "Menor de 50 años"
    r_dos_edad_eti = "Entre 50 y 69 años"
    r_tres_edad_eti = "Mayor a 69 años"
    opciones_edad = [r_uno_edad_eti, r_dos_edad_eti, r_tres_edad_eti]
    cantidades = [0, 0, 0]

    edad_min = 50
    edad_max = 69

    for resultado in resultados:
        edad, cantidad = resultado
        if edad <edad_min:
            cantidades[0] += cantidad
        elif edad >= edad_min and edad <= edad_max:
            cantidades[1] += cantidad
        elif edad > edad_max :
            cantidades[2] += cantidad

    plt.figure(figsize=[18, 8])
    plt.bar(opciones_edad, cantidades, color=['#DE8F5F', '#FFB26F', '#FFB38E'])
    plt.xlabel("Rango de edad según guía clínica")
    plt.ylabel("Cantidad de usuarias")
    plt.title("Cantidad de usuarias por rango de edad", pad=20)

    # Agregar etiquetas en las barras
    for i, cantidad in enumerate(cantidades):
        plt.text(i, cantidad, str(cantidad), ha='center', va='bottom')

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def mamografia_por_edad_si_no_rango_edad():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT us.edad, COUNT(*) as Cantidad, ur.id_opc_respuesta_id
            FROM botApp_usuariorespuesta ur 
            JOIN botApp_usuario us ON ur.RutHash = us.RutHash  JOIN botApp_respusuariofactorriesgonomod r ON us.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND id_opc_respuesta_id IN (1,2)
            GROUP BY edad, ur.id_opc_respuesta_id 
            ORDER BY edad ASC;
            """
        )
        resultados = cursor.fetchall()

    r_uno_edad_eti = "Menor de 50 años"
    r_dos_edad_eti = "Entre 50 y 69 años"
    r_tres_edad_eti = "Mayor a 69 años"
    opciones_anios = [r_uno_edad_eti, r_dos_edad_eti, r_tres_edad_eti]
    cantidades_si = [0, 0, 0]
    cantidades_no = [0, 0, 0]

    edad_min = 50
    edad_max = 69

    # Iteramos sobre los resultados
    for resultado in resultados:
        edad, cantidad, respuesta = resultado

        if edad < edad_min and respuesta == 1:
            cantidades_si[0] += cantidad
        elif edad >= edad_min and edad <= edad_max and respuesta == 1:
            cantidades_si[1] += cantidad
        elif edad > edad_max and respuesta == 1:
            cantidades_si[2] += cantidad 
        elif edad < edad_min and respuesta == 2:
            cantidades_no[0] += cantidad
        elif edad >= edad_min and edad <= edad_max and respuesta == 2:
            cantidades_no[1] += cantidad
        elif edad > edad_max and respuesta == 2:
            cantidades_no[2] += cantidad 

    # Crear el gráfico
    plt.figure(figsize=[18, 8])
    plt.bar(opciones_anios, cantidades_si, color="#79addc", label="Cantidad Sí")
    plt.bar(opciones_anios, cantidades_no, color="#EFB0C9", bottom=cantidades_si, label="Cantidad No")
    plt.xlabel("Rango de edad según guía clínica")
    plt.ylabel("Número de Usuarias")
    plt.title("Mamografías por rango de Edad", pad=20)
    plt.legend()

    # Agregar etiquetas para las barras de cantidades_si
    for edad, cantidad_si, cantidad_no in zip(opciones_anios, cantidades_si, cantidades_no):
        if cantidad_si > 0:
            plt.text(edad, cantidad_si - cantidad_si / 2,  
                 str(cantidad_si), ha='center', va='bottom', color='black')

    # Agregar etiquetas para las barras de cantidades_no
    for edad, cantidad_si, cantidad_no in zip(opciones_anios, cantidades_si, cantidades_no):
        if cantidad_no > 0:
            plt.text(edad, cantidad_si + cantidad_no - cantidad_no / 2,  
                str(cantidad_no), ha='center', va='top', color='black')

   # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def mamografia_por_edad_si_no_rango_edad_agrupado():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT us.edad, COUNT(*) as Cantidad, ur.id_opc_respuesta_id
            FROM botApp_usuariorespuesta ur 
            JOIN botApp_usuario us ON ur.RutHash = us.RutHash JOIN botApp_respusuariofactorriesgonomod r ON us.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND id_opc_respuesta_id IN (1,2)
            GROUP BY edad, ur.id_opc_respuesta_id 
            ORDER BY edad ASC;
            """
        )
        resultados = cursor.fetchall()

    opciones_anios = ["Menores de 50", "50 a 69", "Desde los 70"]
    cantidades_si = [0, 0, 0]
    cantidades_no = [0, 0, 0]

    # Iteramos sobre los resultados
    for resultado in resultados:
        edad, cantidad, respuesta = resultado

        if edad < 50 and respuesta == 1:
            cantidades_si[0] += cantidad
        elif edad >= 50 and edad <= 69 and respuesta == 1:
            cantidades_si[1] += cantidad
        elif edad > 69 and respuesta == 1:
            cantidades_si[2] += cantidad 
        elif edad < 50 and respuesta == 2:
            cantidades_no[0] += cantidad
        elif edad >= 50 and edad <= 69 and respuesta == 2:
            cantidades_no[1] += cantidad
        elif edad > 69 and respuesta == 2:
            cantidades_no[2] += cantidad 

    x = np.arange(len(opciones_anios))  
    width = 0.35  

    fig, ax = plt.subplots(figsize=[18, 8])
    rects1 = ax.bar(x - width/2, cantidades_si, width, label='Cantidad Sí', color = '#79addc')
    rects2 = ax.bar(x + width/2, cantidades_no, width, label='Cantidad No', color="#EFB0C9")

    ax.set_xlabel("Rango de edad guía clínica")
    ax.set_ylabel("Número de Usuarias")
    ax.set_title("Mamografías por rango de Edad", pad=20)

    ax.set_xticks(x)
    ax.set_xticklabels(opciones_anios)
    plt.legend()

    # Etiquetas en las barras
    ax.bar_label(rects1, padding=3, color="black")
    ax.bar_label(rects2, padding=3, color="black")

   # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def grafico_prev_salud_por_rango_edad():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT us.edad, COUNT(*) as Cantidad, ds.respuesta_DS_id
            FROM botApp_usuario us JOIN  botApp_respdetersalud ds ON us.RutHash = ds.RutHash
            JOIN botApp_respusuariofactorriesgonomod r ON us.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND ds.respuesta_DS_id IN(4,5,6)
            GROUP BY edad, respuesta_DS_id 
            ORDER BY edad ASC;
            """
        )
        resultados = cursor.fetchall()

    r_uno_edad_eti = "Menor de 50 años"
    r_dos_edad_eti = "Entre 50 y 69 años"
    r_tres_edad_eti = "Mayor a 69 años"
    opciones_anios = [r_uno_edad_eti, r_dos_edad_eti, r_tres_edad_eti]
    cantidades_fonasa = [0, 0, 0]
    cantidades_isapre = [0, 0, 0]
    cantidades_otro = [0, 0, 0]

    edad_min = 50
    edad_max = 69

    # Iteramos sobre los resultados
    for edad, cantidad, respuesta in resultados:
        index = 0 if edad < edad_min else (1 if edad <= edad_max else 2)
        
        if respuesta == 4:
            cantidades_fonasa[index] += cantidad
        elif respuesta == 5:
            cantidades_isapre[index] += cantidad
        elif respuesta == 6:
            cantidades_otro[index] += cantidad

    # Crear el gráfico
    plt.figure(figsize=[18, 8])
    plt.bar(opciones_anios, cantidades_fonasa, color="#a0b3a8", label="Cantidad Fonasa")
    plt.bar(opciones_anios, cantidades_isapre, color="#c6a78f", bottom=cantidades_fonasa, label="Cantidad Isapre")
    plt.bar(opciones_anios, cantidades_otro, color="#ecc8c9", bottom=np.array(cantidades_fonasa) + np.array(cantidades_isapre), label="Cantidad Otro")
    plt.xlabel("Rango de edad según guía clínica")
    plt.ylabel("Número de Usuarias")
    plt.title("Previsión de salud por rango de Edad", pad=20)
    plt.legend()

    # Agregar etiquetas para las barras de cantidades_fonasa
    for i, (edad, cantidad_fonasa) in enumerate(zip(opciones_anios, cantidades_fonasa)):
        if cantidad_fonasa > 0:
            plt.text(i, cantidad_fonasa / 2, str(cantidad_fonasa), ha='center', va='center', color='black', fontsize=10, fontweight='bold')

    # Agregar etiquetas para las barras de cantidades_isapre
    for i, (edad, cantidad_fonasa, cantidad_isapre) in enumerate(zip(opciones_anios, cantidades_fonasa, cantidades_isapre)):
        if cantidad_isapre > 0:
            plt.text(i, cantidad_fonasa + cantidad_isapre / 2, str(cantidad_isapre), ha='center', va='center', color='black', fontsize=10, fontweight='bold')

    # Agregar etiquetas para la barra de cantidades_otro
    for i, (edad, cantidad_fonasa, cantidad_isapre, cantidad_otro) in enumerate(zip(opciones_anios, cantidades_fonasa, cantidades_isapre, cantidades_otro)):
        if cantidad_otro > 0:
            plt.text(i, cantidad_fonasa + cantidad_isapre + cantidad_otro / 2, str(cantidad_otro), ha='center', va='center', color='black', fontsize=10, fontweight='bold')

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=300)
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def grafico_escolaridad():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT respuesta_DS_id, COUNT(*) 
            FROM botApp_respdetersalud us JOIN botApp_respusuariofactorriesgonomod r ON us.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND respuesta_DS_id IN (1,2,3) 
            GROUP BY respuesta_DS_id;
            """
        )
        resultados = cursor.fetchall()

    labels = []
    sizes = []
    counts = []

    for resultado in resultados:
        id_opc_respuesta, cantidad = resultado
        opcion_respuesta = OpcDeterSalud.objects.get(id=id_opc_respuesta)
        labels.append(opcion_respuesta.opc_respuesta_DS)
        sizes.append(cantidad)
        counts.append(f"{opcion_respuesta.opc_respuesta_DS} - {cantidad}")

    # Configurar el gráfico circular
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=['#79addc', '#EFB0C9', '#A5F8CE'])
    
    # Configurar las etiquetas del gráfico
    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Mostrar el gráfico
    plt.title('Nivel de estudio usuarias', pad=20)

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

def grafico_frecuencia_alcohol():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT respuesta_FRM_id, COUNT(*) 
            FROM botApp_respusuariofactorriesgomod us JOIN botApp_respusuariofactorriesgonomod r ON us.RutHash = r.RutHash
            WHERE respuesta_FRNM_id IN (1) AND respuesta_FRM_id IN (3,4,5) 
            GROUP BY respuesta_FRM_id;
            """
        )
        resultados = cursor.fetchall()

    labels = []
    sizes = []
    counts = []

    for resultado in resultados:
        id_opc_respuesta, cantidad = resultado
        opcion_respuesta = OpcFactorRiesgoMod.objects.get(id=id_opc_respuesta)
        labels.append(opcion_respuesta.opc_respuesta_FRM)
        sizes.append(cantidad)
        counts.append(f"{opcion_respuesta.opc_respuesta_FRM} - {cantidad}")

    # Configurar el gráfico circular
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=['#79addc', '#EFB0C9', '#A5F8CE'])
    
    # Configurar las etiquetas del gráfico
    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Mostrar el gráfico
    plt.title('Consumo de Alcohol', pad=20)

    # Guardar la imagen en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return imagen_base64

@login_required
def reportes(request):
    data = {
        "imagen_base64_edad": generar_grafico_usuario_por_edad(),
        "imagen_base64_ingresos": generar_grafico_respuestas_por_dia(),
        "imagen_base64_ingresos_comuna": generar_grafico_ingresos_por_comuna(),
        "imagen_base64_pregunta1": generar_grafico_pregunta1(),
        "imagen_base64_pregunta2": generar_grafico_pregunta2(),
        "imagen_base64_pregunta3": generar_grafico_pregunta3(),
        "imagen_base64_pregunta4": generar_grafico_pregunta4(),
        "imagen_base64_pregunta5": generar_grafico_pregunta5(),
        "imagen_base64_pregunta6": generar_grafico_pregunta6(),  
        "imagen_base64_referencias": generar_grafico_referencias(), 
        "imagen_base64_anios_nacimiento": generar_grafico_anio_nacimiento(),
        "imagen_base64_mamografia_si_por_edad":generar_grafico_mamografia_si_por_edad(),
        "imagen_base64_mamografia_no_por_edad":generar_grafico_mamografia_no_por_edad(),
        "imagen_base64_mamografia_por_edad_si_no": mamografia_por_edad_si_no(),
        "imagen_base64_tiempo_transc": generar_grafico_tiempo_trascurrido(),
        "imagen_base64_rango_edad": generar_grafico_por_rango_edad(),
        "imagen_base64_mamografia_si_no_rango_edad": mamografia_por_edad_si_no_rango_edad(),
        "imagen_base64_mamo_si_por_familiar_directo":generar_grafico_mamo_si_por_familiar_directo(),
        "imagen_base64_mamo_no_por_familiar_directo":generar_grafico_mamo_no_por_familiar_directo(),
        "imagen_base64_mamografia_si_no_rango_edad_agrupadas": mamografia_por_edad_si_no_rango_edad_agrupado(),
        "imagen_base64_grafico_prev_salud_por_rango_edad":grafico_prev_salud_por_rango_edad(),
        "imagen_base64_grafico_consumo_alcohol":grafico_frecuencia_alcohol(),
        "imagen_base64_grafico_escolaridad":grafico_escolaridad(),
        "imagen_base64_grafico_genero_nuevo":generar_grafico_personas_por_genero_NUEVO(), 
        
        }
    return render(request, "reportes.html", data)


# --------------------- Formulario WEB --------------------- #
@login_required
def formulario(request):
    data = {
        "formUsuario": UsuarioForm(),
        "preguntas": Pregunta.objects.all(),
        "usuarios": User.objects.all(),
    }

    if request.method == "POST":
        form_usuario = UsuarioForm(request.POST)

        if form_usuario.is_valid():
            form_usuario.instance.id_usuario = request.POST.get("id_usuario")
            usuario = form_usuario.save()

            for pregunta in data["preguntas"]:
                respuesta = request.POST.get(f"pregunta_{pregunta.id}")
                opc_respuesta = OPC_Respuesta(
                    id_pregunta=pregunta, OPC_Respuesta=respuesta
                )
                opc_respuesta.save()
                respuesta_usuario = RespuestaUsuario(
                    id_usuario=usuario,
                    id_pregunta=pregunta,
                    id_opc_respuesta=opc_respuesta,
                )
                respuesta_usuario.save()

            messages.success(request, "Datos guardados correctamente")
            form_usuario = UsuarioForm()
            return redirect(to="home")

        else:
            print(form_usuario.errors)
            messages.error(
                request,
                "La persona debe tener más de 18 años y haber nacido después de 1930.",
            )
            form_usuario = UsuarioForm()

    return render(request, "formulario.html", data)


# --------------------- Preguntas --------------------- #

# Listar Preguntas
@login_required
def listarPreguntas(request):
    Preguntas = Pregunta.objects.all()
    data = {
        "preguntas": Preguntas,
    }
    return render(request, "preguntas/listarPreguntas.html", data)


# Modificar Pregunta
@login_required
def modificarPregunta(request, id):
    Preguntas = Pregunta.objects.get(id=id)
    data = {"form": PreguntaForm(instance=Preguntas)}

    if request.method == "POST":
        formulario = PreguntaForm(
            data=request.POST, instance=Preguntas, files=request.FILES
        )
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Modificado Correctamente")
            return redirect(to="listarPreguntas")
        data["form"] = formulario

    return render(request, "preguntas/modificarPreguntas.html", data)


# Eliminar Pregunta
@login_required
def eliminarPregunta(request, id):
    Preguntas = Pregunta.objects.get(id=id)
    Preguntas.delete()
    messages.success(request, "Eliminado Correctamente")
    return redirect(to="listarPreguntas")


# Crear Pregunta
@login_required
def crearPregunta(request):
    data = {"form": PreguntaForm()}

    if request.method == "POST":
        formulario = PreguntaForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Pregunta Creada Correctamente")
        else:
            data["form"] = formulario

    return render(request, "preguntas/crearPreguntas.html", data)


# --------------------- Mensajes --------------------- #
@login_required
def homeMensajes(request):
    Mensajes = MensajeContenido.objects.all()
    data = {
        "mensajes": Mensajes,
    }
    return render(request, "mensajes/homeMensajes.html", data)

@login_required
def crearMensaje(request):
    data = {"form": MensajeContenidoForm()}

    if request.method == "POST":
        formulario = MensajeContenidoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Mensaje Creado Correctamente")
        else:
            data["form"] = formulario

    return render(request, "mensajes/crearMensajes.html", data)

@login_required
def modificarMensaje(request, id):
    Mensajes = MensajeContenido.objects.get(id=id)
    data = {"form": MensajeContenidoForm(instance=Mensajes)}

    if request.method == "POST":
        formulario = MensajeContenidoForm(
            data=request.POST, instance=Mensajes, files=request.FILES
        )
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Modificado Correctamente")
            return redirect(to="mensajesHome")
        data["form"] = formulario

    return render(request, "mensajes/modificarMensajes.html", data)

@login_required
def eliminarMensaje(request, id):
    Mensajes = MensajeContenido.objects.get(id=id)
    Mensajes.delete()
    messages.success(request, "Eliminado Correctamente")
    return redirect(to="mensajesHome")

# --------------------- Api --------------------- #

@login_required
def apiHome(request):
    return render(request, "api/apiHome.html")

#Usuario
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

#RespuestaUsuario
class UsuarioRespuestaViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRespuesta.objects.all()
    serializer_class = UsuarioRespuestaSerializer

#TextoPreguntaUsuario
class UsuarioTextoPreguntaViewSet(viewsets.ModelViewSet):
    queryset = UsuarioTextoPregunta.objects.all()
    serializer_class = UsuarioTextoPreguntaSerializer
    
#MensajeContenido
class MensajeContenidoViewSet(viewsets.ModelViewSet):
    queryset = MensajeContenido.objects.all()
    serializer_class = MensajeContenidoSerializer

#Factor riesgo no modificable
class FRNMViewSet(viewsets.ModelViewSet):
    queryset = RespUsuarioFactorRiesgoNoMod.objects.all()
    serializer_class = UsuarioRespuestaFRNMSerializer

#Factor riesgo modificable
class FRMViewSet(viewsets.ModelViewSet):
    queryset = RespUsuarioFactorRiesgoMod.objects.all()
    serializer_class = UsuarioRespuestaFRMSerializer

#Determinante salud
class DSViewSet(viewsets.ModelViewSet):
    queryset = RespDeterSalud.objects.all()
    serializer_class = UsuarioRespuestaDSSerializer

# Respuesta Texto Peso y Altura (FRM)
class RespTextoFRMViewSet(viewsets.ModelViewSet):
    queryset = RespTextoFRM.objects.all()
    serializer_class = RespTextoFRMSerializer

class UsuarioRespuestaAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    def get(self, request):
        respuestas = UsuarioRespuesta.objects.all()
        serializer = UsuarioRespuestaSerializer(respuestas, many=True)
        return Response(serializer.data)

class UsuarioTextoPreguntaAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    def get(self, request):
        textos_pregunta = UsuarioTextoPregunta.objects.all()
        serializer = UsuarioTextoPreguntaSerializer(textos_pregunta, many=True)
        return Response(serializer.data)

class UsuarioAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    def get(self, request):
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)
    
class MensajeContenidoAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    def get(self, request):
        mensajes = MensajeContenido.objects.all()
        serializer = MensajeContenidoSerializer(mensajes, many=True)
        return Response(serializer.data)
    
class ObtenerID(APIView):
    def get(self, request):
        # Obtener la fecha de hoy
        fecha_hoy = date.today()
        
        # Buscar un registro en la tabla que coincida con la fecha de hoy
        registro_hoy = MensajeContenido.objects.filter(fecha=fecha_hoy).first()
        
        if registro_hoy:
            # Si se encuentra un registro para la fecha de hoy, devolverlo
            return Response({'id': registro_hoy.id, 'texto': registro_hoy.texto, 'genero': registro_hoy.Genero_Usuario.OPC_Genero})
        else:
            # Si no se encuentra ningún registro para la fecha de hoy, devolver un código de error
            return Response({'error_code': '1'})
        
class UsuarioRespuestFRNMaAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    def get(self, request):
        respuestas = RespUsuarioFactorRiesgoNoMod.objects.all()
        serializer = UsuarioRespuestaFRNMSerializer(respuestas, many=True)
        return Response(serializer.data)
    
class UsuarioRespuestFRMaAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    def get(self, request):
        respuestas = RespUsuarioFactorRiesgoMod.objects.all()
        serializer = UsuarioRespuestaFRMSerializer(respuestas, many=True)
        return Response(serializer.data)
    
class RespTextoFRMAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    def get(self, request):
        respuestas = RespTextoFRM.objects.all()
        serializer = RespTextoFRMSerializer(respuestas, many=True)
        return Response(serializer.data)

# --------------------- Api --------------------- #
def obtener_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        fecha_formateada = usuario.AnioNacimiento.strftime("%d/%m/%Y") if usuario.AnioNacimiento else None

        return JsonResponse({
            "nombre": usuario.nombre,
            "fecha_nacimiento": usuario.fecha_nacimiento,
            "AnioNacimiento": fecha_formateada  
        })
    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

def generar_hash(valor):
    """Genera el hash SHA-256 del Rut"""
    return hashlib.sha256(valor.encode()).hexdigest()

@csrf_exempt
def consultar_estado_pregunta(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    try:
        data = JSONParser().parse(request)
    except Exception:
        return JsonResponse({"error": "Error al leer el JSON, asegúrate de que el formato es correcto."}, status=400)

    # Validar que ManyChat envió el Rut
    if "Rut" not in data:
        return JsonResponse({"error": "El campo 'Rut' es obligatorio en la petición."}, status=400)

    # Encriptar el Rut para compararlo con RutHash
    rut_encriptado = generar_hash(data["Rut"])

    # Verificar si el usuario existe en la BD
    usuario_model = Usuario.objects.filter(RutHash=rut_encriptado).first()
    
    if not usuario_model:
        return JsonResponse({"respondido": "false"})

    # Inicializar respuesta como False
    respondido = False

    # Verificar el tipo de pregunta
    if data["tipo_pregunta"] == "TM":
        pregunta_model = Pregunta.objects.filter(pregunta=data["nombre_pregunta"]).first()
        if pregunta_model:
            id_pregunta = pregunta_model.id
            opcion_respuesta_model = list(PreguntaOpcionRespuesta.objects.filter(id_pregunta=id_pregunta).values_list("id", flat=True))
            respuesta = list(UsuarioRespuesta.objects.filter(RutHash=rut_encriptado, id_opc_respuesta__in=opcion_respuesta_model).values_list("id", flat=True))
            respondido = len(respuesta) > 0

    elif data["tipo_pregunta"] == "DS":
        pregunta_model = PregDeterSalud.objects.filter(pregunta_DS=data["nombre_pregunta"]).first()
        if pregunta_model:
            id_pregunta = pregunta_model.id
            opcion_respuesta_model = list(OpcDeterSalud.objects.filter(id_pregunta_DS=id_pregunta).values_list("id", flat=True))
            respuesta = list(RespDeterSalud.objects.filter(RutHash=rut_encriptado, respuesta_DS__in=opcion_respuesta_model).values_list("id", flat=True))
            respondido = len(respuesta) > 0

    elif data["tipo_pregunta"] == "FRM":
        pregunta_model = PregFactorRiesgoMod.objects.filter(pregunta_FRM=data["nombre_pregunta"]).first()
        if pregunta_model:
            id_pregunta = pregunta_model.id
            opcion_respuesta_model = list(OpcFactorRiesgoMod.objects.filter(id_pregunta_FRM=id_pregunta).values_list("id", flat=True))
            respuesta = list(RespUsuarioFactorRiesgoMod.objects.filter(RutHash=rut_encriptado, respuesta_FRM__in=opcion_respuesta_model).values_list("id", flat=True))
            respondido = len(respuesta) > 0

        # Verificación específica para peso y altura
        """if "peso" in data["nombre_pregunta"].lower() or "altura" in data["nombre_pregunta"].lower():
            calculo_model = CalculoFRM.objects.filter(RutHash=rut_encriptado).first()
            if calculo_model:
                # Verificar si ambos valores (peso y altura) están presentes y son mayores que 0
                if calculo_model.peso_mod > 0 and calculo_model.altura_mod > 0:
                    respondido = True"""

    elif data["tipo_pregunta"] == "FRNM":
        pregunta_model = PregFactorRiesgoNoMod.objects.filter(pregunta_FRNM=data["nombre_pregunta"]).first()
        if pregunta_model:
            id_pregunta = pregunta_model.id
            opcion_respuesta_model = list(OpcFactorRiesgoNoMod.objects.filter(id_pregunta_FRNM=id_pregunta).values_list("id", flat=True))
            respuesta = list(RespUsuarioFactorRiesgoNoMod.objects.filter(RutHash=rut_encriptado, respuesta_FRNM__in=opcion_respuesta_model).values_list("id", flat=True))
            respondido = len(respuesta) > 0

    # Devolver la respuesta
    return JsonResponse({
        "respondido": "true" if respondido else "false"
    })

@csrf_exempt
def retorna_genero(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    try:
        data = JSONParser().parse(request)
    except Exception:
        return JsonResponse({"error": "Error al leer el JSON, asegúrate de que el formato es correcto."}, status=400)

    # Validar que ManyChat envió el Rut
    if "Rut" not in data:
        return JsonResponse({"error": "El campo 'Rut' es obligatorio en la petición."}, status=400)

    # Encriptar el Rut para compararlo con RutHash
    rut_encriptado = generar_hash(data["Rut"])

    # Verificar si el usuario existe en la BD
    usuario_model = Usuario.objects.filter(RutHash=rut_encriptado).first()

    if usuario_model:
        pregunta_model = PregFactorRiesgoNoMod.objects.filter(pregunta_FRNM= "¿Cuál es tu género?").first()
        id_pregunta = pregunta_model.id
        opcion_respuesta_model = list(OpcFactorRiesgoNoMod.objects.filter(id_pregunta_FRNM=id_pregunta).values_list("id", flat=True))
        respuesta = RespUsuarioFactorRiesgoNoMod.objects.filter(RutHash=rut_encriptado, respuesta_FRNM__in=opcion_respuesta_model).first()
        #opcion = OpcFactorRiesgoNoMod.objects.filter(id=respuesta.respuesta_FRNM)
        return JsonResponse({"genero": respuesta.respuesta_FRNM.id})
    else:
        return JsonResponse({"error": "usuario no existe"})
    
@csrf_exempt
def verificar_usuario(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    try:
        data = JSONParser().parse(request)
    except Exception as e:
        return JsonResponse({"error": f"Error al leer el JSON: {str(e)}"}, status=400)

    # Validar que el campo 'Rut' esté presente
    if "Rut" not in data:
        return JsonResponse({"error": "El campo 'Rut' es obligatorio en la petición."}, status=400)

    # Encriptar el Rut para compararlo con RutHash
    rut_encriptado = generar_hash(data["Rut"])

    try:
        # Verificar si el usuario existe en la BD
        usuario_model = Usuario.objects.filter(RutHash=rut_encriptado).first()

        if usuario_model:
            return JsonResponse({"existe": "true"})
        else:
            return JsonResponse({"existe": "false"})

    except Exception as e:
        # Manejo de errores inesperados
        return JsonResponse({"error": f"Error interno del servidor: {str(e)}"}, status=500)

