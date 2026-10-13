from basededatos.conexion import conectar


def listar_calificaciones_por_curso(curso):

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT
                e.nro,
                e.nombre_apellido,
                m.nombre_materia,
                m.turno,
                c.nota_primer_trimestre,
                c.nota_segundo_trimestre,
                c.nota_tercer_trimestre,
                c.promedio_anual,
                c.nota_examen_diciembre,
                c.nota_examen_marzo,
                c.calificacion_final
            FROM calificaciones c
            JOIN estudiantes e
                ON c.id_estudiante = e.id_estudiante
            JOIN materias m
                ON c.id_materia = m.id_materia
            WHERE m.curso = ?
            ORDER BY e.nro, m.nombre_materia
        """

        cursor.execute(consulta, (curso,))
        calificaciones = cursor.fetchall()

        return calificaciones

    finally:
        conexion.close()


from basededatos.conexion import conectar


def listar_calificaciones_por_curso_y_materia(curso, id_materia):

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT
                e.nro,
                e.nombre_apellido,
                e.dni,
                c.nota_primer_trimestre,
                c.nota_segundo_trimestre,
                c.nota_tercer_trimestre,
                c.promedio_anual,
                c.nota_examen_diciembre,
                c.nota_examen_marzo,
                c.calificacion_final,
                c.observaciones
            FROM calificaciones AS c
            INNER JOIN estudiantes AS e
                ON c.id_estudiante = e.id_estudiante
            INNER JOIN materias AS m
                ON c.id_materia = m.id_materia
            WHERE m.curso = ?
              AND m.id_materia = ?
            ORDER BY e.nombre_apellido COLLATE NOCASE ASC
        """

        cursor.execute(consulta, (curso, id_materia))

        return cursor.fetchall()

    finally:
        conexion.close()
