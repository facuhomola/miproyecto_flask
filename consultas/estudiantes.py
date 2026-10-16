from basededatos.conexion import conectar


def listar_estudiantes():

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        consulta = """
            SELECT
                e.id_estudiante,
                e.nro,
                e.nombre_apellido,
                e.dni,
                CASE
                    WHEN g.id_grupo IS NULL THEN 'Sin asignar'
                    ELSE g.curso || '° año - ' || g.turno
                END AS grupo
            FROM estudiantes AS e
            LEFT JOIN grupos AS g
                ON e.id_grupo = g.id_grupo
            ORDER BY e.nro ASC
        """

        cursor.execute(consulta)

        estudiantes = cursor.fetchall()

        return estudiantes

    finally:

        conexion.close()

def insertar_estudiante(nro, nombre_apellido, dni, id_grupo):

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        consulta = """
            INSERT INTO estudiantes (nro, nombre_apellido, dni, id_grupo)
            VALUES (?, ?, ?, ?)
        """

        cursor.execute(consulta, (nro, nombre_apellido, dni, id_grupo))

        conexion.commit()

        return True, "Estudiante insertado correctamente"

    except Exception as e:

        return False, str(e)

    finally:

        conexion.close()

def listar_grupos():

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        consulta = """
            SELECT id_grupo, curso, turno
            FROM grupos
            ORDER BY curso ASC,
                CASE turno
                    WHEN 'mañana' THEN 1
                    WHEN 'tarde' THEN 2
                    WHEN 'noche' THEN 3
                END
        """

        cursor.execute(consulta)

        return cursor.fetchall()

    finally:

        conexion.close()

def listar_estudiantes_por_grupo(id_grupo):

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        consulta = """
            SELECT
                id_estudiante,
                nro,
                nombre_apellido,
                dni
            FROM estudiantes
            WHERE id_grupo = ?
            ORDER BY nro ASC
        """

        cursor.execute(consulta, (id_grupo,))

        return cursor.fetchall()

    finally:

        conexion.close()