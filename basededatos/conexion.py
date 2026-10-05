import sqlite3

def conectar():

    conexion = sqlite3.connect("basededatos/calificaciones.db")

    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion