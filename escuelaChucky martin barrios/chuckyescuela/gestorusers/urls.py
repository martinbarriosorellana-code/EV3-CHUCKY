from django.urls import path
from . import views

urlpatterns = [

    # =========================================
    #          PÁGINA INICIAL + AUTENTICACIÓN
    # =========================================
    path("", views.index_view, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # =========================================
    #               REGISTRO
    # =========================================
    path("registro/", views.registro_view, name="registro"),

    # =========================================
    #      PANEL SEGÚN TIPO DE USUARIO
    # =========================================
    path("panel/estudiante/", views.panel_estudiante, name="panel_estudiante"),
    path("panel/usuario/", views.panel_usuario, name="panel_usuario"),
    path("panel/admin/", views.panel_admin, name="panel_admin"),

    # =========================================
    #      MÓDULO ADMIN – GESTIÓN DE USUARIOS
    # =========================================
    path(
        "admin/estudiantes/",
        views.admin_listar_estudiantes,
        name="admin_listar_estudiantes"
    ),

    #  NUEVO: Crear estudiante (ADMIN)
    path(
        "admin/estudiantes/nuevo/",
        views.admin_crear_estudiante,
        name="admin_crear_estudiante"
    ),

    #  Editar estudiante (ADMIN)
    path(
        "admin/estudiantes/<int:estudiante_id>/editar/",
        views.admin_editar_estudiante,
        name="admin_editar_estudiante"
    ),

    #  Eliminar estudiante (ADMIN)
    path(
        "admin/estudiantes/<int:estudiante_id>/eliminar/",
        views.admin_eliminar_estudiante,
        name="admin_eliminar_estudiante"
    ),

    # =========================================
    #     ⚡ MÓDULO ADMIN – REPORTES
    # =========================================
    path(
        "admin/reportes/",
        views.admin_reportes,
        name="admin_reportes"
    ),
]
