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
                dni,
                activo
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


def listar_usuarios_docentes():
    """
    Obtiene todos los usuarios registrados con rol docente.
    """

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_usuario,
                nombre_apellido,
                dni,
                nombre_de_usuario,
                activo
            FROM usuarios
            WHERE rol = 'docente'
            ORDER BY nombre_apellido
        """)

        return cursor.fetchall()

    finally:
        conexion.close()

def suspender_usuario(id_usuario):
    """
    Suspende una cuenta docente sin eliminar sus datos.
    """

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE usuarios
            SET activo = 0
            WHERE id_usuario = ?
            AND rol = 'docente'
            AND activo = 1
        """, (id_usuario,))

        conexion.commit()

        return cursor.rowcount > 0

    except sqlite3.Error:
        conexion.rollback()
        return False

    finally:
        conexion.close()

def reactivar_usuario(id_usuario):
    """
    Reactiva una cuenta docente suspendida.
    """

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE usuarios
            SET activo = 1
            WHERE id_usuario = ?
            AND rol = 'docente'
            AND activo = 0
        """, (id_usuario,))

        conexion.commit()

        return cursor.rowcount > 0

    except sqlite3.Error:
        conexion.rollback()
        return False

    finally:
        conexion.close()

def actualizar_usuario(id_usuario, nombre_apellido, dni, nombre_de_usuario):

    nombre_apellido = nombre_apellido.strip()
    dni = dni.strip()
    nombre_de_usuario = nombre_de_usuario.strip()

    if not nombre_apellido or not dni or not nombre_de_usuario:
        return False, "Todos los campos son obligatorios."

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE usuarios
            SET
                nombre_apellido = ?,
                dni = ?,
                nombre_de_usuario = ?
            WHERE id_usuario = ?
            AND rol = 'docente'
        """, (
            nombre_apellido,
            dni,
            nombre_de_usuario,
            id_usuario
        ))

        if cursor.rowcount == 0:
            conexion.rollback()
            return False, "No se encontró el docente."

        conexion.commit()
        return True, "Datos del docente actualizados correctamente."

    except sqlite3.IntegrityError:
        conexion.rollback()
        return False, "El nombre de usuario o DNI ya existe."

    except sqlite3.Error:
        conexion.rollback()
        return False, "Error al actualizar los datos del docente."

    finally:
        conexion.close()

def buscar_docente_por_id(id_usuario):

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_usuario,
                nombre_apellido,
                dni,
                nombre_de_usuario
            FROM usuarios
            WHERE id_usuario = ?
            AND rol = 'docente'
        """, (id_usuario,))

        return cursor.fetchone()

    finally:
        conexion.close()