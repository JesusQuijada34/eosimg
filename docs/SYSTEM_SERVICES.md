# Userland y gestores de EOS

EOS no será un Linux de escritorio con otra apariencia. El kernel Linux queda debajo como motor de procesos, memoria, drivers y almacenamiento, pero el userland oficial expondrá contratos propios.

## Servicios base

| Servicio | Función | Dependencias |
|---|---|---|
| `eos-logd` | Registro estructurado y diagnóstico | Kernel |
| `eos-powerd` | Energía, batería y estados de suspensión | `eos-logd` |
| `eos-storaged` | Volúmenes, datos y caché | `eos-logd` |
| `eos-packaged` | Firma, instalación, permisos y rollback | `eos-logd`, `eos-storaged` |
| `eos-displayd` | Pantalla, escalado y composición | `eos-logd`, `eos-powerd` |
| `eos-windowd` | Superficies, foco, gestos y ventanas | `eos-displayd` |
| `eos-phone-shell` | Launcher, recovery UI y sesión táctil | `eos-windowd`, `eos-packaged` |

`eos-serviced` calcula el orden de dependencias de forma determinista. La siguiente etapa será añadir supervisión de procesos, reinicio controlado, límites de recursos y políticas de aislamiento. El binario de prueba actual solo muestra el plan y no modifica el sistema anfitrión.

## Frontera de aplicación

Una aplicación EOS no obtiene acceso directo a syscalls, `/proc`, `/sys`, glibc ni herramientas de distribución. Solicita operaciones a APIs EOS versionadas mediante IPC. `eos-packaged` comprueba el manifiesto `.eapp`, la firma, la versión mínima de EOS, el target, los permisos y el sandbox antes de entregar la app al runtime.

El sistema de producción puede contener ejecutables internos necesarios para arrancar Linux y los servicios, pero estos son componentes firmados de la imagen EOS y no forman parte de la ABI pública. El launcher de aplicaciones rechaza ELF Linux de usuario y `.deb`.
