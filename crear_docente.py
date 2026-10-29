
from getpass import getpass

from consultas.usuarios import crear_usuario


def inicializar_docente():
    print("=== Crear usuario docente ===")

    nombre_apellido = input(
        "Nombre y apellido reales: "
    ).strip()

    dni = input(
        "DNI: "
    ).strip()

    nombre_usuario = input(
        "Nombre de usuario: "
    ).strip()

    contrasenia = getpass(
        "Contraseña: "
    )

    confirmar_contrasenia = getpass(
        "Confirmar contraseña: "
    )

    if contrasenia != confirmar_contrasenia:
        print("Error: las contraseñas no coinciden.")
        return

    correcto, mensaje = crear_usuario(
        nombre_usuario,
        contrasenia,
        "docente",
        nombre_apellido,
        dni
    )

    print(mensaje)


if __name__ == "__main__":
    inicializar_docente()
