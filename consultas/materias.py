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