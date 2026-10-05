from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    lista = ["Elemento 1", "Elemento 2", "Elemento 3"]
    numero_de_elementos = len(lista)
    data = {
        'titulo': 'Index123',
        'bienvenida': 'Bienvenido a mi aplicación Flask',
        'lista': lista,
        'numero_elementos': len(lista)
    }
    return render_template("index.html", data=data)
    #return "<h1>Hola, Mundo!</h1>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
