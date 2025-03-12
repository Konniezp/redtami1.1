from django import forms
from .models import *


class UsuarioForm(forms.ModelForm):
    Comuna_Usuario = forms.ModelChoiceField(queryset=comuna.objects.all(), empty_label="Seleccione una opción", widget=forms.Select(attrs={'class': 'form-control'}))
    AnioNacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'dark-input'}))
    Rut = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Whatsapp = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fecha_nacimiento = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = ['Rut', 'Whatsapp', 'fecha_nacimiento', 'Comuna_Usuario']

    def clean_Comuna_Usuario(self):
        comuna = self.cleaned_data['comuna']
        return comuna

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['pregunta']
        
class MensajeContenidoForm(forms.ModelForm):
    class Meta:
        model = MensajeContenido
        fields = ['texto','fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'dark-input'})
        }