from django.db import models


# Create your models here.
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime
from dateutil import parser
from unidecode import unidecode 
from fuzzywuzzy import fuzz
from .utils import encrypt_data, decrypt_data
from cryptography.fernet import Fernet
import hashlib
import base64
import os
from django.conf import settings

import locale
import re

locale.setlocale(locale.LC_TIME, 'es_ES') 

cipher_suite = Fernet(settings.ENCRYPT_KEY)

class Usuario(models.Model):
    id_manychat = models.IntegerField(primary_key=True, verbose_name="ID Manychat")
    AnioNacimiento = models.DateField(verbose_name="Fecha de Nacimiento", null=True, blank=True)
    Whatsapp = models.CharField(max_length=255)  # Se almacena cifrado
    Comuna_Usuario = models.ForeignKey('comuna', on_delete=models.CASCADE)
    Referencia = models.CharField(max_length=200)
    Fecha_Ingreso = models.DateTimeField(default=timezone.now)
    edad = models.IntegerField(default=0)
    fecha_nacimiento = models.CharField(max_length=30, null=True, blank=True)

    def get_whatsapp_descifrado(self):
        return decrypt_data(self.Whatsapp) if self.Whatsapp else None
    
    def calculo_edad(self):
        if self.AnioNacimiento:
            fecha_actual = date.today()
            edad = fecha_actual.year - self.AnioNacimiento.year
            edad -= ((fecha_actual.month, fecha_actual.day) < (self.AnioNacimiento.month, self.AnioNacimiento.day))
            return edad
        return 0

    def validar_fecha_nacimiento(self):
        if not self.fecha_nacimiento:
            return None

        meses_correctos = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]

        fecha_normalizada = unidecode(self.fecha_nacimiento.lower())

        for mes in meses_correctos:
            palabras_fecha = fecha_normalizada.split()
            for palabra in palabras_fecha:
                puntaje = fuzz.ratio(palabra, mes)
                if puntaje > 70:
                    fecha_normalizada = fecha_normalizada.replace(palabra, mes)

        formatos_fecha = [
            "%d/%m/%Y", "%d-%m-%Y", "%d %B %Y", "%d de %B de %Y",
            "%d %m %Y", "%d/%m/%y", "%d-%m-%y", "%d %m %y",
            "%d de %B del %Y", "%d de %B del %y", "%d de %B %y",
            "%d de %B %Y", "%d de %b %Y", "%d de %b %y",
            "%d de %b del %Y", "%d de %b del %y"
        ]

        for formato in formatos_fecha:
            try:
                fecha_convertida = datetime.strptime(fecha_normalizada, formato).date()
                return fecha_convertida
            except ValueError:
                continue

        raise ValidationError(
            f"Formato de fecha inválido. Recibido: '{self.fecha_nacimiento}'. Usa dd/mm/yyyy, dd-mm-yyyy, o 'día de mes de año'."
        )

    def save(self, *args, **kwargs):
        # Validar y convertir fecha de nacimiento
        if self.fecha_nacimiento:
            try:
                fecha_validada = self.validar_fecha_nacimiento()
                if fecha_validada:
                    self.AnioNacimiento = fecha_validada
            except ValidationError as e:
                raise e

        if self.Whatsapp and not self.Whatsapp.startswith("gAAAA"):
            self.Whatsapp = encrypt_data(self.Whatsapp).decode()

        # Calcular edad antes de guardar
        self.edad = self.calculo_edad()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id_manychat}"
    
class Codigos_preg (models.Model):
    id = models.AutoField(primary_key=True, verbose_name= "ID códigos preguntas")
    codigo_preguntas = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.codigo_preguntas
    
class PregTamizaje(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Pregunta")
    pregunta = models.CharField(max_length=200)
    codigo_preguntas = models.ForeignKey(Codigos_preg, on_delete = models.CASCADE, null=True)

    def __str__(self):
        return self.pregunta

class OpcTamizaje(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Opcion Respuesta")
    id_pregunta = models.ForeignKey(PregTamizaje, on_delete=models.CASCADE)
    opc_respuesta_TM = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.id_pregunta} - {self.opc_respuesta_TM}"

class RespUsuarioTamizaje(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Usuario Respuesta")
    id_manychat = models.IntegerField()
    respuesta_TM = models.ForeignKey(OpcTamizaje, on_delete=models.CASCADE)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
        if self.respuesta_TM.id in [10, 11, 12, 13]:
            usuario = Usuario.objects.filter(id_manychat=self.id_manychat).first()
            if usuario:
                anio = self.obtener_anio_mamografia()
                if anio:
                    ultima_mamografia_anio.update_or_create(id_manychat=usuario, defaults = {"anio_ult_mamografia":anio})
                    
    def obtener_anio_mamografia(self):
    
        respuestas_mamografia = {
            10: 2024,  # ID 10 corresponde a Año 2024
            11: 2023,  # ID 11 corresponde a Año 2023
            12: 2022,  # ID 12 corresponde a Antes de 2022, para el cálculo se asume 2022. 
        }
        return respuestas_mamografia.get(self.respuesta_TM.id)
    
    def __str__(self):
        return f"{self.id_manychat} - {self.respuesta_TM}"

class MensajeContenido(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Texto")
    texto = models.CharField(max_length=200)
    fecha = models.DateField(verbose_name="Fecha")

    def __str__(self):
        return self.texto

class filtro_mensaje(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID filtro mensaje")
    opcresTM =models.ForeignKey(RespUsuarioTamizaje, on_delete= models.CASCADE)
    opcresUS = models.ForeignKey(Usuario, on_delete= models.CASCADE, to_field="id_manychat")
    mensaje_contenido_id = models.ForeignKey(MensajeContenido, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.opcresTM} - {self.opcresUS}"
    
class ultima_mamografia_anio(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de última mamografía")
    anio_ult_mamografia = models.IntegerField(default=0, verbose_name="Año de última mamografía")
    tiempo_transc_ult_mamografia = models.IntegerField(default=0, verbose_name="Tiempo transcurrido")
    fecha_pregunta = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    id_manychat = models.ForeignKey(Usuario, on_delete=models.CASCADE, to_field="id_manychat")

    def calculo_tiempo_transc_ult_mamografia(self):
        anio_actual = date.today().year
        return anio_actual - self.anio_ult_mamografia if self.anio_ult_mamografia else 0

    def save(self, *args, **kwargs):
        self.tiempo_transc_ult_mamografia = self.calculo_tiempo_transc_ult_mamografia()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id_manychat} - {self.anio_ult_mamografia}"

class region(models.Model):
    cod_region = models.CharField(primary_key=True, verbose_name= "Cod region", max_length=2)
    nombre_region = models.CharField(max_length=200)

    def __str__(self):
        return self.cod_region

class provincia(models.Model):
    cod_provincia = models.CharField(primary_key=True, verbose_name= "Cod provincia", max_length=4)
    nombre_provincia = models.CharField(max_length=200)
    cod_region = models.ForeignKey(region,on_delete = models.CASCADE)

    def __str__(self):
        return self.cod_provincia

class comuna(models.Model):
    cod_comuna = models.CharField(primary_key=True, verbose_name="Cod comuna", max_length=6)
    nombre_comuna = models.CharField (max_length=200)
    cod_provincia = models.ForeignKey (provincia, on_delete = models.CASCADE)

    def __str__(self):
        return self.nombre_comuna
    