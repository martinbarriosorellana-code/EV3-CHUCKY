from django.db import models
from gestorusers.models import Estudiante


# =============================================================
#                          CURSO
# =============================================================
class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    nivel = models.CharField(
        max_length=50,
        blank=True,     # ✔ El formulario puede enviarlo vacío
        null=True       # ✔ MySQL ahora permite NULL correctamente
    )

    def __str__(self):
        return self.nombre


# =============================================================
#                        ASIGNATURA
# =============================================================
class Asignatura(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name="asignaturas"  # ✔ Para acceder como curso.asignaturas.all()
    )

    def __str__(self):
        return f"{self.nombre} — {self.curso.nombre}"


# =============================================================
#                   INSCRIPCIÓN DE ESTUDIANTES
# =============================================================
class Inscripcion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('estudiante', 'curso')  # ✔ Evita duplicados

    def __str__(self):
        return f"{self.estudiante.user.first_name} inscrito en {self.curso.nombre}"
