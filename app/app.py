from flask import Flask, render_template, request
from consultas.estudiantes import listar_estudiantes, insertar_estudiante
from consultas.materias import listar_materias, insertar_materia
from consultas.calificaciones import listar_calificaciones_por_curso

app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("index.html")

# ESTUDIANTES

# Ruta para alta de estudiantes
@app.route("/estudiantes/alta", methods=["GET", "POST"])
def alta_estudiante():

    if request.method == "POST":

        nro = int(request.form["nro"])
        nombre_apellido = request.form["nombre_apellido"]
        dni = int(request.form["dni"])

        resultado, mensaje = insertar_estudiante(nro, nombre_apellido, dni)

        if resultado:
            return "<h1>Estudiante guardado correctamente</h1>"

        else:
            return f"<h1>Error al guardar estudiante</h1><p>{mensaje}</p>"

    return render_template("estudiantes/alta_estudiante.html")


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

# FIN CALIFICACIONES

# main
if __name__ == "__main__":
    app.run(debug=True)