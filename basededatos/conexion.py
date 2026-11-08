import sqlite3
import os

def conectar():

    ruta = os.path.abspath("basededatos/calificaciones.db")
    #print("BASE DE DATOS UTILIZADA:", ruta)

    conexion = sqlite3.connect(ruta)

    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion