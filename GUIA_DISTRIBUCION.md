# Guía para Compartir la Aplicación (Sin Código)

Para compartir tu programa sin que nadie pueda ver ni modificar tu código fuente, debes **enviar solamente el archivo ejecutable**.

## Diferencia entre archivos

*   ❌ **Código Fuente (.py):** Son tus planos. Si envías esto, cualquiera puede leerlo y cambiarlo. Es lo que tienes en tu carpeta principal.
*   ✅ **Ejecutable (.exe / .app):** Es el edificio terminado. La gente puede usarlo, pero no puede ver cómo está construido por dentro.

## ¿Qué archivo debo enviar?

Dependiendo del sistema operativo de la persona que lo usará:

### Para usuarios de MAC 🍎
1.  Debes crear el ejecutable **desde una Mac** (ver instrucciones en `INSTRUCCIONES_MAC.md`).
2.  Una vez creado, ve a la carpeta **`dist`**.
3.  Encontrarás un archivo llamado **`collage_maker.app`**.
4.  **Ese es el único archivo que debes enviar.** Puedes comprimirlo en un `.zip` para enviarlo por correo o WeTransfer.

### Para usuarios de WINDOWS 🪟
1.  Puedes crearlo ahora mismo en tu computadora.
2.  Abre la terminal y escribe:
    ```bash
    pyinstaller collage_maker.spec
    ```
3.  Cuando termine, entra a la carpeta **`dist`**.
4.  Verás una carpeta llamada `collage_maker` (o un archivo `collage_maker.exe`).
5.  **Envía esa carpeta o archivo.** El destinatario solo tiene que hacer doble clic en `collage_maker.exe` para usarlo. No necesita instalar Python ni nada más.

## Consejos de Seguridad

*   Cuando compartas el archivo de la carpeta `dist`, la otra persona **NO necesita** instalar nada. El programa ya lleva todo incluido (Python, librerías, imágenes, etc.).
*   Si quieres que se vea aún más profesional, puedes cambiarle el nombre al archivo final (por ejemplo: `EtiquetasSephu.app` o `EtiquetasSephu.exe`).
