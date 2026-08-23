# Bootloader EOS

## Estado actual

La imagen de desarrollo usa GRUB UEFI como bootstrap para cargar `eos-linux` e `eos-initramfs.img` desde `EOS-BOOT`. Esto permite probar el kernel, el initramfs y el menú normal/recovery sin instalar nada en el firmware del equipo anfitrión.

## Diseño objetivo

El bootloader propio de EOS tendrá cuatro etapas. La primera verificará el hardware y la arquitectura. La segunda validará la firma y los hashes del manifiesto de firmware. La tercera seleccionará el slot A/B y el modo normal o recovery. La cuarta cargará el kernel Linux y transferirá los parámetros de arranque al init de EOS.

| Etapa | Responsabilidad |
|---|---|
| ROM/UEFI | Entregar control al cargador firmado |
| `eos-boot` | Verificar imagen, perfil y slot |
| `eos-kernel` | Arrancar Linux con parámetros EOS |
| `eos-init` | Montar servicios, políticas y userland |

El bootloader no ejecutará paquetes `.eapp`, `.deb` ni ELF Linux de usuario. Solo cargará componentes de sistema que pertenezcan a la imagen EOS, coincidan con el perfil de hardware y pasen la política de integridad. La implementación propia reemplazará GRUB cuando exista un formato de configuración y una cadena de confianza estables.

## Seguridad de instalación

El instalador futuro deberá mostrar el disco destino, verificar el tamaño y pedir confirmación antes de escribir. No se añadirá una operación silenciosa que pueda sobrescribir un disco del usuario. En este repositorio los scripts escriben únicamente rutas de imagen proporcionadas explícitamente.
