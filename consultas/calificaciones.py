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

    campos_trimestres = (
        "nota_primer_trimestre",
        "nota_segundo_trimestre",
        "nota_tercer_trimestre",
    )

    campos_examenes = (
        "nota_examen_diciembre",
        "nota_examen_marzo",
    )

    campos_notas = campos_trimestres + campos_examenes

    try:
        cursor = conexion.cursor()

        # 1. Verificar que exista la materia seleccionada.
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

        # 2. Procesar cada estudiante recibido desde la planilla.
        for registro in registros:

            id_estudiante = registro["id_estudiante"]
            notas = registro["notas"]

            # Verificar que exista el estudiante.
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

            notas_validas = {}

            # 3. Validar las notas ingresadas.
            for campo in campos_notas:

                valor = notas.get(campo, "")

                if valor is None:
                    valor = ""

                valor = str(valor).strip()

                # Una celda vacía no modifica la nota guardada.
                if valor == "":
                    continue

                # Permitir coma decimal, además del punto.
                valor = valor.replace(",", ".")

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

            # 4. Buscar el registro de calificaciones existente.
            cursor.execute(
                """
                SELECT id_calificacion
                FROM calificaciones
                WHERE id_estudiante = ? AND id_materia = ?
                """,
                (id_estudiante, id_materia)
            )

            existente = cursor.fetchone()

            if existente:

                # 5. Actualizar solamente las notas modificadas.
                if notas_validas:

                    campos_update = ", ".join(
                        f"{campo} = ?" for campo in notas_validas
                    )

                    valores_update = list(notas_validas.values())
                    valores_update.extend([
                        id_estudiante,
                        id_materia
                    ])

                    cursor.execute(
                        f"""
                        UPDATE calificaciones
                        SET {campos_update}
                        WHERE id_estudiante = ? AND id_materia = ?
                        """,
                        valores_update
                    )

            else:

                # No crear un registro si todas las celdas están vacías.
                if not notas_validas:
                    continue

                # 6. Insertar el registro inicial del estudiante.
                columnas = [
                    "id_estudiante",
                    "id_materia",
                    *notas_validas.keys()
                ]

                valores_insert = [
                    id_estudiante,
                    id_materia,
                    *notas_validas.values()
                ]

                marcadores = ", ".join(
                    "?" for _ in columnas
                )

                cursor.execute(
                    f"""
                    INSERT INTO calificaciones
                    ({", ".join(columnas)})
                    VALUES ({marcadores})
                    """,
                    valores_insert
                )

            # 7. Recuperar todas las notas actuales de la base de datos.
            # Así conservamos las notas anteriores que no se modificaron.
            cursor.execute(
                """
                SELECT
                    nota_primer_trimestre,
                    nota_segundo_trimestre,
                    nota_tercer_trimestre,
                    nota_examen_diciembre,
                    nota_examen_marzo
                FROM calificaciones
                WHERE id_estudiante = ? AND id_materia = ?
                """,
                (id_estudiante, id_materia)
            )

            fila = cursor.fetchone()

            if fila is None:
                continue

            trimestres = [
                float(nota) if nota is not None else None
                for nota in fila[:3]
            ]

            diciembre = (
                float(fila[3]) if fila[3] is not None else None
            )

            marzo = (
                float(fila[4]) if fila[4] is not None else None
            )

            # 8. Calcular el promedio anual.
            # Solo se calcula si los tres trimestres tienen nota.
            if all(nota is not None for nota in trimestres):
                promedio_anual = round(sum(trimestres) / 3, 2)
            else:
                promedio_anual = None

            # 9. Calcular la calificación final.
            calificacion_final = None

            # Aprobación directa:
            # promedio >= 7 y cada trimestre >= 4.
            if (
                promedio_anual is not None
                and promedio_anual >= 7
                and all(nota >= 4 for nota in trimestres)
            ):

                calificacion_final = promedio_anual

            else:

                # Si diciembre alcanza 7, se utiliza esa nota.
                if diciembre is not None and diciembre >= 7:

                    calificacion_final = diciembre

                # Si diciembre no alcanza 7, se evalúa marzo.
                elif marzo is not None and marzo >= 7:

                    calificacion_final = marzo

            # 10. Guardar los resultados calculados.
            cursor.execute(
                """
                UPDATE calificaciones
                SET promedio_anual = ?,
                    calificacion_final = ?
                WHERE id_estudiante = ? AND id_materia = ?
                """,
                (
                    promedio_anual,
                    calificacion_final,
                    id_estudiante,
                    id_materia
                )
            )

        # 11. Confirmar todos los cambios.
        conexion.commit()

    except Exception:
        # Si algo falla, deshacer todos los cambios de esta operación.
        conexion.rollback()
        raise

    finally:
        # Cerrar la conexión independientemente del resultado.
        conexion.close()

