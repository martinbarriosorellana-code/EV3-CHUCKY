from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse

from gestorusers.models import Estudiante, Docente, Administrador, PerfilUsuario
from gestorcursos.models import Curso, Asignatura, Inscripcion


# =============================================================
#                    PÁGINA INICIAL (INDEX)
# =============================================================

def index_view(request):
    """
    Página pública de inicio de Chucky Escuela.
    Muestra la landing con acceso a login y registro.
    """
    return render(request, "usuarios/index.html")


# =============================================================
#                LOGIN — AUTENTICACIÓN
# =============================================================

def login_view(request):

    if request.method == "POST":
        correo = request.POST.get("correo").lower().strip()
        password = request.POST.get("password")

        user = authenticate(request, username=correo, password=password)

        if user is None:
            messages.error(request, "Credenciales incorrectas.")
            return redirect("login")

        login(request, user)

        perfil = PerfilUsuario.objects.get(user=user)

        if perfil.rol == "administrador":
            return redirect("panel_admin")
        elif perfil.rol == "docente":
            # Rol docente = usuario normal según rúbrica
            return redirect("panel_usuario")
        else:
            # estudiante
            return redirect("panel_estudiante")

    # Cuando llegas por GET (por ejemplo desde registro), precarga el correo
    correo_inicial = request.GET.get("correo", "")

    return render(request, "usuarios/login.html", {
        "correo_inicial": correo_inicial
    })


# =============================================================
#                LOGOUT
# =============================================================

def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("login")


# =============================================================
#                REGISTRO — FIX DEFINITIVO
# =============================================================

def registro_view(request):

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        correo = request.POST.get("correo").lower().strip()
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        tipo_usuario = request.POST.get("tipo_usuario")
        rut = request.POST.get("rut")

        # Validaciones
        if password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("registro")

        if User.objects.filter(username=correo).exists():
            messages.error(request, "Este correo ya está registrado.")
            return redirect("registro")

        if tipo_usuario == "estudiante" and not rut:
            messages.error(request, "El RUT es obligatorio para estudiantes.")
            return redirect("registro")

        # Crear usuario Django
        user = User.objects.create_user(
            username=correo,
            email=correo,
            password=password,
            first_name=nombre,
            last_name=apellido
        )

        # Crear Perfil de Rol
        PerfilUsuario.objects.create(
            user=user,
            rol=tipo_usuario
        )

        # Crear tabla asociada al rol
        if tipo_usuario == "estudiante":
            Estudiante.objects.create(
                user=user,
                rut=rut
            )

        elif tipo_usuario == "docente":
            Docente.objects.create(user=user)

        elif tipo_usuario == "administrador":
            Administrador.objects.create(user=user)

        messages.success(request, "Registro exitoso. Ya puedes iniciar sesión.")

        # Redirigir al login con el correo en la URL para prellenar el campo
        login_url = reverse("login")
        return redirect(f"{login_url}?correo={correo}")

    return render(request, "usuarios/registro.html")


# =============================================================
#              PANELES SEGÚN TIPO DE USUARIO
# =============================================================

@login_required
def panel_estudiante(request):
    """
    Panel exclusivo para rol 'estudiante'.
    Muestra los cursos inscritos + total de cursos.
    """

    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != "estudiante":
        messages.error(request, "No tiene permisos para acceder al panel de estudiante.")
        if perfil.rol == "administrador":
            return redirect("panel_admin")
        else:  # docente / usuario normal
            return redirect("panel_usuario")

    try:
        estudiante = Estudiante.objects.get(user=request.user)
        inscripciones = Inscripcion.objects.filter(estudiante=estudiante)
        total_cursos = inscripciones.count()
    except Estudiante.DoesNotExist:
        inscripciones = []
        total_cursos = 0

    return render(request, "usuarios/panel_estudiante.html", {
        "inscripciones": inscripciones,
        "total_cursos": total_cursos,
    })


@login_required
def panel_usuario(request):
    """
    Panel exclusivo para el rol 'docente',
    que en la rúbrica funciona como 'usuario normal'.
    """

    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != "docente":
        messages.error(request, "No tiene permisos para acceder al panel de usuario.")
        if perfil.rol == "administrador":
            return redirect("panel_admin")
        else:  # estudiante
            return redirect("panel_estudiante")

    # Aquí podrías cargar info propia del usuario normal (docente),
    # por ahora solo mostramos el panel base.
    return render(request, "usuarios/panel_usuario.html")


@login_required
def panel_admin(request):
    """
    Panel principal del administrador.
    Solo accesible para usuarios con rol 'administrador'.
    """
    perfil = PerfilUsuario.objects.get(user=request.user)

    if perfil.rol != "administrador":
        messages.error(request, "No tiene permisos para acceder al panel de administración.")
        if perfil.rol == "estudiante":
            return redirect("panel_estudiante")
        else:  # docente / usuario normal
            return redirect("panel_usuario")

    return render(request, "usuarios/dashboard/admin.html")


# =============================================================
#               ADMIN — LISTA DE ESTUDIANTES
# =============================================================

@login_required
def admin_listar_estudiantes(request):

    perfil = PerfilUsuario.objects.get(user=request.user)

    if perfil.rol != "administrador":
        messages.error(request, "No tiene permisos para acceder aquí.")
        if perfil.rol == "estudiante":
            return redirect("panel_estudiante")
        else:
            return redirect("panel_usuario")

    # Traemos estudiantes + usuario relacionado
    estudiantes = (
        Estudiante.objects
        .select_related("user")
        .all()
        .order_by("-id")
    )

    # Info académica: total de cursos inscritos por cada estudiante
    for est in estudiantes:
        est.total_cursos = Inscripcion.objects.filter(estudiante=est).count()

    return render(request, "usuarios/admin/estudiantes_listar.html", {
        "estudiantes": estudiantes
    })


# =============================================================
#     ADMIN — CRUD COMPLETO DE ESTUDIANTES (NUEVO)
# =============================================================

@login_required
def admin_crear_estudiante(request):
    """
    Crear un estudiante desde el panel administrador.
    Crea:
      - User
      - PerfilUsuario (rol='estudiante')
      - Estudiante
    """

    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != "administrador":
        messages.error(request, "No tiene permisos para acceder aquí.")
        if perfil.rol == "estudiante":
            return redirect("panel_estudiante")
        else:
            return redirect("panel_usuario")

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        correo = request.POST.get("correo", "").lower().strip()
        rut = request.POST.get("rut")
        password = request.POST.get("password")

        if not nombre or not apellido or not correo:
            messages.error(request, "Nombre, apellido y correo son obligatorios.")
            return redirect("admin_crear_estudiante")

        if User.objects.filter(username=correo).exists():
            messages.error(request, "Ya existe un usuario con ese correo.")
            return redirect("admin_crear_estudiante")

        # Si el admin no escribe password, usamos una por defecto simple (solo demo)
        if not password:
            password = "Chucky123*"

        user = User.objects.create_user(
            username=correo,
            email=correo,
            password=password,
            first_name=nombre,
            last_name=apellido
        )

        PerfilUsuario.objects.create(
            user=user,
            rol="estudiante"
        )

        Estudiante.objects.create(
            user=user,
            rut=rut
        )

        messages.success(request, "Estudiante creado correctamente.")
        return redirect("admin_listar_estudiantes")

    # GET: mostrar formulario vacío
    return render(request, "usuarios/admin/estudiantes_form.html", {
        "titulo": "Crear Estudiante",
        "modo": "crear",
    })


@login_required
def admin_editar_estudiante(request, estudiante_id):
    """
    Editar datos básicos de un estudiante:
    nombre, apellido, correo y RUT.
    """

    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != "administrador":
        messages.error(request, "No tiene permisos para acceder aquí.")
        if perfil.rol == "estudiante":
            return redirect("panel_estudiante")
        else:
            return redirect("panel_usuario")

    est = get_object_or_404(Estudiante, id=estudiante_id)
    user = est.user

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        correo = request.POST.get("correo", "").lower().strip()
        rut = request.POST.get("rut")

        if not nombre or not apellido or not correo:
            messages.error(request, "Nombre, apellido y correo son obligatorios.")
            return redirect("admin_editar_estudiante", estudiante_id=est.id)

        # Validar que no exista otro usuario con ese correo
        existe = User.objects.filter(username=correo).exclude(id=user.id).exists()
        if existe:
            messages.error(request, "Ya existe otro usuario con ese correo.")
            return redirect("admin_editar_estudiante", estudiante_id=est.id)

        # Actualizar datos del usuario
        user.first_name = nombre
        user.last_name = apellido
        user.email = correo
        user.username = correo   
        user.save()


        est.rut = rut
        est.save()

        messages.success(request, "Estudiante actualizado correctamente.")
        return redirect("admin_listar_estudiantes")

    # GET: mostrar formulario con datos actuales
    return render(request, "usuarios/admin/estudiantes_form.html", {
        "titulo": "Editar Estudiante",
        "modo": "editar",
        "estudiante": est,
    })


@login_required
def admin_eliminar_estudiante(request, estudiante_id):
    """
    Eliminar un estudiante.
    Se elimina también su usuario asociado.
    """

    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != "administrador":
        messages.error(request, "No tiene permisos para acceder aquí.")
        if perfil.rol == "estudiante":
            return redirect("panel_estudiante")
        else:
            return redirect("panel_usuario")

    est = get_object_or_404(Estudiante, id=estudiante_id)
    user = est.user

    # Aquí podrías hacer un "soft delete" si quisieras.
    # Por ahora, borramos el usuario, lo que arrastra al Estudiante
    user.delete()

    messages.success(request, "Estudiante eliminado correctamente.")
    return redirect("admin_listar_estudiantes")


# =============================================================
#               ADMIN — MÓDULO DE REPORTES
# =============================================================

@login_required
def admin_reportes(request):
    """
    Módulo de Reportes accesible solo para administradores.
    Carga la plantilla base de reportes.
    """

    perfil = PerfilUsuario.objects.get(user=request.user)

    if perfil.rol != "administrador":
        messages.error(request, "No tiene permisos para acceder aquí.")
        if perfil.rol == "estudiante":
            return redirect("panel_estudiante")
        else:
            return redirect("panel_usuario")

    return render(request, "usuarios/admin/reportes.html")


# =============================================================
#                     MIS CURSOS — VISTA COMPLETA
# =============================================================

@login_required
def mis_cursos(request):
    """
    Vista exclusiva para estudiantes.
    Muestra cursos disponibles + inscripciones del alumno.
    """

    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != "estudiante":
        messages.error(request, "Solo los estudiantes pueden acceder a 'Mis cursos'.")
        if perfil.rol == "administrador":
            return redirect("panel_admin")
        else:
            return redirect("panel_usuario")

    try:
        estudiante = Estudiante.objects.get(user=request.user)
        inscripciones = Inscripcion.objects.filter(estudiante=estudiante)
        total_cursos = inscripciones.count()
    except Estudiante.DoesNotExist:
        inscripciones = []
        total_cursos = 0

    cursos = Curso.objects.all()

    return render(request, "cursos/mis_cursos.html", {
        "cursos": cursos,
        "inscripciones": inscripciones,
        "total_cursos": total_cursos,
    })
