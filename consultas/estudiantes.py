from basededatos.conexion import conectar


def listar_estudiantes():

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        consulta = """
            SELECT *
            FROM estudiantes
        """

        cursor.execute(consulta)

        estudiantes = cursor.fetchall()

        return estudiantes

    finally:

        conexion.close()

def insertar_estudiante(nro, nombre_apellido, dni):

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        consulta = """
            INSERT INTO estudiantes (nro, nombre_apellido, dni)
            VALUES (?, ?, ?)
        """

        cursor.execute(consulta, (nro, nombre_apellido, dni))

        conexion.commit()

        return True, "Estudiante insertado correctamente"

    except Exception as e:

        return False, str(e)

    finally:

        conexion.close()