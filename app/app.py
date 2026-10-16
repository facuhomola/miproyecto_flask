from flask import Flask, render_template, request, redirect, url_for, flash
from consultas.estudiantes import listar_estudiantes, insertar_estudiante, listar_grupos, listar_estudiantes_por_grupo
from consultas.materias import listar_materias, insertar_materia, listar_cursos, listar_materias_por_curso
from consultas.calificaciones import listar_calificaciones_por_curso, listar_calificaciones_por_curso_y_materia, guardar_calificaciones_planilla

app = Flask(__name__)
app.secret_key = "1234567890"  # Clave secreta para sesiones y flash messages   

@app.route("/")
def inicio():
    return render_template("index.html")

# ESTUDIANTES

# Ruta para alta de estudiantes
@app.route("/estudiantes/alta", methods=["GET", "POST"])
def alta_estudiante():

    grupos = listar_grupos()

    if request.method == "POST":

        try:
            nro = int(request.form["nro"])
            nombre_apellido = request.form["nombre_apellido"].strip()
            dni = int(request.form["dni"])
            id_grupo = int(request.form["id_grupo"])

        except (ValueError, KeyError):
            return (
                "<h1>Error en los datos</h1>"
                "<p>Verifique los campos e intente nuevamente.</p>"
            ), 400

        # Verificar que el grupo seleccionado exista.
        ids_grupos = [grupo[0] for grupo in grupos]

        if id_grupo not in ids_grupos:
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
            id_grupo
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
def mostrar_estudiantes_por_grupo():

    grupos = listar_grupos()

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
def estudiantes():
    return render_template("estudiantes/index.html")


@app.route("/estudiantes/listado")
def mostrar_estudiantes():

    estudiantes = listar_estudiantes()

    return render_template(
        "estudiantes/mostrar_estudiantes.html",
        estudiantes=estudiantes
    )

# FIN ESTUDIANTES

# MATERIAS

@app.route("/materias")
def materias():
    return render_template("materias/index.html")


# Ruta para alta de materias
@app.route("/materias/alta" , methods=["GET", "POST"])
def alta_materia():
    if request.method == "POST":

        nombre_materia = request.form["nombre_materia"]
        curso = int(request.form["curso"])
        docente = request.form["docente"]
        turno = request.form["turno"]

        resultado = insertar_materia(nombre_materia, curso, docente, turno)

        if resultado:
            return "<h1>Materia guardada correctamente</h1>"

        else:
            return "<h1>Error al guardar materia</h1>"
    return render_template("materias/alta_materia.html")


@app.route("/materias/listado")
def mostrar_materias():

    materias = listar_materias()

    return render_template(
        "materias/mostrar_materias.html",
        materias=materias
    )

# FIN MATERIAS

# CALIFICACIONES

@app.route("/calificaciones")
def calificaciones():
    return render_template("calificaciones/index.html")

@app.route("/calificaciones/curso")
def seleccionar_curso_calificaciones():
    return render_template("calificaciones/seleccionar_curso.html")

@app.route("/calificaciones/curso/<int:curso>")
def mostrar_calificaciones_por_curso(curso):

    calificaciones = listar_calificaciones_por_curso(curso)

    return render_template(
        "calificaciones/por_curso.html",
        curso=curso,
        calificaciones=calificaciones
    )


@app.route("/calificaciones/planilla", methods=["GET", "POST"])
def planilla_calificaciones():

    cursos = listar_cursos()

    if request.method == "POST":

        curso = request.form.get("curso", type=int)
        id_materia = request.form.get("id_materia", type=int)

        # Comprobar que el curso sea válido.
        if curso not in cursos:
            flash("El curso seleccionado no es válido.", "error")
            return redirect(url_for("planilla_calificaciones"))

        # Comprobar que la materia pertenezca al curso.
        materias_del_curso = listar_materias_por_curso(curso)

        materia_valida = any(
            materia[0] == id_materia
            for materia in materias_del_curso
        )

        if not materia_valida:
            flash("La materia no corresponde al curso seleccionado.", "error")
            return redirect(
                url_for("planilla_calificaciones", curso=curso)
            )

        registros = []

        # Recibir los estudiantes enviados desde el formulario.
        for valor_id in request.form.getlist("id_estudiante"):

            try:
                id_estudiante = int(valor_id)
            except ValueError:
                flash("Se recibió un identificador de estudiante inválido.", "error")
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
                registros
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

    # A partir de aquí continúa la visualización habitual.
    curso = request.args.get("curso", type=int)
    id_materia = request.args.get("id_materia", type=int)

    materias = []
    calificaciones = []
    materia_seleccionada = None

    if curso in cursos:
        materias = listar_materias_por_curso(curso)

        for materia in materias:
            if materia[0] == id_materia:
                materia_seleccionada = materia
                break

        if materia_seleccionada is not None:
            calificaciones = (
                listar_calificaciones_por_curso_y_materia(
                    curso, id_materia
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

# main
if __name__ == "__main__":
    app.run(debug=True)

