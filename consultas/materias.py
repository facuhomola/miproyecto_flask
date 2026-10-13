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


def listar_materias_por_curso(curso):

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT id_materia, nombre_materia, curso, docente, turno
            FROM materias
            WHERE curso = ?
            ORDER BY nombre_materia COLLATE NOCASE ASC
        """

        cursor.execute(consulta, (curso,))

        return cursor.fetchall()

    finally:
        conexion.close()



def listar_cursos():

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT DISTINCT curso
            FROM materias
            ORDER BY curso ASC
        """

        cursor.execute(consulta)

        return [fila[0] for fila in cursor.fetchall()]

    finally:
        conexion.close()
