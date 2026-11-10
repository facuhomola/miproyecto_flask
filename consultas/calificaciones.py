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
                g.turno,
                g.division,
                c.nota_primer_trimestre,
                c.nota_segundo_trimestre,
                c.nota_tercer_trimestre,
                c.promedio_anual,
                c.nota_examen_diciembre,
                c.nota_examen_marzo,
                c.calificacion_final,
                c.observaciones
            FROM calificaciones c

            JOIN estudiantes e
                ON c.id_estudiante = e.id_estudiante

            JOIN grupos_nuevo g
                ON e.id_gruponuevo = g.id_grupo

            JOIN materias m
                ON c.id_materia = m.id_materia

            WHERE m.curso = ?

            ORDER BY
                g.division ASC,
                e.nro ASC,
                m.nombre_materia ASC
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
            FROM materias AS m

            JOIN estudiantes AS e
                ON e.id_gruponuevo = m.id_grupo

            LEFT JOIN calificaciones AS c
                ON c.id_estudiante = e.id_estudiante
                AND c.id_materia = m.id_materia

            WHERE m.id_materia = ?
              AND m.curso = ?

            ORDER BY e.nro ASC
        """

        cursor.execute(consulta, (id_materia, curso))

        return cursor.fetchall()

    finally:
        conexion.close()

def listar_calificaciones_generales(id_usuario=None):

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT
                e.nro,
                e.nombre_apellido,
                e.dni,
                g.curso,
                g.turno,
                g.division,
                m.nombre_materia,
                c.nota_primer_trimestre,
                c.nota_segundo_trimestre,
                c.nota_tercer_trimestre,
                c.promedio_anual,
                c.nota_examen_diciembre,
                c.nota_examen_marzo,
                c.calificacion_final,
                c.observaciones
            FROM calificaciones c

            JOIN estudiantes e
                ON c.id_estudiante = e.id_estudiante

            JOIN grupos_nuevo g
                ON e.id_gruponuevo = g.id_grupo

            JOIN materias m
                ON c.id_materia = m.id_materia

            WHERE (? IS NULL OR m.id_usuario = ?)

            ORDER BY
                g.curso ASC,
                g.division ASC,
                e.nro ASC,
                m.nombre_materia ASC
        """

        cursor.execute(
            consulta,
            (id_usuario, id_usuario)
        )

        return cursor.fetchall()

    finally:
        conexion.close()



def guardar_calificaciones_planilla(id_materia, registros, id_usuario=None):

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

        # 1. Verificar que exista la materia.
        cursor.execute(
            """
            SELECT id_materia, id_grupo, id_usuario
            FROM materias
            WHERE id_materia = ?
            """,
            (id_materia,)
        )

        materia = cursor.fetchone()

        if materia is None:
            raise ValueError("La materia seleccionada no existe.")

        id_grupo_materia = materia[1]
        id_docente_materia = materia[2]

        # 2. Verificar autorización del docente.
        if (
            id_usuario is not None
            and id_docente_materia != id_usuario
        ):
            raise ValueError(
                "No tenés autorización para modificar esta materia."
            )

        # 3. Procesar cada estudiante.
        for registro in registros:

            id_estudiante = registro["id_estudiante"]
            notas = registro["notas"]

            # Obtener y preparar la observación.
            observaciones = registro.get("observaciones", "")

            if observaciones is None:
                observaciones = ""

            observaciones = str(observaciones).strip()

            # 4. Verificar que el estudiante pertenezca al grupo.
            cursor.execute(
                """
                SELECT id_estudiante, id_gruponuevo
                FROM estudiantes
                WHERE id_estudiante = ?
                """,
                (id_estudiante,)
            )

            estudiante = cursor.fetchone()

            if estudiante is None:
                raise ValueError(
                    f"El estudiante {id_estudiante} no existe."
                )

            if estudiante[1] != id_grupo_materia:
                raise ValueError(
                    "El estudiante no pertenece al grupo de esta materia."
                )

            notas_validas = {}

            # 5. Validar las notas ingresadas.
            for campo in campos_notas:

                valor = notas.get(campo, "")

                if valor is None:
                    valor = ""

                valor = str(valor).strip()

                # Una celda vacía no modifica la nota guardada.
                if valor == "":
                    continue

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

            # 6. Buscar el registro existente.
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

                # Actualizar notas y observaciones.
                campos_update = {
                    **notas_validas,
                    "observaciones": observaciones
                }

                campos_sql = ", ".join(
                    f"{campo} = ?" for campo in campos_update
                )

                valores_update = list(campos_update.values())

                valores_update.extend([
                    id_estudiante,
                    id_materia
                ])

                cursor.execute(
                    f"""
                    UPDATE calificaciones
                    SET {campos_sql}
                    WHERE id_estudiante = ? AND id_materia = ?
                    """,
                    valores_update
                )

            else:

                # No crear registros si no hay notas ni observaciones.
                if not notas_validas and not observaciones:
                    continue

                # Insertar el registro inicial.
                columnas = [
                    "id_estudiante",
                    "id_materia",
                    *notas_validas.keys(),
                    "observaciones"
                ]

                valores_insert = [
                    id_estudiante,
                    id_materia,
                    *notas_validas.values(),
                    observaciones
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

            # 7. Recuperar las notas actuales.
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
            if all(nota is not None for nota in trimestres):
                promedio_anual = round(sum(trimestres) / 3, 2)
            else:
                promedio_anual = None

            # 9. Calcular la calificación final.
            calificacion_final = None

            if (
                promedio_anual is not None
                and promedio_anual >= 7
                and all(nota >= 4 for nota in trimestres)
            ):

                calificacion_final = promedio_anual

            else:

                if diciembre is not None and diciembre >= 7:
                    calificacion_final = diciembre

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
        conexion.rollback()
        raise

    finally:
        conexion.close()

