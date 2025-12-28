# Solución: "La aplicación no se puede abrir" (Apple Silicon)

Si al intentar abrir `collage_maker.app` en tu Mac con chip M1/M2/M3 aparece un mensaje como:
- *"collage_maker no se puede abrir porque proviene de un desarrollador no identificado"*
- *"collage_maker está dañado y no se puede abrir"*
- *"No se puede verificar el desarrollador"*

**No te preocupes, es completamente normal.** macOS protege las apps que no están firmadas digitalmente.

## ✅ Solución Principal (Apple Silicon)

### Método 1: Abrir con clic derecho (MÁS RÁPIDO)

1.  **Haz clic derecho** (o Control + clic) en `collage_maker.app`
2.  Selecciona **"Abrir"** del menú contextual
3.  Aparecerá un diálogo con el botón **"Abrir"** → ¡Haz clic ahí!

macOS recordará tu decisión y nunca volverá a preguntar.

### Método 2: Desde Configuración del Sistema

Si el Método 1 no funciona (a veces pasa en macOS Ventura+):

1.  Intenta abrir la app normalmente (doble clic) - saldrá el error
2.  Ve inmediatamente a **Configuración del Sistema** → **Privacidad y Seguridad**
3.  Baja hasta la sección **"Seguridad"**
4.  Verás un mensaje: *"Se bloqueó collage_maker..."*
5.  Haz clic en **"Abrir de todas formas"**
6.  Confirma con tu contraseña o Touch ID

### Método 3: Por Terminal (si nada más funciona)

Abre la Terminal y escribe:

```bash
cd ~/Downloads  # o donde esté la app
xattr -cr collage_maker.app
```

Luego intenta abrir la app normalmente.

## ¿Por qué pasa esto?

Las apps necesitan una "firma digital" de Apple (cuesta $99/año). Como esta es gratuita y para uso personal, no tiene firma.

**La app es 100% segura** - está construida automáticamente desde el código fuente en GitHub. Puedes revisar todo el código si quieres verificarlo.
