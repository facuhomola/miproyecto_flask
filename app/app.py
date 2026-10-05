from flask import Flask, render_template, request
from consultas.estudiantes import listar_estudiantes, insertar_estudiante

app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("index.html")

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


# Ruta para mostrar estudiantes
@app.route("/estudiantes")
def mostrar_estudiantes(): # Función para mostrar estudiantes

    print("ENTRÓ A LA RUTA /ESTUDIANTES")

    estudiantes = listar_estudiantes()

    print("ESTUDIANTES:", estudiantes)

    return render_template(
        "estudiantes/mostrar_estudiantes.html",
        estudiantes=estudiantes
    )

# Ruta para alta de materias
@app.route("/materias/alta")
def alta_materia():
    return render_template("alta_materia.html")

if __name__ == "__main__":
    app.run(debug=True)