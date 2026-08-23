# Política de ABI y compatibilidad de EOS

## Objetivo

EOS usará Linux como kernel, pero no será una distribución Linux de escritorio. El contrato público para aplicaciones será **EOS API + `.eapp` + EosLang/EOSBC**, no glibc, POSIX completo, ELF genérico, dpkg ni apt.

## Qué se rechazará

| Entrada | Política EOS |
|---|---|
| `.deb` | No hay instalador ni gestor dpkg/apt; se rechaza como paquete de aplicación |
| ELF Linux de usuario | No forma parte de la ABI pública; el launcher no lo ejecuta |
| AppImage | No soportado |
| Binario Linux con glibc | No soportado como app EOS |
| `.eapp` firmado | Formato público de aplicaciones EOS |
| EOSBC/EosLang | Formato portable controlado por el runtime EOS |
| Componente nativo EOS | Solo se carga desde particiones de sistema, con firma y ABI de build compatibles |

## Cómo se consigue sin cambiar el kernel

El kernel Linux seguirá proporcionando procesos, memoria virtual, archivos, red, drivers y aislamiento. EOS cerrará la frontera de ejecución en userland:

1. El shell no ejecuta rutas arbitrarias. Solicita el lanzamiento a `eos-packaged`.
2. `eos-packaged` acepta solo `.eapp` con manifiesto válido, versión compatible, permisos declarados y firma confiable.
3. El runtime público carga EOSBC o un formato nativo EOS versionado; no expone un launcher de ELF Linux al usuario.
4. Las particiones de apps se montan con políticas restrictivas y sin herramientas `apt`, `dpkg`, `ld-linux` o shells de desarrollo en la imagen de producción.
5. El soporte interno de ELF que pueda necesitar Linux para arrancar componentes del sistema no se convierte en compatibilidad de usuario. Los binarios de sistema estarán aislados, firmados y compilados contra el ABI privado de la build EOS.

Esto produce **incompatibilidad de plataforma**, no una afirmación de que el kernel Linux sea incapaz de reconocer los bytes de un ELF. Un usuario con control de root sobre su propio dispositivo siempre puede modificar el sistema; el objetivo es que la plataforma oficial no lo soporte ni lo anuncie.

## ABI de EOS

EOS expondrá servicios mediante interfaces versionadas, IPC propio y bibliotecas EOSKit. La aplicación no deberá depender de syscalls Linux directas, rutas internas, `/proc`, `/sys`, glibc o detalles del hardware. El compilador marcará el target, la API y la versión mínima en `.eapp`.

## Beneficio de esta decisión

La separación permite que EOS evolucione como Android: Linux es el motor, mientras que el framework, el runtime, los servicios, la interfaz y la distribución forman una plataforma diferente. También facilita que una futura versión de Windows/Linux ejecute `.eapp` mediante un runner oficial sin prometer compatibilidad con software Linux arbitrario.
