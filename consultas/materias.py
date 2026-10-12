from basededatos.conexion import conectar

def listar_materias():

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        consulta = """
            SELECT *
            FROM materias
            ORDER BY curso ASC
        """

        cursor.execute(consulta)

        materias = cursor.fetchall()

        return materias

    finally:
        conexion.close()


def insertar_materia(nombre_materia, curso, docente, turno):

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO materias (
                nombre_materia,
                curso,
                docente,
                turno
            )
            VALUES (?, ?, ?, ?)
        """

        cursor.execute(
            consulta,
            (nombre_materia, curso, docente, turno)
        )

        conexion.commit()

        return True

    except Exception as error:
        conexion.rollback()
        print(f"Error al insertar materia: {error}")
        return False

    finally:
        conexion.close()