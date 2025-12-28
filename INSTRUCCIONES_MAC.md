# Instrucciones para ejecutar en Mac (Versión Moderna)

Esta versión utiliza una nueva interfaz moderna que funciona perfecto en Mac.

## 1. Requisitos Previos

Necesitas tener **Python 3** instalado.

## 2. Instalación de Dependencias

Abre la aplicación **Terminal** y navega a la carpeta donde guardaste estos archivos:
(Por ejemplo, si está en Descargas)
```bash
cd ~/Downloads/EtiquetasPanApp
```

Instala las librerías necesarias (¡Importante! Se añadió `customtkinter`):
```bash
pip3 install -r requirements.txt
```

## 3. Ejecutar la Aplicación

Ejecuta el programa con:
```bash
python3 collage_maker.py
```

## Notas
*   Ahora la aplicación tiene un "Tema Oscuro" y botones modernos.
*   Puedes cambiar entre modo Claro y Oscuro en la barra lateral.
*   Si macOS pide permisos para acceder a carpetas, acéptalos.

## Solución de problemas
Si al ejecutar te sale error de `ModuleNotFoundError: No module named 'customtkinter'`, asegúrate de haber ejecutado el comando `pip3 install -r requirements.txt`.
