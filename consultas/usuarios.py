import sqlite3

from basededatos.conexion import conectar
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


def crear_usuario(
    nombre_de_usuario,
    contrasenia,
    rol,
    nombre_apellido,
    dni
):
    """
    Registra un usuario con sus datos personales
    y contraseña protegida mediante hash.
    """

    nombre_de_usuario = nombre_de_usuario.strip()
    nombre_apellido = nombre_apellido.strip()
    dni = dni.strip()

    roles_validos = ("administrador", "docente")

    if not nombre_de_usuario:
        return False, "El nombre de usuario es obligatorio"

    if not contrasenia:
        return False, "La contraseña es obligatoria"

    if not nombre_apellido:
        return False, "El nombre y apellido son obligatorios"

    if not dni:
        return False, "El DNI es obligatorio"

    if rol not in roles_validos:
        return False, "El rol seleccionado no es válido"

    contrasenia_hash = generate_password_hash(contrasenia)

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO usuarios (
                nombre_de_usuario,
                contrasenia,
                rol,
                nombre_apellido,
                dni
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            nombre_de_usuario,
            contrasenia_hash,
            rol,
            nombre_apellido,
            dni
        ))

        conexion.commit()

        return True, "Usuario creado correctamente"

    except sqlite3.IntegrityError as e:
        if "usuarios.nombre_de_usuario" in str(e):
            return False, "El nombre de usuario ya existe"

        if "usuarios.dni" in str(e):
            return False, "El DNI ya existe"

        return False, "No se pudo registrar el usuario"

    except sqlite3.Error:
        return False, "Error al acceder a la base de datos"

    finally:
        conexion.close()


def buscar_usuario(nombre_de_usuario):
    """
    Busca un usuario por su nombre de usuario.
    """

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_usuario,
                nombre_de_usuario,
                contrasenia,
                rol,
                nombre_apellido,
                dni
            FROM usuarios
            WHERE nombre_de_usuario = ?
        """, (nombre_de_usuario.strip(),))

        return cursor.fetchone()

    finally:
        conexion.close()


def verificar_contrasenia(
    contrasenia_ingresada,
    contrasenia_hash
):
    """
    Verifica una contraseña contra su hash almacenado.
    """

    if not contrasenia_hash:
        return False

    return check_password_hash(
        contrasenia_hash,
        contrasenia_ingresada
    )
