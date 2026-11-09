import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

# estudiantes, materias, calificaciones y usuarios

from consultas.estudiantes import (
    listar_estudiantes,
    insertar_estudiante,
    listar_grupos as listar_grupos_estudiantes,
    listar_estudiantes_por_grupo
)

from consultas.materias import (
    listar_materias,
    listar_docentes,
    listar_grupos as listar_grupos_materias,
    insertar_materia,
    listar_materias_por_curso,
    listar_cursos,
    actualizar_docente_materia, 
    listar_cursos_por_docente
)

from consultas.calificaciones import (
    listar_calificaciones_por_curso,
    listar_calificaciones_por_curso_y_materia,
    guardar_calificaciones_planilla,
    listar_calificaciones_generales
)

from consultas.usuarios import (
    crear_usuario,
    buscar_usuario,
    verificar_contrasenia,
    listar_usuarios_docentes,
    suspender_usuario,
    reactivar_usuario,
    actualizar_usuario,
    buscar_docente_por_id
)


app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "admin1234"  # Cambiar en producción
)


# CONTROL DE ACCESO

def requiere_login(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):

        if "id_usuario" not in session:
            flash("Debe iniciar sesión para acceder.", "error")
            return redirect(url_for("login"))

        return funcion(*args, **kwargs)

    return envoltura


def requiere_rol(*roles_permitidos):
    def decorador(funcion):
        @wraps(funcion)
        def envoltura(*args, **kwargs):

            if "id_usuario" not in session:
                flash("Debe iniciar sesión para acceder.", "error")
                return redirect(url_for("login"))

            if session.get("rol") not in roles_permitidos:
                flash("No tiene permisos para acceder a esta sección.", "error")
                return redirect(url_for("inicio"))

            return funcion(*args, **kwargs)

        return envoltura

    return decorador


# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():

    if "id_usuario" in session:
        return redirect(url_for("inicio"))

    if request.method == "POST":

        nombre_usuario = request.form.get(
            "nombre_de_usuario", ""
        ).strip()

        contrasenia = request.form.get(
            "contrasenia", ""
        )

        usuario = buscar_usuario(nombre_usuario)

        if (
            usuario is not None
            and usuario[6] == 1
            and verificar_contrasenia(
                contrasenia,
                usuario[2]
            )
        ):
            session.clear()

            session["id_usuario"] = usuario[0]
            session["nombre_de_usuario"] = usuario[1]
            session["rol"] = usuario[3]

            flash("Inicio de sesión correcto.", "success")

            return redirect(url_for("inicio"))

        flash(
            "Nombre de usuario o contraseña incorrectos.",
            "error"
        )

    return render_template("login.html")


@app.route("/logout")
@requiere_login
def logout():

    session.clear()

    flash("La sesión se cerró correctamente.", "success")

    return redirect(url_for("login"))


# INICIO

@app.route("/")
def inicio():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") == "docente":
        return redirect(url_for("calificaciones"))

    return render_template("index.html")


# ESTUDIANTES

# Ruta para alta de estudiantes
@app.route("/estudiantes/alta", methods=["GET", "POST"])
@requiere_rol("administrador")
def alta_estudiante():

    grupos = listar_grupos_estudiantes()

    if request.method == "POST":

        try:
            nro = int(request.form["nro"])
            nombre_apellido = request.form["nombre_apellido"].strip()
            dni = int(request.form["dni"])
            id_gruponuevo = int(request.form["id_grupo"])

        except (ValueError, KeyError):
            return (
                "<h1>Error en los datos</h1>"
                "<p>Verifique los campos e intente nuevamente.</p>"
            ), 400

        # Verificar que el grupo seleccionado exista.
        ids_grupos = [grupo[0] for grupo in grupos]

        if id_gruponuevo not in ids_grupos:
            return (
                "<h1>Error</h1>"
                "<p>El grupo seleccionado no es válido.</p>"
            ), 400

        if not nombre_apellido:
            return (
                "<h1>Error</h1>"
                "<p>El nombre y apellido son obligatorios.</p>"
            ), 400

        resultado, mensaje = insertar_estudiante(
            nro,
            nombre_apellido,
            dni,
            id_gruponuevo
        )

        if resultado:
            return "<h1>Estudiante guardado correctamente</h1>"

        else:
            return (
                "<h1>Error al guardar estudiante</h1>"
                f"<p>{mensaje}</p>"
            ), 400

    return render_template(
        "estudiantes/alta_estudiante.html",
        grupos=grupos
    )


@app.route("/estudiantes/por-grupo")
@requiere_rol("administrador")
def mostrar_estudiantes_por_grupo():

    grupos = listar_grupos_estudiantes()

    id_grupo = request.args.get("id_grupo", type=int)

    estudiantes = []
    grupo_seleccionado = None

    if id_grupo is not None:

        for grupo in grupos:
            if grupo[0] == id_grupo:
                grupo_seleccionado = grupo
                break

        if grupo_seleccionado is not None:
            estudiantes = listar_estudiantes_por_grupo(id_grupo)

    return render_template(
        "estudiantes/por_grupo.html",
        grupos=grupos,
        estudiantes=estudiantes,
        id_grupo_seleccionado=id_grupo,
        grupo_seleccionado=grupo_seleccionado
    )


@app.route("/estudiantes")
@requiere_rol("administrador")
def estudiantes():
    return render_template("estudiantes/index.html")


@app.route("/estudiantes/listado")
@requiere_rol("administrador")
def mostrar_estudiantes():

    estudiantes = listar_estudiantes()

    return render_template(
        "estudiantes/mostrar_estudiantes.html",
        estudiantes=estudiantes
    )


# FIN ESTUDIANTES


# MATERIAS

@app.route("/materias")
@requiere_rol("administrador")
def materias():
    return render_template("materias/index.html")


# Ruta para alta de materias

@app.route("/materias/alta", methods=["GET", "POST"])
@requiere_rol("administrador")
def alta_materia():

    docentes = listar_docentes()
    grupos = listar_grupos_materias()

    if request.method == "POST":

        nombre_materia = request.form.get(
            "nombre_materia", ""
        ).strip()

        try:
            curso = int(request.form.get("curso", ""))
            id_grupo = int(request.form.get("id_grupo", ""))
            id_usuario = int(request.form.get("id_usuario", ""))

        except (ValueError, TypeError):
            flash("Debe completar correctamente todos los campos.", "error")
            return redirect(url_for("alta_materia"))

        # Verificar que el nombre de la materia no esté vacío.
        if not nombre_materia:
            flash("El nombre de la materia es obligatorio.", "error")
            return redirect(url_for("alta_materia"))

        # Verificar que el grupo pertenezca al curso seleccionado.
        grupo_valido = any(
            grupo[0] == id_grupo and grupo[1] == curso
            for grupo in grupos
        )

        if not grupo_valido:
            flash(
                "El grupo seleccionado no corresponde al curso indicado.",
                "error"
            )
            return redirect(url_for("alta_materia"))

        # Insertar la materia.
        resultado = insertar_materia(
            nombre_materia,
            id_grupo,
            id_usuario
        )

        if resultado:
            flash("Materia guardada correctamente.", "success")
            return redirect(url_for("materias"))

        flash("No se pudo guardar la materia.", "error")

    return render_template(
        "materias/alta_materia.html",
        docentes=docentes,
        grupos=grupos
    )


@app.route("/materias/listado")
@requiere_rol("administrador")
def mostrar_materias():

    materias = listar_materias()

    return render_template(
        "materias/mostrar_materias.html",
        materias=materias
    )


@app.route("/materias/editar/<int:id_materia>", methods=["GET", "POST"])
@requiere_rol("administrador")
def editar_materia(id_materia):

    conexion = None

    from basededatos.conexion import conectar

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id_materia, nombre_materia, curso, turno, id_usuario
            FROM materias
            WHERE id_materia = ?
        """, (id_materia,))

        materia = cursor.fetchone()

    finally:
        conexion.close()

    if materia is None:
        flash("La materia seleccionada no existe.", "error")
        return redirect(url_for("mostrar_materias"))

    docentes = listar_docentes()

    if request.method == "POST":

        try:
            id_usuario = int(request.form["id_usuario"])
        except (ValueError, KeyError):
            flash("Debe seleccionar un docente válido.", "error")
            return redirect(url_for("editar_materia", id_materia=id_materia))

        resultado = actualizar_docente_materia(
            id_materia,
            id_usuario
        )

        if resultado:
            flash("Docente responsable actualizado correctamente.", "success")
            return redirect(url_for("mostrar_materias"))

        flash("No se pudo actualizar el docente responsable.", "error")

    return render_template(
        "materias/editar_materia.html",
        materia=materia,
        docentes=docentes
    )


# FIN MATERIAS

# USUARIOS

@app.route("/usuarios")
@requiere_rol("administrador")
def usuarios():

    docentes = listar_usuarios_docentes()

    return render_template(
        "usuarios/listado.html",
        docentes=docentes
    )

@app.route("/usuarios/alta", methods=["GET", "POST"])
@requiere_rol("administrador")
def alta_usuario():

    if request.method == "POST":

        nombre_apellido = request.form.get(
            "nombre_apellido", ""
        ).strip()

        dni = request.form.get(
            "dni", ""
        ).strip()

        nombre_de_usuario = request.form.get(
            "nombre_de_usuario", ""
        ).strip()

        contrasenia = request.form.get(
            "contrasenia", ""
        )

        confirmar_contrasenia = request.form.get(
            "confirmar_contrasenia", ""
        )

        datos = {
            "nombre_apellido": nombre_apellido,
            "dni": dni,
            "nombre_de_usuario": nombre_de_usuario
        }

        if not all([
            nombre_apellido,
            dni,
            nombre_de_usuario,
            contrasenia,
            confirmar_contrasenia
        ]):
            flash("Todos los campos son obligatorios.", "error")

        elif contrasenia != confirmar_contrasenia:
            flash("Las contraseñas no coinciden.", "error")

        else:
            resultado, mensaje = crear_usuario(
                nombre_de_usuario,
                contrasenia,
                "docente",
                nombre_apellido,
                dni
            )

            if resultado:
                flash(mensaje, "success")
                return redirect(url_for("usuarios"))

            flash(mensaje, "error")

        return render_template(
            "usuarios/alta.html",
            datos=datos
        )

    return render_template(
        "usuarios/alta.html",
        datos={}
    )

@app.route("/usuarios/suspender/<int:id_usuario>", methods=["POST"])
@requiere_rol("administrador")
def suspender_docente(id_usuario):

    resultado = suspender_usuario(id_usuario)

    if resultado:
        flash("Docente suspendido correctamente.", "success")
    else:
        flash("No se pudo suspender el docente.", "error")

    return redirect(url_for("usuarios"))

@app.route("/usuarios/reactivar/<int:id_usuario>", methods=["POST"])
@requiere_rol("administrador")
def reactivar_docente(id_usuario):

    resultado = reactivar_usuario(id_usuario)

    if resultado:
        flash("Docente reactivado correctamente.", "success")
    else:
        flash("No se pudo reactivar el docente.", "error")

    return redirect(url_for("usuarios"))

@app.route("/usuarios/editar/<int:id_usuario>", methods=["GET", "POST"])
@requiere_rol("administrador")
def editar_docente(id_usuario):

    docente = buscar_docente_por_id(id_usuario)

    if docente is None:
        flash("No se encontró el docente.", "error")
        return redirect(url_for("usuarios"))

    if request.method == "POST":

        nombre_apellido = request.form.get(
            "nombre_apellido", ""
        ).strip()

        dni = request.form.get(
            "dni", ""
        ).strip()

        nombre_de_usuario = request.form.get(
            "nombre_de_usuario", ""
        ).strip()

        resultado, mensaje = actualizar_usuario(
            id_usuario,
            nombre_apellido,
            dni,
            nombre_de_usuario
        )

        if resultado:
            flash(mensaje, "success")
            return redirect(url_for("usuarios"))

        flash(mensaje, "error")

        docente = (
            id_usuario,
            nombre_apellido,
            dni,
            nombre_de_usuario
        )

    return render_template(
        "usuarios/editar.html",
        docente=docente
    )

# FIN USUARIOS


# CALIFICACIONES

@app.route("/calificaciones")
@requiere_rol("administrador", "docente")
def calificaciones():
    return render_template("calificaciones/index.html")


# Esta consulta general queda reservada al administrador,
# porque actualmente no filtra las materias por docente.
@app.route("/calificaciones/curso")
@requiere_rol("administrador")
def seleccionar_curso_calificaciones():
    return render_template("calificaciones/seleccionar_curso.html")


@app.route("/calificaciones/curso/<int:curso>")
@requiere_rol("administrador")
def mostrar_calificaciones_por_curso(curso):

    calificaciones = listar_calificaciones_por_curso(curso)

    return render_template(
        "calificaciones/por_curso.html",
        curso=curso,
        calificaciones=calificaciones
    )

@app.route("/calificaciones/listado-general")
@requiere_rol("administrador", "docente")
def listado_general_calificaciones():

    # Determinar si corresponde aplicar el filtro por docente.
    id_usuario = None

    if session.get("rol") == "docente":
        id_usuario = session.get("id_usuario")

    # Obtener las calificaciones según el usuario conectado.
    calificaciones = listar_calificaciones_generales(id_usuario)

    return render_template(
        "calificaciones/listado_general.html",
        calificaciones=calificaciones
    )

@app.route("/calificaciones/planilla", methods=["GET", "POST"])
@requiere_rol("administrador", "docente")
def planilla_calificaciones():

    # Determinar los cursos disponibles según el rol.
    if session.get("rol") == "docente":
        id_usuario = session.get("id_usuario")
        cursos = listar_cursos_por_docente(id_usuario)
    else:
        id_usuario = None
        cursos = listar_cursos()

    if request.method == "POST":

        curso = request.form.get("curso", type=int)
        id_materia = request.form.get("id_materia", type=int)

        # Comprobar que el curso sea válido.
        if curso not in cursos:
            flash("El curso seleccionado no es válido.", "error")
            return redirect(url_for("planilla_calificaciones"))

        # Comprobar que la materia pertenezca al curso
        # y que esté asignada al docente conectado.
        materias_del_curso = listar_materias_por_curso(
            curso,
            id_usuario
        )

        materia_valida = any(
            materia[0] == id_materia
            for materia in materias_del_curso
        )

        if not materia_valida:
            flash(
                "La materia no corresponde al curso seleccionado.",
                "error"
            )
            return redirect(
                url_for("planilla_calificaciones", curso=curso)
            )

        registros = []

        # Recibir los estudiantes enviados desde el formulario.
        for valor_id in request.form.getlist("id_estudiante"):

            try:
                id_estudiante = int(valor_id)

            except ValueError:
                flash(
                    "Se recibió un identificador de estudiante inválido.",
                    "error"
                )
                return redirect(
                    url_for(
                        "planilla_calificaciones",
                        curso=curso,
                        id_materia=id_materia
                    )
                )

            notas = {
                "nota_primer_trimestre":
                    request.form.get(
                        f"nota_primer_trimestre_{id_estudiante}", ""
                    ),

                "nota_segundo_trimestre":
                    request.form.get(
                        f"nota_segundo_trimestre_{id_estudiante}", ""
                    ),

                "nota_tercer_trimestre":
                    request.form.get(
                        f"nota_tercer_trimestre_{id_estudiante}", ""
                    ),

                "nota_examen_diciembre":
                    request.form.get(
                        f"nota_examen_diciembre_{id_estudiante}", ""
                    ),

                "nota_examen_marzo":
                    request.form.get(
                        f"nota_examen_marzo_{id_estudiante}", ""
                    ),
            }

            registros.append({
                "id_estudiante": id_estudiante,
                "notas": notas
            })

        try:
            guardar_calificaciones_planilla(
                id_materia,
                registros,
                id_usuario
            )

            flash(
                "Las calificaciones se guardaron correctamente.",
                "success"
            )

        except ValueError as error:
            flash(str(error), "error")

        return redirect(
            url_for(
                "planilla_calificaciones",
                curso=curso,
                id_materia=id_materia
            )
        )

    # Visualización de la planilla.
    curso = request.args.get("curso", type=int)
    id_materia = request.args.get("id_materia", type=int)

    materias = []
    calificaciones = []
    materia_seleccionada = None

    if curso in cursos:

        # Mostrar solamente las materias del docente conectado.
        materias = listar_materias_por_curso(
            curso,
            id_usuario
        )

        for materia in materias:
            if materia[0] == id_materia:
                materia_seleccionada = materia
                break

        if materia_seleccionada is not None:

            calificaciones = (
                listar_calificaciones_por_curso_y_materia(
                    curso,
                    id_materia
                )
            )

    return render_template(
        "calificaciones/planilla.html",
        cursos=cursos,
        curso_seleccionado=curso,
        materias=materias,
        id_materia_seleccionada=id_materia,
        materia_seleccionada=materia_seleccionada,
        calificaciones=calificaciones
    )


# FIN CALIFICACIONES


# MAIN

if __name__ == "__main__":
    app.run(debug=True)
