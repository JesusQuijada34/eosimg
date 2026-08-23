# EOS SDK y EOS Studio

## Objetivo

EOS Studio será el entorno oficial para crear una aplicación `.eapp` desde cero sin editar manualmente cada archivo. La herramienta estará construida sobre Qt 6 y usará Python para generación de proyectos, validación, preview, compilación, pruebas y empaquetado. Las apps creadas seguirán siendo aplicaciones EOS: EosLang/EOSBC, EOS UI, actividades, triggers, permisos YAML, metadata JSON y firmas MF.

El SDK puede crecer hasta varios gigabytes cuando incorpore toolchains, documentación offline, templates, assets, runtimes de preview, símbolos de depuración y toolchains por arquitectura. El tamaño del SDK no cambia el contrato ligero del `.eapp` distribuido.

## Componentes

| Componente | Responsabilidad |
|---|---|
| `eos-sdk` | Crear proyectos, añadir actividades, controles, recursos y librerías |
| `eoslangc` | Compilar EosLang a EOSBC y validar handlers |
| `eos-ui-check` | Validar layouts, bindings, estilos y acciones EOS UI |
| `eos-triggerc` | Validar triggers YAML contra actividades y handlers |
| `eos-preview` | Renderizar una UI y simular navegación/touch/swipe sin hardware |
| `eos-debug` | Ejecutar EOSBC con eventos, logs, breakpoints futuros y trazas |
| `eapp` | Empaquetar, generar MF, firmar, inspeccionar e instalar en un prefix EOS |
| `EOS Studio` | Frontend visual Qt 6 para orquestar todos los componentes |

## Proyecto creado por el SDK

```text
my-app/
├── eapp.json
├── src/main.elang
├── ui/activities.yml
├── ui/home.eosui
├── ui/styles.eos.css
├── ui/animations.eos.yml
├── policy/permissions.yml
├── policy/triggers.yml
├── resources/
├── docs/README.md
└── LICENSE
```

`eapp.json` contiene metadata y la actividad principal. `activities.yml` permite editar actividades sin convertir la metadata en un archivo ilegible. EOS Studio mantiene ambos documentos sincronizados y muestra los errores de referencia inmediatamente.

## Superficie visual de EOS Studio

La ventana principal tendrá un explorador de proyecto, una paleta de controles, un canvas de preview, un inspector de propiedades, un editor de código y una consola de build/debug. El canvas permite seleccionar una actividad, arrastrar controles, editar bindings y conectar acciones; el inspector modifica el documento EOS UI, no genera widgets Qt arbitrarios dentro del `.eapp`.

EOS CSS será un lenguaje de estilos propio, inspirado en la ergonomía de CSS pero con propiedades EOS explícitas como `safe-area`, `material`, `focus-ring`, `touch-target`, `elevation` y `notch-avoidance`. No será una promesa de compatibilidad con CSS web. Las animaciones declararán estados, duración, easing y eventos del lifecycle; el runtime decidirá si puede ejecutarlas según el display y la política de energía.

## Actividades, triggers y depuración

El diseñador selecciona `notes.home` o `notes.editor` desde un selector de actividad. Las acciones de controles se enlazan a handlers EosLang o a rutas EOS Navigation. Los triggers YAML se muestran con su actividad, entrega (`resumed-only`, `foreground` o `background-authorized`) y permisos relacionados.

El modo Preview ejecuta un runtime de referencia aislado. Puede simular `app.launch`, `ui.action`, `touch`, `gesture.swipe-left`, rotación, notch y back. La consola separa logs de UI, lifecycle, navegación, permisos y errores de EosLang. Esto no sustituye las pruebas del compositor, hardware o sandbox de producción.

## Qt 6 y Python

Qt 6 proporciona la interfaz de EOS Studio y, en el sistema EOS, la base del shell y de la composición UI. Python es una herramienta de desarrollo: orquesta validadores, genera archivos, lanza builds y produce informes. Un `.eapp` no depende de una instalación Linux de Python ni se convierte en una app Qt genérica; el runtime EOS ejecuta EOSBC y las APIs EOS.

## Seguridad

EOS Studio nunca incluirá claves privadas dentro de un proyecto por defecto. El modo de firma pide una clave externa o un almacén confiable. El preview no concede permisos reales, no abre `/dev/input`, no captura cámara/micrófono y no descarga dependencias automáticamente. La depuración mostrará los límites del runtime en lugar de ocultarlos.
