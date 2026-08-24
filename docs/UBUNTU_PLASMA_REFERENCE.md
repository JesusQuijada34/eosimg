# Imagen Ubuntu/KDE Plasma de referencia

Esta imagen es un entorno gráfico experimental para probar una experiencia de escritorio convencional dentro de QEMU. Está basada en Ubuntu Noble y usa KDE Plasma sobre X11, KWin como gestor de ventanas y SDDM como gestor gráfico de sesión. Incluye Calamares como instalador gráfico y un acceso `EOS Installer` dentro del menú de aplicaciones.

## Construcción

La construcción no instala Ubuntu, Plasma ni Calamares en el sistema anfitrión. `tools/build_ubuntu_plasma_reference.sh` crea un rootfs independiente bajo `build/ubuntu-plasma-rootfs`, instala los paquetes desde los repositorios configurados, crea el usuario de prueba `eos` y empaqueta el contenido en `build/eos-ubuntu-plasma-reference.img`. El usuario de prueba de esta imagen es `eos` con contraseña de desarrollo `eos`; estas credenciales no deben usarse fuera de QEMU.

`tools/build_ubuntu_plasma_iso.sh` convierte el rootfs en un squashfs Live y construye `build/eos-ubuntu-plasma-calamares.iso`. La ISO contiene las entradas de arranque normal y recovery, el kernel de desarrollo, la initramfs Live, el sistema Ubuntu/Plasma, KWin, SDDM y Calamares.

```bash
EOS_PLASMA_IMAGE_SIZE=6G tools/build_ubuntu_plasma_reference.sh
tools/build_ubuntu_plasma_iso.sh build/eos-ubuntu-plasma-calamares.iso
```

## Validación en QEMU

La validación se realiza con un CD-ROM virtual y un kernel explícito. La ISO debe arrancar hasta systemd y mostrar el servicio `sddm.service` iniciado sin un kernel panic.

```bash
timeout 120s qemu-system-x86_64 \
  -m 2048 -smp 2 \
  -kernel build/vmlinuz-eos-dev \
  -initrd build/ubuntu-plasma-live-initramfs.img \
  -append 'console=ttyS0 rdinit=/init boot=live systemd.unit=graphical.target' \
  -cdrom build/eos-ubuntu-plasma-calamares.iso \
  -nographic -serial mon:stdio -monitor none
```

La prueba actual confirmó que la initramfs Live monta el squashfs, entrega el control a systemd, inicia SDDM y no produce un kernel panic. La salida serial no es una captura visual del escritorio: para una captura gráfica se necesita una sesión QEMU con salida VGA/VNC y un cliente visual.

## Calamares

Calamares está instalado dentro de la imagen y se expone mediante `/usr/share/applications/eos-installer.desktop`, que ejecuta `pkexec calamares`. La imagen incorpora `calamares-settings-ubuntu-common` y `calamares-settings-kubuntu`, por lo que el instalador carga una secuencia y branding de Ubuntu/Kubuntu en `/etc/calamares`. La validación offscreen confirmó que Calamares puede inicializar su interfaz y comprobar módulos; no se ejecutaron particionado ni escritura de discos. Todavía requiere módulos de particionado, identidad y postinstalación ajustados a un producto EOS antes de poder instalar o reemplazar una instalación real.

## Relación con EOS

Ubuntu/KDE Plasma es una **referencia de escritorio**, no el ABI oficial de EOS. Plasma, KWin, SDDM, Calamares y los paquetes `.deb` no se convierten en aplicaciones `.eapp` ni se incorporan al runtime oficial de EOS. La plataforma EOS seguirá definiendo su propio shell Qt 6, compositor, servicios, permisos, formato `.eapp` y runtime EOSBC.

La imagen no debe publicarse como una versión terminada de EOS. Es una imagen experimental de referencia para evaluar paneles, dock, menú, ventanas, workspaces, sesión gráfica y flujo de instalación.
