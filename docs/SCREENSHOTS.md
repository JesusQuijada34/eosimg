# Capturas visuales EOS

Estas capturas se generan localmente durante el desarrollo y permanecen fuera de Git hasta que exista una matriz de release aprobada.

| Archivo | Estado representado | Origen | Dimensiones |
|---|---|---|---:|
| `build/captures/eos-shell-home.png` | Pantalla principal del shell EOS con launcher, dock y teclado | `eos-phone-shell --capture` | 430×860 |
| `build/captures/eos-studio.png` | EOS Studio con explorador, actividades, canvas, tabs EosLang/Triggers/EOS CSS, paleta e inspector | `eos-studio --capture` | 1280×780 |
| `build/captures/eos-notes-home.png` | Actividad principal `notes.home` con lista y acción de nueva nota | `eos-app-preview --capture` | 430×820 |
| `build/captures/eos-notes-editor.png` | Actividad secundaria `notes.editor` con back, editor y guardar | `eos-app-preview --capture-activity notes.editor` | 430×820 |

## Alcance honesto

Las capturas de `eos-phone-shell`, `eos-studio` y `eos-app-preview` son salidas reales de programas Qt 6 compilados en el sandbox. `eos-app-preview` es un preview visual de las actividades Notes y no el compositor de producción del sistema. No debe confundirse con soporte de hardware físico, un motor Gecko integrado o enforcement final de sandbox.
| `build/captures/eos-oobe-welcome.png` | OOBE inicial: bienvenida, selector de idioma, progreso y acciones Atrás/Omitir/Continuar | `eos-oobe --capture` | 760×520 |

La captura OOBE fue inspeccionada visualmente y corresponde al primer paso real del flujo Qt 6. El progreso, el selector de idioma y los botones pertenecen al prototipo ejecutable; la configuración persistente se guarda en un root EOS de desarrollo.
| `build/captures/etternhall-desktop.png` | Escritorio convencional con panel superior, launcher, búsqueda, selector de workspaces, ventanas Archivos/Notas y barra de tareas | `eos-phone-shell --capture` | 1280×800 |

La captura demuestra el cambio desde el shell de teléfono a un escritorio Qt 6 de desarrollo. Las ventanas son contenedores del shell; las pantallas internas de Notes siguen siendo responsabilidad de `eos-activityd`.
| `build/captures/etternhall-desktop-workspaces.png` | Escritorio convencional con selector funcional de escritorios 1, 2 y 3; ventanas visibles en el workspace activo | `eos-phone-shell --capture` | 1280×800 |
