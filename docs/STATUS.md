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

Se añadió `eos-serviced`, que calcula un orden de arranque determinista para los servicios propios de EOS. También se añadió `eos_boot_config.py`, que genera entradas normales y de recovery para UEFI/GRUB a partir de un kernel y un initramfs explícitos. La validación se hizo con un marcador de kernel porque el sandbox no contiene una imagen Linux EOS compilada.

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
| Generador de configuración de bootloader | PASS con kernel marcador |
| Ejecución de una app comercial `.ipa` | No implementada |
| ISO arrancable completa | No implementada |
| Soporte universal de Swift/UIKit/SwiftUI | No implementado |

## Próximo hito

El siguiente hito será trasladar el gestor de paquetes y recovery a servicios C++ de EOS, añadir sandbox por proceso y construir un bootloader/instalador de PC que produzca una imagen GPT `.img` con un kernel Linux real configurado para EOS. La ejecución de `.ipa` seguirá limitada a análisis y a binarios de prueba autorizados hasta disponer de un runtime compatible verificable.
