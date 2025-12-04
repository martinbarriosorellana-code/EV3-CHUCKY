from django.contrib import admin
from .models import PerfilUsuario, Estudiante, Docente, Administrador

# Mostrar PerfilUsuario en el admin
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "rol", "fecha_creacion")
    list_filter = ("rol",)
    search_fields = ("user__username", "user__first_name", "user__last_name")


# Mostrar Estudiante en el admin
@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ("user", "rut", "nivel", "fecha_registro")
    search_fields = ("user__username", "rut")


# Mostrar Docente en el admin
@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ("user", "especialidad", "fecha_ingreso")
    search_fields = ("user__username", "especialidad")


# Mostrar Administrador en el admin
@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ("user", "cargo")
    search_fields = ("user__username", "cargo")
