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


def listar_calificaciones_por_curso_y_materia(curso, id_materia):

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT
                e.id_estudiante,
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
            FROM estudiantes AS e

            LEFT JOIN calificaciones AS c
                ON c.id_estudiante = e.id_estudiante
                AND c.id_materia = ?

            ORDER BY e.nro ASC
        """

        cursor.execute(consulta, (id_materia,))

        return cursor.fetchall()

    finally:
        conexion.close()


def guardar_calificaciones_planilla(id_materia, registros):

    conexion = conectar()

    campos_notas = (
        "nota_primer_trimestre",
        "nota_segundo_trimestre",
        "nota_tercer_trimestre",
        "nota_examen_diciembre",
        "nota_examen_marzo",
    )

    try:
        cursor = conexion.cursor()

        # Verificar que la materia exista.
        cursor.execute(
            """
            SELECT id_materia
            FROM materias
            WHERE id_materia = ?
            """,
            (id_materia,)
        )

        if cursor.fetchone() is None:
            raise ValueError("La materia seleccionada no existe.")

        for registro in registros:

            id_estudiante = registro["id_estudiante"]
            notas = registro["notas"]

            # Verificar que el estudiante exista.
            cursor.execute(
                """
                SELECT id_estudiante
                FROM estudiantes
                WHERE id_estudiante = ?
                """,
                (id_estudiante,)
            )

            if cursor.fetchone() is None:
                raise ValueError(
                    f"El estudiante {id_estudiante} no existe."
                )

            # Validar las notas recibidas.
            notas_validas = {}

            for campo in campos_notas:
                valor = notas.get(campo, "").strip()

                # Una celda vacía no modifica una nota existente.
                if valor == "":
                    continue

                try:
                    nota = float(valor)
                except ValueError:
                    raise ValueError(
                        f"El valor de {campo} debe ser numérico."
                    )

                if not 0 <= nota <= 10:
                    raise ValueError(
                        f"La nota de {campo} debe estar entre 0 y 10."
                    )

                notas_validas[campo] = nota

            # Si no se completó ninguna nota, no hay nada que guardar.
            if not notas_validas:
                continue

            # Buscar si ya existe la combinación estudiante-materia.
            cursor.execute(
                """
                SELECT id_calificacion
                FROM calificaciones
                WHERE id_estudiante = ?
                  AND id_materia = ?
                """,
                (id_estudiante, id_materia)
            )

            existente = cursor.fetchone()

            if existente:
                # Actualizar únicamente los campos completados.
                campos = ", ".join(
                    f"{campo} = ?" for campo in notas_validas
                )

                valores = list(notas_validas.values())
                valores.extend([id_estudiante, id_materia])

                cursor.execute(
                    f"""
                    UPDATE calificaciones
                    SET {campos}
                    WHERE id_estudiante = ?
                      AND id_materia = ?
                    """,
                    valores
                )

            else:
                # Crear un registro nuevo.
                columnas = [
                    "id_estudiante",
                    "id_materia",
                    *notas_validas.keys(),
                ]

                valores = [
                    id_estudiante,
                    id_materia,
                    *notas_validas.values(),
                ]

                marcadores = ", ".join(
                    "?" for _ in columnas
                )

                cursor.execute(
                    f"""
                    INSERT INTO calificaciones (
                        {", ".join(columnas)}
                    )
                    VALUES ({marcadores})
                    """,
                    valores
                )

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()