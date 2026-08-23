# Formatos de imagen EOS

## `.edisk` para dispositivos

`.edisk` será un contenedor de firmware orientado a dispositivos concretos. Su manifiesto declarará el fabricante EOS, modelo de placa, SoC/perfil, revisión de hardware, bootloader, kernel, initramfs, device tree, particiones, versión mínima de bootloader, versión de rollback y firma. No se instalará si el perfil de hardware no coincide.

Particiones conceptuales:

| Partición | Contenido | Política |
|---|---|---|
| `boot` | bootloader y configuración | firmada, no modificable por apps |
| `system` | kernel, servicios y EOS userland | solo lectura durante arranque |
| `vendor` | drivers y HAL del dispositivo | vinculada al modelo |
| `recovery` | entorno de recuperación | arranque independiente |
| `data` | apps, preferencias y datos del usuario | cifrado opcional |
| `cache` | actualizaciones temporales y caché | borrable desde recovery |

## `.img` para PC

`.img` será una imagen de disco de PC arrancable. La versión final usará una tabla GPT y una partición EFI para el bootloader. El sistema tendrá particiones separadas para `system`, `recovery`, `data` y `cache`, con un archivo de metadatos EOS en la partición de sistema. El instalador de PC verificará hash y firma antes de escribir la imagen y ofrecerá una vista previa del disco destino.

## Requisitos comunes

Ambos formatos deberán ser versionados, contener hashes por componente, declarar la arquitectura (`x86_64`, `aarch64` u otra), indicar el perfil de EOS, soportar actualización atómica A/B en una fase posterior y permitir rollback. Un paquete de firmware no debe ejecutar instrucciones de instalación recibidas desde el archivo: el instalador oficial valida primero estructura, tamaño, firma, destino y compatibilidad.

El prototipo del repositorio usa un contenedor comprimido para validar el diseño. No sustituye aún una imagen GPT/UEFI real ni un firmware para hardware físico.
