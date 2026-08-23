# EOS OOBE y sistema visual

## Objetivo

El OOBE de Etternhall Operating System será una experiencia de primer arranque limpia, amable y breve. Tomará como referencia la claridad de los asistentes modernos de escritorio, incluido Windows 11, pero no copiará recursos gráficos, textos ni identidad de Microsoft o Apple.

## Flujo de primer arranque

| Paso | Pantalla | Resultado |
|---:|---|---|
| 1 | Bienvenida | Selección de idioma y accesibilidad |
| 2 | Región y teclado | Localización, formato y layout táctil |
| 3 | Red | Wi-Fi/Ethernet; puede omitirse |
| 4 | EOS ID | Crear, iniciar sesión u omitir temporalmente |
| 5 | Privacidad | Diagnóstico, ubicación, cámara, micrófono y personalización |
| 6 | Apariencia | Tema claro/oscuro, colores y orientación |
| 7 | Asistente local | Selección de modelo según RAM; descarga opcional |
| 8 | Recuperación | Crear punto inicial y explicar wipe data/cache |
| 9 | Finalización | Resumen, aceptación y apertura del shell EOS |

Cada pantalla tendrá un título, una explicación de una o dos líneas, un control principal y una acción secundaria. El usuario nunca quedará atrapado en una pantalla de red o de cuenta.

## Lenguaje visual

EOS usará superficies planas, esquinas moderadas, sombras discretas, tipografía legible y botones de alto contraste. Los botones serán simples y minimalistas: una acción primaria rellena, una acción secundaria plana y una acción de retorno. No se usarán gradientes intensos ni iconos ambiguos.

| Elemento | Regla EOS |
|---|---|
| Fondo | `#101522` oscuro o `#F6F8FF` claro |
| Superficie | plana, contraste suave y borde fino |
| Radio | 8–14 px según control |
| Botón primario | relleno azul EOS, texto claro |
| Botón secundario | transparente con borde o texto |
| Foco | anillo visible para teclado y accesibilidad |
| Touch target | mínimo 44 px en modo táctil |
| Animación | 120–220 ms, sin movimiento obligatorio |
| Navegación | Atrás, continuar, omitir y cancelar siempre consistentes |

## Arquitectura

`eos-oobe` será una aplicación del sistema con permisos para configuración, red, entrada, almacenamiento inicial y EOS ID. Guardará el progreso en un estado transaccional; si el equipo se apaga, el siguiente arranque podrá continuar sin repetir pasos ya confirmados. La configuración se validará antes de activar el shell normal.

La implementación inicial usará Qt 6 Widgets para compartir componentes con el shell existente. Una fase posterior podrá migrar partes a Qt Quick/QML si se necesita composición táctil más fluida.

## Principios de seguridad

El OOBE no descargará modelos, extensiones, launchers ni aplicaciones silenciosamente. Las opciones que implican red, cuenta, cámara, micrófono, ubicación o sincronización mostrarán consentimiento claro. El restablecimiento de fábrica tendrá una pantalla de confirmación separada y nunca se ejecutará por una pulsación accidental.
