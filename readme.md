# Sistema de gestión de calificaciones

Proyecto desarrollado con **Python, Flask y SQLite** para la gestión de estudiantes, materias y calificaciones.

Este proyecto surge como una **adaptación a Flask de una versión previa desarrollada como aplicación de consola**, manteniendo como base la estructura y lógica de acceso a datos desarrollada originalmente con Python y SQLite.

## Tecnologías utilizadas

* Python
* Flask
* SQLite
* HTML
* Jinja2
* Git / GitHub

## Estado del proyecto

El proyecto se encuentra en desarrollo.

La rama `main` contiene la versión estable, mientras que la rama `desarrollo` se utiliza para incorporar y probar nuevas funcionalidades antes de integrarlas a `main`.

## Funcionalidades

Actualmente se encuentra implementado:

* Visualización de estudiantes.
* Alta de estudiantes.
* Conexión con la base de datos SQLite.
* Uso de plantillas HTML mediante Jinja2.

Se continuará incorporando progresivamente la gestión de materias y calificaciones.

## Estructura general

```text
miproyecto_flask/
├── app/
├── basededatos/
├── consultas/
└── ...
```

La aplicación mantiene separadas las rutas de Flask, las consultas a la base de datos y las plantillas utilizadas para
