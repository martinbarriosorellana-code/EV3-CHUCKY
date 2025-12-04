from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Curso, Asignatura, Inscripcion
from gestorusers.models import Estudiante, PerfilUsuario  # Necesario para roles


# =============================================================
#                     CURSOS — CRUD GENERAL
# =============================================================

@login_required
def listar_cursos(request):
    """
    Listado general de cursos.
    Accesible para cualquier usuario logueado (estudiante, usuario normal, admin).
    """
    cursos = Curso.objects.all()
    return render(request, "cursos/cursos_listar.html", {
        "cursos": cursos
    })


@login_required
def agregar_curso(request):
    """
    Agregar un curso nuevo.
    (Normalmente usado desde contexto de administración, pero protegido
    solo por login aquí. El control de quién ve el botón lo manejas en templates.)
    """

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        nivel = request.POST.get("nivel")

        if not nombre or nombre.strip() == "":
            messages.error(request, "El nombre del curso es obligatorio.")
            return redirect("agregar_curso")

        Curso.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            nivel=nivel if nivel != "" else None
        )

        messages.success(request, "Curso creado correctamente.")
        return redirect("admin_listar_cursos")

    return render(request, "cursos/cursos_agregar.html")


@login_required
def editar_curso(request, id):
    """
    Editar un curso existente.
    """

    curso = get_object_or_404(Curso, id=id)

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        nivel = request.POST.get("nivel")

        curso.nombre = nombre
        curso.descripcion = descripcion
        curso.nivel = nivel if nivel != "" else None
        curso.save()

        messages.success(request, "Curso modificado correctamente.")
        return redirect("admin_listar_cursos")

    return render(request, "cursos/cursos_editar.html", {
        "curso": curso
    })


@login_required
def eliminar_curso(request, id):
    """
    Eliminar un curso.
    """
    curso = get_object_or_404(Curso, id=id)
    curso.delete()
    messages.success(request, "Curso eliminado correctamente.")
    return redirect("admin_listar_cursos")


# =============================================================
#                 PANEL ADMIN — LISTAR CURSOS
# =============================================================

@login_required
def admin_listar_cursos(request):
    """
    Listado de cursos para el panel del ADMINISTRADOR.
    Solo accesible para rol 'administrador'.
    """

    perfil = PerfilUsuario.objects.get(user=request.user)

    if perfil.rol != "administrador":
        messages.error(request, "No tiene permisos para acceder a esta sección.")

        # 🔒 Redirección según rol (igual que en gestorusers.views)
        if perfil.rol == "estudiante":
            return redirect("panel_estudiante")
        else:  # docente / usuario normal
            return redirect("panel_usuario")

    cursos = Curso.objects.all().order_by("-id")

    # 👉 IMPORTANTE:
    # Este template es el del MÓDULO ADMIN que dijiste que está bajo
    # gestorusers/templates/admin/cursos_listar.html  →  "admin/cursos_listar.html"
    return render(request, "admin/cursos_listar.html", {
        "cursos": cursos
    })


# =============================================================
#                     ASIGNATURAS (EV3 Placeholder)
# =============================================================

@login_required
def listar_asignaturas(request):
    asignaturas = Asignatura.objects.all()

    return render(request, "cursos/asignaturas_listar.html", {
        "asignaturas": asignaturas
    })


# =============================================================
#                INSCRIBIR ESTUDIANTE EN CURSO ⭐
# =============================================================

@login_required
def inscribir_en_curso(request, curso_id):
    """
    Solo estudiantes se pueden inscribir en cursos.
    """

    try:
        estudiante = Estudiante.objects.get(user=request.user)
    except Estudiante.DoesNotExist:
        messages.error(request, "Solo los estudiantes pueden inscribirse en cursos.")
        return redirect("mis_cursos")

    curso = get_object_or_404(Curso, id=curso_id)

    # Evitar inscripción duplicada
    existe = Inscripcion.objects.filter(estudiante=estudiante, curso=curso).exists()
    if existe:
        messages.warning(request, "Ya estás inscrito en este curso.")
        return redirect("mis_cursos")

    Inscripcion.objects.create(
        estudiante=estudiante,
        curso=curso
    )

    messages.success(request, f"Te has inscrito correctamente en {curso.nombre}.")
    return redirect("mis_cursos")


# =============================================================
#                 NUEVO: VER CURSO DETALLADO
# =============================================================

@login_required
def ver_curso(request, curso_id):
    """
    Ver detalle de un curso:
    - Información del curso
    - Asignaturas relacionadas
    - Si el estudiante está inscrito o no
    """

    curso = get_object_or_404(Curso, id=curso_id)

    # Cargar asignaturas relacionadas
    asignaturas = Asignatura.objects.filter(curso=curso)

    # Verificar si el usuario es estudiante
    try:
        estudiante = Estudiante.objects.get(user=request.user)
    except Estudiante.DoesNotExist:
        estudiante = None

    # Verificar si está inscrito
    inscrito = False
    if estudiante:
        inscrito = Inscripcion.objects.filter(
            estudiante=estudiante, curso=curso
        ).exists()

    return render(request, "cursos/ver_curso.html", {
        "curso": curso,
        "asignaturas": asignaturas,
        "inscrito": inscrito
    })


# =============================================================
#                  MIS CURSOS (Vista Estudiante)
# =============================================================

@login_required
def mis_cursos(request):
    """
    Vista de cursos propia del estudiante:
    muestra en qué cursos está inscrito.
    """

    try:
        estudiante = Estudiante.objects.get(user=request.user)
    except Estudiante.DoesNotExist:
        estudiante = None

    if estudiante:
        inscripciones = Inscripcion.objects.filter(estudiante=estudiante)
    else:
        inscripciones = []

    cursos = Curso.objects.all()

    return render(request, "cursos/mis_cursos.html", {
        "cursos": cursos,
        "inscripciones": inscripciones,
    })


# =============================================================
#          ADMIN — VISTA GLOBAL DE INSCRIPCIONES ⭐ NUEVO
# =============================================================

@login_required
def admin_inscripciones(request):
    """
    Listado global de inscripciones (Estudiante ↔ Curso)
    Solo accesible para administradores.
    """

    perfil = PerfilUsuario.objects.get(user=request.user)

    if perfil.rol != "administrador":
        messages.error(request, "No tiene permisos para acceder a esta sección.")

        # 🔒 Igual que arriba: redirigir según rol
        if perfil.rol == "estudiante":
            return redirect("panel_estudiante")
        else:
            return redirect("panel_usuario")

    # Cargamos todas las inscripciones con sus relaciones
    inscripciones = (
        Inscripcion.objects
        .select_related("estudiante__user", "curso")
        .all()
        .order_by("-id")
    )

    return render(request, "cursos/admin/inscripciones_listar.html", {
        "inscripciones": inscripciones
    })
