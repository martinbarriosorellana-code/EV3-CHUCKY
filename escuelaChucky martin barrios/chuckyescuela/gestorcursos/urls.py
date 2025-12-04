from django.urls import path
from . import views

urlpatterns = [

    # =============================================================
    #                         CURSOS (CRUD)
    # =============================================================
    path("", views.listar_cursos, name="listar_cursos"),
    path("agregar/", views.agregar_curso, name="agregar_curso"),
    path("editar/<int:id>/", views.editar_curso, name="editar_curso"),
    path("eliminar/<int:id>/", views.eliminar_curso, name="eliminar_curso"),

    # =============================================================
    #               ⚡ ADMIN — GESTIONAR CURSOS (MEJORA NUEVA)
    # =============================================================
    path(
        "admin/gestion/",
        views.admin_listar_cursos,
        name="admin_listar_cursos"
    ),

    # =============================================================
    #          ⚡ ADMIN — VER INSCRIPCIONES (NUEVO MÓDULO)
    # =============================================================
    path(
        "admin/inscripciones/",
        views.admin_inscripciones,
        name="admin_inscripciones"
    ),

    # =============================================================
    #                         ASIGNATURAS (Placeholder)
    # =============================================================
    path("asignaturas/", views.listar_asignaturas, name="listar_asignaturas"),

    # =============================================================
    #                 MIS CURSOS (VISTA EV3 - ESTUDIANTE)
    # =============================================================
    path("mis-cursos/", views.mis_cursos, name="mis_cursos"),

    # =============================================================
    #              ⭐ NUEVO — INSCRIBIRSE EN CURSO
    # =============================================================
    path(
        "inscribir/<int:curso_id>/",
        views.inscribir_en_curso,
        name="inscribir_en_curso"
    ),

    # =============================================================
    #              ⭐⭐ NUEVO — VER CURSO DETALLADO
    # =============================================================
    path(
        "ver/<int:curso_id>/",
        views.ver_curso,
        name="ver_curso"
    ),
]
