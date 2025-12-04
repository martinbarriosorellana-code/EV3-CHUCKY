from django.db import models
from django.contrib.auth.models import User


# =====================================================
#   PERFIL GENERAL DE USUARIO (ROLES)
# =====================================================
class PerfilUsuario(models.Model):
    ROLES = (
        ("estudiante", "Estudiante"),
        # 👉 Internamente sigue siendo 'docente',
        #    pero en la app se muestra como "Usuario normal"
        ("docente", "Usuario normal"),
        ("administrador", "Administrador"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES, default="estudiante")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Mostramos el rol con su etiqueta legible (Estudiante / Usuario normal / Administrador)
        return f"{self.user.username} — {self.get_rol_display()}"


# =====================================================
#   ESTUDIANTE (Datos adicionales)
# =====================================================
class Estudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=20, unique=True)
    # Nivel académico usado en Gestión de Estudiantes (tabla académica del admin)
    nivel = models.CharField(max_length=50, blank=True, null=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Estudiante: {self.user.first_name} {self.user.last_name}"


# =====================================================
#   DOCENTE → USUARIO NORMAL (según rúbrica)
# =====================================================
class Docente(models.Model):
    """
    En la rúbrica este rol se considera 'usuario normal'.
    Se mantiene el nombre 'Docente' solo a nivel interno/código,
    pero en la interfaz y reportes se presenta como 'Usuario normal'.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    fecha_ingreso = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Usuario normal: {self.user.first_name} {self.user.last_name}"


# =====================================================
#   ADMINISTRADOR (Datos adicionales)
# =====================================================
class Administrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100, default="Administrador General")

    def __str__(self):
        return f"Administrador: {self.user.first_name} {self.user.last_name}"
