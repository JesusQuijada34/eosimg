# Etternhall Operating System — arquitectura de plataforma

## Principio central

EOS usa Linux como **motor de bajo nivel**: kernel, controladores, memoria virtual, procesos, interrupciones, almacenamiento elemental y redes. Linux no define la experiencia de usuario ni la ABI pública de aplicaciones. EOS expone su propio runtime, permisos, servicios, shell, paquetes y ciclo de actualización.

> Un binario ELF Linux genérico no es una aplicación EOS. Una aplicación EOS debe entrar por el contrato `.eapp`, ser validada por la herramienta oficial, usar APIs EOS y ejecutarse a través de EOSBC/EosRuntime o de un componente del sistema explícitamente firmado.

## Capas congeladas

| Capa | Responsabilidad | ABI pública |
|---|---|---|
| EOS Linux Kernel Base | procesos, memoria, drivers, VFS, red y energía de bajo nivel | no expuesta directamente a apps |
| EDAL | hardware, input, display, audio, cámara, sensores y almacenamiento | C++/IPC EOS |
| EOS Core | init, supervisor, servicios, políticas, logs y sesiones | `eos-*` + eventos EOS |
| EOS Runtime | EosLang, EOSBC, permisos y ciclo de vida `.eapp` | EOSBC/EosLang |
| EOSKit | filesystem lógico, ventanas, notificaciones, multimedia, IA y red | headers/API EOS versionados |
| EOS Shell | shell Qt 6, compositor, launchers, OOBE, notch y panel inmersivo | Qt 6 interno + EOSKit |
| Apps EOS | Notes, Browser, ePhoto, Editor, Media, juegos y utilidades | `.eapp` firmado |
| Recovery/Update | wipe, backup, A/B, rollback e imágenes | herramientas de mantenimiento EOS |

## Fronteras de procesos

Los servicios del sistema se ejecutan bajo nombres `eos-*` y no deben exponerse como comandos Linux de usuario. `eos-supervise` controla el ciclo de vida; `eos-policyd` aplica el principio deny-by-default; `eos-serviced` determina dependencias; y cada servicio tiene un protocolo versionado y una autoprueba.

El navegador Gecko, llama.cpp, cámaras, audio y futuras apps con contenido no confiable vivirán detrás de procesos separados. El shell Qt 6 no debe cargar directamente páginas web ni modelos; recibe eventos normalizados. Las aplicaciones no reciben acceso directo a `/proc`, dispositivos, sockets del kernel ni rutas físicas del sistema.

## Contratos de datos

| Objeto | Formato/ubicación | Regla |
|---|---|---|
| Aplicación | `.eapp` v2 | firma Ed25519, identidad, API, permisos y hashes |
| Código de aplicación | EOSBC/EosLang | no ELF Linux genérico |
| Modelo IA | GGUF + manifiesto | revisión HF fijada, licencia, tamaño, SHA-256 y RAM |
| Perfil | `eos://profiles/<id>` | identidad local; sincronización opt-in |
| Medios | `eos://media/*` | índice local; upload opt-in |
| Descarga | `eos://downloads/*` | URL, destino lógico, estado y hash |
| Snapshot | `swimmer-time/<stamp>` | manifiesto verificable y restauración confirmada |
| Imagen PC | `.img` | GPT con ESP/system/recovery/data/cache |
| Firmware dispositivo | `.edisk` | perfil, arquitectura y firma antes de aplicar |

## Orden de construcción

1. **Base ejecutable:** CMake, toolchain, logging, configuración y pruebas.
2. **Core:** init, servicios, supervisor, políticas, IPC y sesiones.
3. **Persistencia:** perfiles, almacenamiento lógico, recovery, actualización y logs.
4. **Runtime:** EosLang, EOSBC, SDK, `.eapp`, sandbox y trusted keys.
5. **Shell:** Qt 6, compositor, input táctil, ventanas, safe areas, OOBE y accesibilidad.
6. **Motores:** llama.cpp local y Gecko interno detrás de bridges.
7. **Apps:** Browser, Notes, Media, ePhoto, Editor, launchers, juegos y utilidades.
8. **Dispositivos:** imágenes de desarrollo, bootloader, instalador y hardware targets.

## Estado de realidad

Los contratos, varios servicios, el OOBE persistente, `.eapp`, EOSBC, `llama.cpp` CPU con Qwen2.5 0.5B GGUF y bridges iniciales de Gecko ya tienen pruebas locales. Todavía no existe un producto EOS de producción: faltan sandbox fuerte por proceso, compositor completo, almacenamiento persistente de dispositivo, build Gecko interna, integración de audio/cámara, UI final y pruebas sobre hardware.

La política del repositorio continúa siendo **source-only**: se suben código y documentación; los modelos, claves, `.eapp`, `.img`, `.edisk` y builds permanecen ignorados; no se crean releases hasta que el usuario lo solicite expresamente.
