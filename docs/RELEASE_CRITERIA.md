# Criterios de finalización y release EOS

EOS no se considerará terminado solo porque compile. Antes de preparar imágenes públicas deben cumplirse los criterios de esta matriz y cada limitación debe aparecer en las notas de versión.

| Área | Criterio de release | Estado actual |
|---|---|---|
| Arquitectura | Linux limitado a kernel/drivers/procesos; ABI, shell y apps EOS propios | Parcialmente cumplido |
| Build | CMake y `eos_build.py` reproducibles para targets declarados | Cumplido en desarrollo |
| Apps | `.eapp` v3 con JSON, YAML, UI, EOSBC y MF verificables | Cumplido en prototipo |
| EosLang | Compilador y runtime compatibles con versión de bytecode declarada | EOSBC 2 experimental |
| Activities | Actividad principal, navegación, back stack y restauración | Cumplido en preview local |
| UI | EOS Studio, UI declarativa, estilos, animaciones y preview | Cumplido en preview Qt 6 |
| Browser | `eos-browserd` con Gecko real integrado, perfil aislado y proceso controlado | Pendiente; bridge plan-only |
| IA | Modelo local fijado, hash, licencia, consentimiento y modo offline | Inferencia llama.cpp cumplida; daemon aún contractual |
| Multimedia | Audio, vídeo, cámara y galería mediante EDAL/permisos reales | Parcial; hardware pendiente |
| Seguridad | IPC real, namespaces, seccomp, cgroups, device broker y regresiones de denegación | Parcial; enforcement fuerte pendiente |
| Boot | Userland persistente en `EOS-SYSTEM`, recovery y rollback probados en QEMU | Imagen de desarrollo solamente |
| Hardware | Pruebas en equipos físicos y perfiles `.edisk` autorizados | Pendiente de entorno local vinculado |
| Capturas | Capturas de OOBE, shell, Studio, activities, Browser y recovery revisadas | Parcial; Browser/recovery faltan |
| Imágenes | `.img` PC y `.edisk` por perfil con hashes, SBOM y manifest de build | No publicar todavía |
| Publicación | Confirmación final del usuario antes de `gh release create` | No solicitada aún |

## Regla de publicación

> Ningún archivo binario, clave privada, modelo GGUF ni imagen de instalación se publica automáticamente al terminar una compilación.

Cuando los criterios estén satisfechos, se prepara primero una matriz de artefactos y hashes sin crear el release. Después se muestra al usuario qué archivos exactos se publicarían. Solo tras una confirmación explícita se ejecuta la publicación externa. Si algún criterio permanece pendiente, el release debe llamarse experimental y describir claramente el alcance, o debe posponerse.
