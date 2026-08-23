# EOS Browser: arquitectura inicial

## Estado

Este documento define la ruta técnica para `eos-browserd`. EOS no empaquetará un binario ELF Linux de escritorio como si fuera una aplicación nativa: el navegador será un componente EOS integrado mediante una adaptación propia del motor y una interfaz `.eapp`/servicio firmada.

## Decisión de integración

Mozilla documenta **GeckoView** como una biblioteca autocontenida para incrustar Gecko y como una opción orientada a crear navegadores y aplicaciones; su guía pública de integración está centrada en Android y requiere el artefacto de GeckoView, Java 17 y una sesión/runtime de Gecko.[^1] La documentación general de Mozilla describe Gecko como un conjunto amplio que incluye parsing HTML, networking, JavaScript, IPC, DOM, abstracciones de widgets y gráficos.[^2]

Para EOS, GeckoView se tratará como referencia de API y arquitectura, no como una orden de copiar una aplicación Android. La primera entrega será un contrato `eos-browserd` con perfiles, navegación, descargas y aislamiento; la adaptación real del motor requerirá una build controlada de Mozilla/Gecko para el target EOS o un backend oficialmente soportado. No se declarará compatibilidad hasta tener una build reproducible.

## Contrato previsto de `eos-browserd`

| Área | Contrato EOS | Estado |
|---|---|---|
| Navegación | `open(uri)`, `back()`, `forward()`, `reload()` | Diseño |
| Perfiles | perfil persistente y caché separada | Diseño |
| Descargas | cola con destino EOS, hash y cancelación | Diseño |
| Procesos web | proceso de contenido aislado por sitio cuando sea posible | Diseño |
| Permisos | cámara, micrófono, ubicación y almacenamiento con consentimiento | Diseño |
| UI | shell Qt 6, sin depender de widgets de Firefox de escritorio | Diseño |
| Extensiones | superficie futura limitada a APIs revisadas | Pendiente |

La separación por procesos y la comunicación asíncrona son principios relevantes: la documentación de Gecko explica que Firefox es multiproceso y que Fission asigna procesos de contenido por sitio como una mitigación de riesgos de aislamiento.[^2] EOS debe traducir ese principio al supervisor propio, con permisos mínimos, límites de recursos y un perfil aislado por aplicación o pestaña cuando el backend lo permita.

## Licencia y marca

Mozilla informa que el software ejecutable distribuido por el proyecto, incluyendo Firefox, se ofrece bajo MPL, pero también indica que sus nombres, logotipos y marcas tienen restricciones separadas.[^3] Por tanto, EOS podrá estudiar y adaptar código conforme a sus licencias aplicables, conservar avisos y publicar las modificaciones exigidas, pero no usará la marca Firefox para una build no autorizada ni copiará su identidad visual. El nombre de producto será provisionalmente **EOS Browser** hasta resolver branding y distribución.

## Descargas y multimedia

El gestor de descargas debe recibir únicamente tareas originadas por el navegador o por una aplicación EOS con permiso explícito. Cada tarea tendrá URI, destino lógico, tamaño esperado si está disponible, hash opcional, estado y motivo de cancelación. La reproducción de vídeo y audio debe pasar por APIs multimedia de EOS; no se implementará una función para evadir DRM, restricciones de acceso o términos de plataformas. La aplicación de YouTube, si se crea, usará superficies web autorizadas y no descargará contenido protegido por mecanismos no autorizados.

## Próxima implementación segura

La siguiente entrega puede ser un `eos-browserd` de contrato sin motor web: acepta comandos locales de planificación, devuelve estados de navegación y genera una cola de descarga en modo dry-run. Después se añadirá un backend Gecko aprobado para el dispositivo, pruebas de procesos/perfiles y una UI Qt 6. Hasta entonces, el estado es **diseño; no navegador funcional**.

## Referencias

[^1]: [Mozilla Firefox Source Docs — Getting Started with GeckoView](https://firefox-source-docs.mozilla.org/mobile/android/geckoview/consumer/geckoview-quick-start.html) y [GeckoView](https://mozilla.github.io/geckoview/).
[^2]: [Mozilla Firefox Source Docs — Gecko](https://firefox-source-docs.mozilla.org/overview/gecko.html).
[^3]: [Mozilla Foundation — Licensing & Trademarks](https://www.mozilla.org/en-US/foundation/licensing/).
