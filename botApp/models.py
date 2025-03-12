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
    id = models.AutoField(primary_key=True, verbose_name="ID Usuario")
    id_manychat = models.CharField(max_length=200)
    Rut = models.CharField(max_length=255)  # Se almacena cifrado
    RutHash = models.CharField(max_length=255, blank=True, null=True)
    AnioNacimiento = models.DateField(verbose_name="Fecha de Nacimiento", null=True, blank=True)
    Whatsapp = models.CharField(max_length=255)  # Se almacena cifrado
    Email = models.CharField(max_length=255, blank=True) # Se almacena cifrado
    Comuna_Usuario = models.ForeignKey('comuna', on_delete=models.CASCADE)
    Referencia = models.CharField(max_length=200)
    Fecha_Ingreso = models.DateTimeField(default=timezone.now)
    edad = models.IntegerField(default=0)
    fecha_nacimiento = models.CharField(max_length=30, null=True, blank=True)

    # Generar Hash
    def generar_hash(self, valor):
        return hashlib.sha256(valor.encode()).hexdigest()
    
    def get_rut_descifrado(self):
        return decrypt_data(self.Rut) if self.Rut else None

    def get_whatsapp_descifrado(self):
        return decrypt_data(self.Whatsapp) if self.Whatsapp else None
    
    def get_email_descifrado (self):
        return decrypt_data(self.Email) if self.Email else None

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

        # Cifrar Rut, Whatsapp e Email si no están cifrados aún
        if self.Rut and not self.Rut.startswith("gAAAA"):  
            self.Rut = encrypt_data(self.Rut).decode()
            self.RutHash = self.generar_hash(decrypt_data(self.Rut))

        if self.Whatsapp and not self.Whatsapp.startswith("gAAAA"):
            self.Whatsapp = encrypt_data(self.Whatsapp).decode()

        if self.Email and not self.Email.startswith("gAAAA"):
            self.Email = encrypt_data(self.Email).decode()

        # Calcular edad antes de guardar
        self.edad = self.calculo_edad()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_rut_descifrado()} - {self.id}"
    
class Codigos_preg (models.Model):
    id = models.AutoField(primary_key=True, verbose_name= "ID códigos preguntas")
    codigo_preguntas = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.codigo_preguntas
    
class Pregunta(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Pregunta")
    pregunta = models.CharField(max_length=200)
    codigo_preguntas = models.ForeignKey(Codigos_preg, on_delete = models.CASCADE, null=True)

    def __str__(self):
        return self.pregunta

class PreguntaOpcionRespuesta(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Opcion Respuesta")
    id_pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    OPC_Respuesta = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.id_pregunta} - {self.OPC_Respuesta}"

class UsuarioRespuesta(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Usuario Respuesta")
    Rut = models.CharField(max_length=255)
    RutHash = models.CharField(max_length=255, blank=True, null=True)
    id_opc_respuesta = models.ForeignKey(PreguntaOpcionRespuesta, on_delete=models.CASCADE)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.Rut and not self.Rut.startswith("gAAAA"):  
            self.Rut = encrypt_data(self.Rut).decode()
            self.RutHash = Usuario().generar_hash(decrypt_data(self.Rut))
        super().save(*args, **kwargs)
    
        if self.id_opc_respuesta.id in [10, 11, 12, 13]:
                # Obtener el usuario asociado a la respuesta
                usuario = Usuario.objects.get(RutHash=self.RutHash)

                # Crear o actualizar la instancia de ultima_mamografia_anio
                ultima_mamografia_anio.objects.update_or_create(
                    id_usuario=usuario,
                    defaults={
                        "Rut": self.Rut,
                        "RutHash": self.RutHash,
                        "anio_ult_mamografia": self.obtener_anio_mamografia(),
                    }
                )

    def obtener_anio_mamografia(self):
    
        respuestas_mamografia = {
            10: 2024,  # ID 10 corresponde a Año 2024
            11: 2023,  # ID 11 corresponde a Año 2023
            12: 2022,  # ID 12 corresponde a Antes de 2022, para el cálculo se asume 2022. 
        }
        return respuestas_mamografia.get(self.id_opc_respuesta.id, 0)

    def get_rut_descifrado(self):
        return decrypt_data(self.Rut) if self.Rut else None
    
    def __str__(self):
        return f"{self.get_rut_descifrado()} - {self.id_opc_respuesta}"

class UsuarioTextoPregunta(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Texto Pregunta")
    Rut = models.CharField(max_length=255)
    RutHash = models.CharField(max_length=255, blank=True, null=True)
    texto_pregunta = models.CharField(max_length=200)
    fecha_pregunta = models.DateTimeField(auto_now_add=True)
    id_usuario=models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.Rut and not self.Rut.startswith("gAAAA"):  
            self.Rut = encrypt_data(self.Rut).decode()
            self.RutHash = Usuario().generar_hash(decrypt_data(self.Rut))
        super().save(*args, **kwargs)

    def get_rut_descifrado(self):
        return decrypt_data(self.Rut) if self.Rut else None
    
    def __str__(self):
        return f"{self.get_rut_descifrado()} - {self.texto_pregunta}"

class MensajeContenido(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Texto")
    texto = models.CharField(max_length=200)
    fecha = models.DateField(verbose_name="Fecha")

    def __str__(self):
        return self.texto

class filtro_mensaje(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID filtro mensaje")
    opcrespFRNM = models.ForeignKey('RespUsuarioFactorRiesgoNoMod', on_delete=models.CASCADE)
    opcrespFRM = models.ForeignKey('RespUsuarioFactorRiesgoMod', on_delete= models.CASCADE)
    opcrespDS = models.ForeignKey('RespDeterSalud', on_delete= models.CASCADE)
    opcresTM =models.ForeignKey(UsuarioRespuesta, on_delete= models.CASCADE)
    opcresUS = models.ForeignKey(Usuario, on_delete= models.CASCADE)
    mensaje_contenido_id = models.ForeignKey(MensajeContenido, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.opcrespFRNM} - {self.opcrespFRM} - {self.opcrespDS} - {self.opcresTM} - {self.opcresUS}"
    
class ultima_mamografia_anio(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de última mamografía")
    Rut = models.CharField(max_length=255)
    RutHash = models.CharField(max_length=255, blank=True, null=True)
    anio_ult_mamografia = models.IntegerField(default=0, verbose_name="Año de última mamografía")
    tiempo_transc_ult_mamografia = models.IntegerField(default=0, verbose_name="Tiempo transcurrido")
    fecha_pregunta = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def calculo_tiempo_transc_ult_mamografia(self):
        anio_actual = date.today().year
        return anio_actual - self.anio_ult_mamografia if self.anio_ult_mamografia else 0

    def save(self, *args, **kwargs):
        # Cifrar el RUT si no está cifrado
        if self.Rut and not self.Rut.startswith("gAAAA"):  
            self.Rut = encrypt_data(self.Rut).decode()
            self.RutHash = Usuario().generar_hash(decrypt_data(self.Rut))

        self.tiempo_transc_ult_mamografia = self.calculo_tiempo_transc_ult_mamografia()

        # Guardar la instancia
        super().save(*args, **kwargs)

    def get_rut_descifrado(self):
        return decrypt_data(self.Rut) if self.Rut else None

    def __str__(self):
        return f"{self.get_rut_descifrado()} - {self.anio_ult_mamografia}"

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
    
class PregFactorRiesgoMod(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Factor de Riesgo Mod")
    pregunta_FRM = models.CharField(max_length=200)
    codigo_preguntas = models.ForeignKey(Codigos_preg, on_delete = models.CASCADE, null=True)

    def __str__(self):
        return self.pregunta_FRM

class OpcFactorRiesgoMod(models.Model):
    id = models.AutoField(primary_key=True, verbose_name= "ID Opc Riesgo Mod")
    opc_respuesta_FRM = models.CharField(max_length=200)
    id_pregunta_FRM = models.ForeignKey(PregFactorRiesgoMod, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_pregunta_FRM} - {self.opc_respuesta_FRM}"

class RespUsuarioFactorRiesgoMod (models.Model):
    id = models.AutoField(primary_key=True, verbose_name= "ID Resp Riesgo Mod")
    Rut = models.CharField(max_length=255)
    RutHash = models.CharField(max_length=255, blank=True, null=True)
    respuesta_FRM = models.ForeignKey(OpcFactorRiesgoMod, on_delete=models.CASCADE)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.Rut and not self.Rut.startswith("gAAAA"):  
            self.Rut = encrypt_data(self.Rut).decode()
            self.RutHash = Usuario().generar_hash(decrypt_data(self.Rut))
        super().save(*args, **kwargs)

    def get_rut_descifrado(self):
        return decrypt_data(self.Rut) if self.Rut else None

    def __str__(self):
        return f"{self.get_rut_descifrado()} - {self.respuesta_FRM}"

class PregFactorRiesgoNoMod(models.Model):
    id = models.AutoField(primary_key= True, verbose_name= "ID Factor de Riesgo No Mod")
    pregunta_FRNM = models.CharField(max_length=200)
    codigo_preguntas = models.ForeignKey(Codigos_preg, on_delete = models.CASCADE, null=True)

    def __str__(self):
        return self.pregunta_FRNM

class OpcFactorRiesgoNoMod(models.Model):
    id = models.AutoField(primary_key=True, verbose_name= "ID Opc Riesgo No Mod")
    opc_respuesta_FRNM = models.CharField(max_length=200)
    id_pregunta_FRNM = models.ForeignKey(PregFactorRiesgoNoMod, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_pregunta_FRNM} - {self.opc_respuesta_FRNM}"

class RespUsuarioFactorRiesgoNoMod (models.Model):
    id = models.AutoField(primary_key=True, verbose_name= "ID Resp Riesgo Mod")
    Rut = models.CharField(max_length=255)
    RutHash = models.CharField(max_length=255, blank=True, null=True)
    respuesta_FRNM = models.ForeignKey(OpcFactorRiesgoNoMod, on_delete=models.CASCADE)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.Rut and not self.Rut.startswith("gAAAA"):  
            self.Rut = encrypt_data(self.Rut).decode()
            self.RutHash = Usuario().generar_hash(decrypt_data(self.Rut))
        super().save(*args, **kwargs)
    
    def get_rut_descifrado(self):
        return decrypt_data(self.Rut) if self.Rut else None
    
    def __str__(self):
        return f"{self.get_rut_descifrado()} - {self.respuesta_FRNM}"
    
class PregDeterSalud(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Determinantes sociales salud")
    pregunta_DS = models.CharField(max_length=200)
    codigo_preguntas = models.ForeignKey(Codigos_preg, on_delete = models.CASCADE,null=True)

    def __str__(self):
        return self.pregunta_DS
    
class OpcDeterSalud(models.Model):
    id = models.AutoField(primary_key=True, verbose_name= "ID Opc determinantes salud")
    opc_respuesta_DS = models.CharField(max_length=200)
    id_pregunta_DS = models.ForeignKey(PregDeterSalud, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_pregunta_DS} - {self.opc_respuesta_DS}"
    
class RespDeterSalud (models.Model):
    id = models.AutoField(primary_key=True, verbose_name= "ID Resp determinante salud")
    Rut = models.CharField(max_length=255)
    RutHash = models.CharField(max_length=255, blank=True, null=True)
    respuesta_DS = models.ForeignKey(OpcDeterSalud, on_delete=models.CASCADE)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.Rut and not self.Rut.startswith("gAAAA"):  
            self.Rut = encrypt_data(self.Rut).decode()
            self.RutHash = Usuario().generar_hash(decrypt_data(self.Rut))
        super().save(*args, **kwargs)

    def get_rut_descifrado(self):
        return decrypt_data(self.Rut) if self.Rut else None
    
    def __str__(self):
        return f"{self.get_rut_descifrado()} - {self.respuesta_DS}"
    
class RespTextoFRM(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID índice antropométrico")
    Rut = models.CharField(max_length=255)
    RutHash = models.CharField(max_length=255, blank=True, null=True)
    peso_FRM5 = models.CharField(max_length= 3)  # Peso en kg
    altura_FRM4 = models.CharField(max_length= 4)  # Altura en cm
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    id_usuario=models.ForeignKey(Usuario,on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_rut_descifrado()} - Peso: {self.peso_FRM5} kg - Altura: {self.altura_FRM4} cm"

    def save(self, *args, **kwargs):
        if self.Rut and not self.Rut.startswith("gAAAA"):  
            self.Rut = encrypt_data(self.Rut).decode() 
            self.RutHash = Usuario().generar_hash(decrypt_data(self.Rut))
        super().save(*args, **kwargs)

        # Procesa los datos brutos
        CalculoFRM.procesar_datos_brutos(self)

    def get_rut_descifrado(self):
        return decrypt_data(self.Rut) if self.Rut else None

class CalculoFRM(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID Cálculo FRM")
    Rut = models.CharField(max_length=255)
    RutHash = models.CharField(max_length=255, blank=True, null=True)
    altura_mod = models.FloatField(default=0)
    peso_mod = models.FloatField(default=0)
    imc = models.FloatField(default=0.0) 
    datos_originales = models.OneToOneField(RespTextoFRM, on_delete=models.CASCADE)

    def calculo_imc(self):
        if self.altura_mod > 0 and self.peso_mod > 0:  
            altura_metros = self.altura_mod / 100  # Convierte de cm a metros
            return round(self.peso_mod / (altura_metros ** 2), 2)  # Redondear a 2 decimales
        return 0.0 

    def save(self, *args, **kwargs):
        if self.Rut and not self.Rut.startswith("gAAAA"):  
            self.Rut = encrypt_data(self.Rut).decode() 
            self.RutHash = Usuario().generar_hash(decrypt_data(self.Rut))
        self.imc = self.calculo_imc() 
        super().save(*args, **kwargs)
    
    @staticmethod
    def limpiar_numero(valor, es_altura=False):
        if not valor:
            return 0.0

        # Diccionario para convertir palabras a números, no ha sido probado con letras cuando estaba implementado. 
        palabras_a_numeros = {
            'cero': 0, 'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4,
            'cinco': 5, 'seis': 6, 'siete': 7, 'ocho': 8, 'nueve': 9,
            'diez': 10, 'once': 11, 'doce': 12, 'trece': 13, 'catorce': 14,
            'quince': 15, 'dieciséis': 16, 'diecisiete': 17, 'dieciocho': 18,
            'diecinueve': 19, 'veinte': 20, 'treinta': 30, 'cuarenta': 40,
            'cincuenta': 50, 'sesenta': 60, 'setenta': 70, 'ochenta': 80,
            'noventa': 90, 'cien': 100
        }

        valor_lower = str(valor).strip().lower()
        if valor_lower in palabras_a_numeros:
            return palabras_a_numeros[valor_lower]

        # Limpieza de caracteres no numéricos
        valor = valor.strip().replace(',', '.')  # Espacios y comas por puntos
        valor = re.sub(r'[^0-9.]', '', valor)  # Quitar letras y símbolos

        partes = valor.split('.')
        if len(partes) > 2:
            valor = partes[0] + '.' + partes[1]  # Mantener solo el primer punto


        try:
            valor_numerico = float(valor)
            if es_altura and valor_numerico > 250:  
                valor_numerico /= 10  # Corrige alturas mal escritas
            return valor_numerico if valor_numerico > 0 else 0.0
        except ValueError:
            return 0.0

    @classmethod
    def procesar_datos_brutos(cls, instance):
        peso_formateado = cls.limpiar_numero(instance.peso_FRM5)
        altura_formateada = cls.limpiar_numero(instance.altura_FRM4, es_altura=True)
        
        formateado, created = cls.objects.get_or_create(
            datos_originales=instance,
            defaults={
                "Rut": instance.Rut,
                "RutHash": instance.RutHash,
                "peso_mod": peso_formateado,
                "altura_mod": altura_formateada,
            }
        )

        if not created:
            formateado.peso_mod= peso_formateado
            formateado.altura_mod= altura_formateada
            formateado.save()
    