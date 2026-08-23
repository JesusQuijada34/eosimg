# EOS Runner para Windows y Linux

EOS nativo se ejecutará directamente sobre el kernel Linux en el hardware soportado. En Windows o en una distribución Linux que no pueda arrancar EOS, el ejecutor `.eapp` será un producto separado: preparará una máquina virtual y expondrá el ciclo de vida de la aplicación dentro de una instancia EOS.

## Modos

| Modo | Host | Invitado | Uso |
|---|---|---|---|
| Nativo | PC compatible | EOS sobre Linux | Producto principal |
| VM x86-64 | Windows/Linux x86-64 | EOS x86-64 | Desarrollo y pruebas |
| VM AArch64 | Windows/Linux compatible | EOS AArch64 | Pruebas de portabilidad |
| Compatibilidad | Windows/Linux | Runtime `.eapp` limitado | Apps que no requieren servicios de EOS completos |

El prototipo `tools/eos_runner.py` recibe un kernel y un initramfs explícitos. En modo `--dry-run` imprime el comando que usaría QEMU; no descarga imágenes, no ejecuta archivos no proporcionados por el usuario y no altera el sistema anfitrión. En la implementación final, el runner tendrá una lista de imágenes confiables, aislamiento de red, almacenamiento por aplicación y controles de recursos.

## Instalación prevista

El instalador oficial de Windows y Linux se distribuirá con un gestor de imágenes firmado. La primera ejecución comprobará la plataforma, virtualización disponible, espacio, memoria y versión de la imagen EOS. Si el host no permite aceleración, se usará emulación de instrucciones como fallback, con rendimiento inferior. Esto no cambia el diseño del EOS nativo: es solo el mecanismo para ejecutar EOS cuando el host no puede arrancarlo directamente.

## Prueba local

```bash
python3 tools/eos_runner.py \
  --kernel /ruta/a/linux \
  --initramfs build/eos-initramfs.img \
  --arch x86_64 --headless --dry-run
```

La imagen EOS definitiva requerirá un kernel configurado, firmware/bootloader y una política de dispositivos estable. El initramfs actual es un hito de desarrollo y no debe considerarse una distribución lista para instalar.
