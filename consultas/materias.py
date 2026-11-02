from basededatos.conexion import conectar


def listar_materias():
    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT
                m.id_materia,
                m.nombre_materia,
                m.curso,
                COALESCE(u.nombre_apellido, m.docente) AS docente,
                m.turno
            FROM materias m
            LEFT JOIN usuarios u
                ON m.id_usuario = u.id_usuario
            ORDER BY m.curso ASC
        """

        cursor.execute(consulta)
        return cursor.fetchall()

    finally:
        conexion.close()


def listar_docentes():
    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT id_usuario, nombre_apellido
            FROM usuarios
            WHERE rol = 'docente'
            ORDER BY nombre_apellido ASC
        """

        cursor.execute(consulta)
        return cursor.fetchall()

    finally:
        conexion.close()


def insertar_materia(nombre_materia, id_grupo, id_usuario):
    conexion = conectar()

    try:
        cursor = conexion.cursor()

        # 1. Verificar que el usuario seleccionado sea docente.
        cursor.execute("""
            SELECT nombre_apellido
            FROM usuarios
            WHERE id_usuario = ?
              AND rol = 'docente'
        """, (id_usuario,))

        docente = cursor.fetchone()

        if docente is None:
            return False

        # 2. Obtener curso y turno del grupo seleccionado.
        cursor.execute("""
            SELECT curso, turno
            FROM grupos_nuevo
            WHERE id_grupo = ?
        """, (id_grupo,))

        grupo = cursor.fetchone()

        if grupo is None:
            return False

        curso = grupo[0]
        turno = grupo[1]

        # 3. Registrar la materia con su grupo y docente.
        consulta = """
            INSERT INTO materias (
                nombre_materia,
                curso,
                docente,
                turno,
                id_usuario,
                id_grupo
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """

        cursor.execute(
            consulta,
            (
                nombre_materia,
                curso,
                docente[0],
                turno,
                id_usuario,
                id_grupo
            )
        )

        conexion.commit()
        return True

    except Exception as error:
        conexion.rollback()
        print(f"Error al insertar materia: {error}")
        return False

    finally:
        conexion.close()

def listar_materias_por_curso(curso, id_usuario=None):

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT
                m.id_materia,
                m.nombre_materia,
                m.curso,
                COALESCE(u.nombre_apellido, m.docente) AS docente,
                m.turno
            FROM materias m
            LEFT JOIN usuarios u
                ON m.id_usuario = u.id_usuario
            WHERE m.curso = ?
              AND (? IS NULL OR m.id_usuario = ?)
            ORDER BY m.nombre_materia COLLATE NOCASE ASC
        """

        cursor.execute(
            consulta,
            (curso, id_usuario, id_usuario)
        )

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

def actualizar_docente_materia(id_materia, id_usuario):

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        # Verificar que el usuario seleccionado sea docente.
        cursor.execute("""
            SELECT nombre_apellido
            FROM usuarios
            WHERE id_usuario = ?
              AND rol = 'docente'
        """, (id_usuario,))

        docente = cursor.fetchone()

        if docente is None:
            return False

        # Actualizar el docente responsable de la materia.
        cursor.execute("""
            UPDATE materias
            SET id_usuario = ?,
                docente = ?
            WHERE id_materia = ?
        """, (id_usuario, docente[0], id_materia))

        if cursor.rowcount == 0:
            conexion.rollback()
            return False

        conexion.commit()
        return True

    except Exception as error:
        conexion.rollback()
        print(f"Error al actualizar docente: {error}")
        return False

    finally:
        conexion.close()

def listar_grupos():
    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT
                id_grupo,
                curso,
                turno,
                division
            FROM grupos_nuevo
            ORDER BY curso ASC, division ASC
        """

        cursor.execute(consulta)
        return cursor.fetchall()

    finally:
        conexion.close()