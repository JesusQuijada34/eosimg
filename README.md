# Etternhall Operating System (EOS)

EOS es una plataforma experimental construida sobre el kernel Linux, con userland, servicios, shell y formato de aplicaciones propios. El repositorio actual contiene una base compilable del sistema: servicios C++ de core/EDAL, shell Qt 6, OOBE persistente, runtime EosLang/EOSBC, apps fuente `.eapp`, IA local con `llama.cpp` y contratos de Browser/Gecko. Todavía no es una imagen de producción ni un runtime completo para `.ipa`.

## Estado actual

La versión 0.1 define una arquitectura por capas similar en organización a AOSP, pero con nombres, contratos y componentes propios. Se ha implementado un formato `.eapp` versionado con manifiesto JSON canónico, identidad de bundle, publisher, autor, licencia, versión, API de EosLang, versión mínima de EOS, entrypoint, targets, icono, splash, documentación, permisos, dependencias, payload comprimido, hash SHA-256 y firma Ed25519 opcional. Un registro de APIs EOS valida que la aplicación solicite una API conocida y versionada.
 La herramienta solo empaqueta, inspecciona y extrae; nunca ejecuta contenido automáticamente.

## Estructura

| Ruta | Propósito |
|---|---|
| `docs/EOS_SPEC.md` | Especificación de arquitectura |
| `tools/eapp.py` | Empaquetador, firmador, instalador e inspector `.eapp` |
| `tools/eos_launch.py` | Frontera de ejecución: solo `.eapp` firmado |
| `tools/eos_recovery.py` | `wipe-cache`, `wipe-data`, `factory-reset` |
| `tools/eos_image.py` | Contenedores `.edisk` y `.img` de desarrollo |
| `tools/eos_boot.py` | Inspector y planificador de boot |
| `tools/eos_runner.py` | Runner de VM para Windows/Linux |
| `tools/eos_sandbox.py` | Política de permisos y sandbox |
| `tools/eos_build.py` | Motor de compilación coordinado y manifiesto source-only |
| `tools/eos_service_graph.py` | Grafo declarativo de servicios |
| `tools/eos_llama_backend.py` / `tools/eos_gguf_validate.py` | Backend local offline y preflight GGUF |
| `tools/eos_gecko_bridge.py` / `tools/eos_gecko_prepare.py` | Bridge y preparación del backend Gecko |
| `tools/eos_api.py` | Registro y comprobación de APIs EOS |
| `tools/ipa_compat.py` | Matriz pasiva de compatibilidad IPA/Mach-O |
| `tools/eoslangc.py` / `tools/eosrun.py` | Compilador y runtime EosLang |
| `src/` | Servicios C++ core/EDAL, IA, Browser, multimedia, seguridad y shell Qt 6 |
| `apps/eos-browser/` | Primera app fuente Browser con backend Gecko declarado |
| `tests/` | Pruebas del formato y de los servicios |

## Uso del prototipo `.eapp`

```bash
python3 tools/eapp.py keygen build/eos-key.pem
python3 tools/eapp.py pack demo-app demo.eapp \
  --name com.etternhall.demo --version 0.1.0 \
  --entrypoint bin/demo --target eos-x86_64 \
  --publisher 'Etternhall Labs' --author 'EOS Team' \
  --license Apache-2.0 --api elang-0.1 --min-eos '>=0.1.0' \
  --permission network.client --signing-key build/eos-key.pem

python3 tools/eapp.py inspect demo.eapp
python3 tools/eapp.py extract demo.eapp extracted-demo
python3 tools/eos_launch.py demo.eapp --dry-run
```

El formato está pensado para evolucionar hacia un almacén de claves de confianza, múltiples arquitecturas y actualizaciones atómicas. La herramienta oficial puede ser la única vía soportada de instalación, pero el payload debe poder descifrarse o mapearse durante la ejecución. La compresión, el cifrado en reposo y la ofuscación elevan el coste de extracción, pero no hacen que el software sea imposible de analizar en un equipo controlado por el usuario.

## Recovery e imágenes

Las operaciones destructivas requieren una raíz explícita y la frase de confirmación exacta:

```bash
python3 tools/eos_recovery.py wipe-cache --root ~/.eos --confirm 'ERASE EOS DATA'
python3 tools/eos_recovery.py wipe-data --root ~/.eos --confirm 'ERASE EOS DATA'
python3 tools/eos_recovery.py factory-reset --root ~/.eos --confirm 'ERASE EOS DATA'
```

`.edisk` se reserva para perfiles de dispositivos y `.img` para PC. Ya existe una imagen GPT de desarrollo arrancable en QEMU/OVMF, pero no es un firmware de producción ni se publica. `eos_boot.py` genera planes sin modificar dispositivos. `eos_sandbox.py` produce una política declarativa; el supervisor aplica actualmente no-new-privileges y límites iniciales, mientras namespaces, seccomp y cgroups siguen pendientes. `eos_build.py` coordina la compilación, audita apps fuente y escribe un manifiesto local con la publicación desactivada.

## Estado de los motores

Hi Eaid ya puede ejecutar una inferencia real offline con un Qwen2.5-0.5B GGUF verificado, pero la captura de micrófono y TTS todavía están detrás de permisos y contratos de hardware. EOS Browser ya tiene UI fuente, `eos-browserd`, política de red y bridge Gecko, pero el motor Gecko compilado para EOS todavía requiere un checkout Mozilla y un entorno con al menos decenas de GB libres. La ejecución de `.ipa` seguirá limitada a análisis y a binarios de prueba autorizados.

Los siguientes hitos son convertir los contratos de servicio en IPC real, completar namespaces/seccomp/cgroups, integrar una build Gecko interna, unir el compositor Qt 6 con el backend de ventanas y llevar el bootloader/instalador de PC a hardware de prueba.

## Política de publicación

El repositorio público contiene exclusivamente código fuente, especificaciones y pruebas de desarrollo. **No se publicarán releases ni imágenes oficiales `.img`/`.edisk` todavía**. Las imágenes y paquetes generados localmente sirven para pruebas internas hasta que el bootloader, userland, sandbox, recovery y APIs de EOS alcancen una versión estable.

El proyecto seguirá tratando `.ipa` únicamente mediante análisis pasivo y pruebas autorizadas. `ipa_inspect.py` y `ipa_compat.py` leen ZIP, `Info.plist` y cabeceras/dependencias Mach-O, pero nunca ejecutan, resignan, descifran ni parchean aplicaciones. No se incluirán claves privadas, componentes propietarios de Apple ni mecanismos para evadir firmas, DRM o controles de acceso.
