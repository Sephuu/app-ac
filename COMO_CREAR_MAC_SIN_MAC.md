# Cómo crear el ejecutable de Mac SIN tener una Mac

Como no tienes una Mac a mano, vamos a usar **GitHub Actions**. Básicamente, GitHub te presta una Mac en la nube gratis por unos minutos para "construir" tu programa.

## Pasos a seguir:

1.  **Crea una cuenta en GitHub.com** (si no tienes una).
2.  **Crea un "Nuevo Repositorio"** (New Repository):
    *   Ponle nombre (ej: `EtiquetasApp`).
    *   Selecciona **"Private"** (Privado) para que nadie más vea tu código.
    *   Dale a "Create repository".

3.  **Sube tus archivos**:
    *   En la página de tu nuevo repositorio, verás una opción "uploading an existing file".
    *   Arrastra **TODOS** los archivos de tu carpeta `EtiquetasPanApp` ahí (especialmente `.github`, `collage_maker.py`, `requirements.txt`, `collage_maker.spec`).
    *   Dale a "Commit changes".

4.  **Espera la magia 🪄**:
    *   Ve a la pestaña **"Actions"** en tu repositorio de GitHub.
    *   Verás un proceso llamado "Build Mac App" (o similar) ejecutándose (círculo amarillo girando).
    *   Espera a que se ponga verde (✅).

5.  **Descarga tu App**:
    *   Haz clic en el nombre del proceso (ej: "Build Mac App").
    *   Abajo del todo, en la sección **"Artifacts"**, verás un archivo llamado `MacApp-Zip`.
    *   **Descárgalo.** Ese zip contiene tu `collage_maker.app`.

¡Ese archivo `.zip` (o la `.app` descomprimida) es lo que tienes que enviar a la persona que usa Mac! Ella solo tendrá que descomprimirlo y arrastrar la app a su carpeta de Aplicaciones.
