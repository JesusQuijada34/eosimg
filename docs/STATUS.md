# Estado de desarrollo EOS

**Fecha:** 23 de agosto de 2026  
**Versión:** 0.1 experimental

## Hito completado

EOS ya tiene una especificación inicial que adopta el modelo “Linux como kernel, plataforma propia encima”. Se definieron las capas EOS Linux Kernel Base, EOS Device Abstraction Layer, demonios nativos, EosRuntime, EOSKit, shell Qt 6, EosLang, gestor `.eapp` y el runtime experimental EACR para `.ipa`.

Se implementó y probó una herramienta oficial Python que empaqueta directorios en `.eapp`, guarda un manifiesto JSON canónico con identidad, autor, licencia, API, versión mínima de EOS, recursos, permisos y dependencias, comprime un payload tar, verifica SHA-256, firma Ed25519 y extrae sin permitir enlaces ni rutas de escape. La prueba de firma, instalación y manipulación terminó correctamente.

Se implementaron dos componentes C++: `eos-init`, que representa la secuencia de arranque en modo `--dry-run`, y `eos-phone-shell`, una interfaz original de teléfono construida con Qt 6. CMake compila ambos binarios y el shell inicia en modo offscreen sin fallar.

Se implementó un inspector pasivo de `.ipa` que abre el ZIP, localiza `Payload/*.app`, lee `Info.plist` y reconoce cabeceras Mach-O arm64. Se verificó con un `.ipa` sintético creado para pruebas. El inspector no ejecuta, modifica, resigna, descifra ni parchea aplicaciones.

Se añadió EosLang 0.1 con compilador a bytecode EOSBC y runtime de referencia. También se añadió un runner preliminar que separa EOS nativo del modo de ejecución en Windows/Linux mediante una VM explícita; valida que el kernel y el initramfs sean proporcionados por el usuario y ofrece `--dry-run`.

Se añadió una política de ABI que rechaza `.deb`, AppImage y ELF Linux de usuario desde el launcher oficial. Se añadió recovery con `wipe-cache`, `wipe-data` y `factory-reset`, con confirmación obligatoria y raíz explícita. Se definieron y probaron contenedores preliminares `.edisk` para dispositivos y `.img` para PC; todavía no son imágenes GPT/raw arrancables.

Se añadió `eos-serviced`, que calcula un orden de arranque determinista para los servicios propios de EOS. También se añadió `eos_boot_config.py`, que genera entradas normales y de recovery para UEFI/GRUB a partir de un kernel y un initramfs explícitos. La validación inicial se hizo con un marcador de kernel; después se instaló un kernel Linux real de desarrollo en el sandbox y el initramfs de EOS arrancó correctamente dentro de QEMU. La imagen sigue siendo experimental y no se publica como release.

Se añadió `eos-sandbox`, que transforma los permisos de `.eapp` en una política declarativa de aislamiento con no-new-privileges, límites de memoria/CPU, montajes privados y acceso a dispositivos denegado por defecto. Se añadió `eos-supervise`, un supervisor C++ que restringe el lanzamiento a servicios internos `eos-*`, aplica no-new-privileges y límites iniciales de memoria/CPU; la integración completa de namespaces, seccomp y cgroups queda pendiente.

Se añadió `eos_gpt_image.py`, que genera una imagen raw local de 256 MiB con tabla GPT y particiones EOS-BOOT, EOS-SYSTEM, EOS-RECOVERY, EOS-DATA y EOS-CACHE. `sgdisk --verify` confirma que el layout es válido; la imagen aún no está poblada con un bootloader/producto final y no se publica.

El shell Qt 6 incorpora un teclado virtual táctil de demostración con entrada de texto, filas QWERTY y tecla de espacio. El componente compila y arranca en modo offscreen; la internacionalización, predicción, layouts y motor IME quedan pendientes.

Se añadió `build_bootable_iso.sh`, que construye localmente una ISO El Torito/GRUB con el kernel Linux real de desarrollo, initramfs EOS y entradas normal/recovery. La ISO arranca como artefacto de desarrollo y no se publica como release.

Se añadió `populate_gpt_image.sh`, que crea una ESP FAT32 dentro de la imagen GPT y copia un GRUB UEFI standalone, el kernel y el initramfs EOS. `sgdisk --verify` confirma el layout después de poblarla. La imagen GPT ya arranca por UEFI en OVMF y llega al initramfs de EOS. El poblador ahora crea una partición `EOS-SYSTEM` ext4 con `eos-release` y metadatos mínimos del userland; la prueba UEFI sigue pasando. Sigue siendo una imagen de desarrollo: todavía faltan el userland persistente completo, un bootloader EOS propio y pruebas sobre hardware físico.

Se añadió `eos-inputd`, un servicio C++ con protocolo `eos-touch-0.1` que clasifica taps y deslizamientos básicos. La autoprueba pasa sin hardware físico; la integración posterior utilizará dispositivos de entrada del kernel mediante EDAL, sin exponer directamente sus eventos a las aplicaciones.

## Resultados de pruebas

| Prueba | Resultado |
|---|---|
| Empaquetar `.eapp` | PASS |
| Verificar hash y extraer `.eapp` | PASS |
| Compilar con CMake y Qt 6 | PASS |
| Arrancar `eos-init --dry-run` | PASS |
| Iniciar shell Qt 6 offscreen | PASS |
| Analizar `.ipa` sintético | PASS |
| Firma e instalación `.eapp` | PASS |
| Rechazo de `.eapp` manipulado | PASS |
| Compilación y ejecución EosLang | PASS |
| Validación del runner VM en `--dry-run` | PASS |
| Rechazo de `.deb` y ELF Linux | PASS |
| Recovery con confirmación | PASS |
| Contenedores `.edisk` y `.img` de desarrollo | PASS |
| Gestor de servicios EOS | PASS |
| Generador de configuración de bootloader | PASS con kernel real de desarrollo |
| Arranque initramfs + kernel Linux real en QEMU | PASS |
| Generador de política de sandbox | PASS |
| Permisos sandbox para IA, descargas, multimedia, notificaciones y ventanas | PASS; enforcement fuerte pendiente |
| Teclado virtual Qt 6 | PASS en shell offscreen |
| Imagen raw GPT `.img` de desarrollo | PASS |
| ISO GRUB/El Torito de desarrollo | PASS |
| ESP FAT32 + GRUB UEFI en `.img` GPT | PASS |
| Arranque UEFI de `.img` GPT en OVMF | PASS |
| Población de `EOS-SYSTEM` ext4 | PASS |
| Verificador GPT/UEFI de `.img` | PASS sin montar ni escribir |
| Generador de proyectos SDK EOS | PASS |
| Ejecución de `.eapp` firmado mediante EOSBC | PASS |
| OOBE Qt 6 con flujo de setup | PASS en modo offscreen |
| OOBE persistente/reanudable con `oobe-state.json` | PASS en root temporal |
| Servicio de entrada táctil | PASS en autoprueba |
| Registro de APIs EOS | PASS |
| Stub local de IA/asistente | PASS |
| Especificación de selección de modelos HF locales | Documentada |
| Protección de licencia/revisión/revisión fijada | Documentada |
| Selector de modelos por RAM/arquitectura | PASS sin descarga |
| Planificador de asistente local offline | PASS sin ejecución |
| Build real `llama.cpp` CPU en revisión fijada | PASS; binario no versionado |
| Adaptador EOS `llama.cpp` offline con hash obligatorio | PASS en plan-only |
| Preflight GGUF: magic, versión, tamaño y SHA-256 | PASS con fixture; sin inferencia |
| Descarga autorizada Qwen2.5 0.5B Q4_K_M | PASS; revisión/licencia/hash fijados |
| Inferencia real `llama.cpp` offline | PASS; CPU, contexto 512, GPU layers 0 |
| Requisitos y ruta de build Gecko | Documentados; motor pendiente |
| Servicio `eos-immersived` de notch/ondas/voz | PASS en autoprueba |
| Contrato `eos-browserd` y descargas dry-run | PASS sin motor web |
| Bridge Gecko con perfil/URI aislados | PASS en plan-only |
| `eos-browserd` C++ con sesión Gecko y URI policy | PASS en autoprueba |
| `eos-policyd` para llama.cpp/Gecko/permisos | PASS en autoprueba |
| Preparador de build Gecko con recursos/revisión fijada | PASS con fixture |
| Cola de descargas y verificación SHA-256 | PASS sin red |
| EOS Notes: EosLang → EOSBC → `.eapp` firmado | PASS temporal |
| Catálogo de apps fuente y validación de manifiestos | PASS |
| Servicio `eos-mediad` de foto/audio/vídeo | PASS en autoprueba |
| Registro `eos-launcherd` de launchers `.eapp` | PASS en autoprueba |
| Perfil local EOS ID + temas eRalf/eJairo | PASS sin sincronización |
| Swimmer Time: snapshot/restauración con SHA-256 | PASS en root temporal |
| eFace: enrolamiento seguro sin biometría real | PASS en stub local |
| Índice ePhoto/Carrousel de medios local | PASS sin upload/IA |
| Servicio `eos-photod` ePhoto/Carrousel/Editor | PASS en autoprueba |
| Servicio BlinkE + safe area/notch/window API | PASS en autoprueba |
| Validación integral de build y pruebas | PASS |
| Validación final de servicios, `git diff --check` y releases | PASS; `no releases found` |
| Arquitectura de plataforma EOS consolidada | Documentada |
| Presets CMake + `eos-build` source-only | PASS |
| Grafo declarativo completo de servicios EOS | PASS; sin ciclos |
| Auditoría de apps fuente integrada en `eos-build` | PASS; catálogo generado |
| `eos-logd` logging estructurado JSONL | PASS en root temporal |
| `eos-storaged` roots lógicos y escritura atómica | PASS en root temporal |
| `eos-sessiond` sesión local y entrega post-OOBE | PASS en root temporal |
| Validación `.edisk` por perfil y arquitectura | PASS sin flasheo |
| Supervisor C++ de procesos y límites iniciales | PASS |
| Supervisor C++ endurecido: dumpability, nofile y nproc | PASS en dry-run |
| Ejecución de una app comercial `.ipa` | No implementada |
| Ejecución de un `.eapp` EOSBC propio | PASS |
| ISO arrancable completa | No implementada |
| Soporte universal de Swift/UIKit/SwiftUI | No implementado |

## Próximo hito

La integración de `llama.cpp` ya tiene una inferencia real offline con Qwen2.5-0.5B Q4_K_M; el GGUF permanece fuera de Git en `build/models`. El contrato inicial de navegador ya existe, pero todavía no es un navegador web: falta seleccionar y compilar un backend Gecko permitido, integrar perfiles/procesos y añadir una UI Qt 6. La red y las descargas permanecen desactivadas en el prototipo.

La primera utilidad fuente, `apps/eos-notes`, ya valida el flujo EosLang → EOSBC → `.eapp` firmado en un directorio temporal. El paquete generado, sus claves de prueba y sus imágenes no se versionan.

El siguiente hito será trasladar el gestor de paquetes y recovery a servicios C++ de EOS, añadir sandbox por proceso y reemplazar el `eos-init` de demostración por un supervisor de procesos real. Después se construirá un bootloader/instalador de PC que produzca una imagen GPT `.img` con un kernel Linux configurado para EOS. La ejecución de `.ipa` seguirá limitada a análisis y a binarios de prueba autorizados hasta disponer de un runtime compatible verificable.

Se añadió `eos-update.py` con slots A/B, staging atómico, activación en el siguiente arranque, confirmación de éxito y rollback. La prueba local completó staging en B, marcó el slot como exitoso y volvió a A mediante rollback. El gestor todavía opera sobre un directorio de desarrollo y no modifica variables UEFI ni discos físicos.
