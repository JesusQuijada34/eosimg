# Escritorio Etternhall

Etternhall tendrá un escritorio convencional sobre el que se ejecutan aplicaciones EOS. El sistema no será una pantalla de teléfono ampliada: tendrá un área de trabajo, ventanas, panel superior, launcher, tareas abiertas, áreas de trabajo y navegación con teclado y ratón, además de touch cuando el hardware lo permita.

## Lenguaje visual

La dirección visual se inspira en dos ideas generales: la claridad, el espaciado y la jerarquía limpia de los sistemas móviles modernos, y la composición tipográfica, los mosaicos funcionales y el uso estructurado del espacio asociado a Metro. La implementación será original: no copiará iconos, nombres, tipografías propietarias, assets ni métricas exactas de iOS o Windows.

| Superficie | Decisión de Etternhall |
|---|---|
| Fondo | Superficie neutra con acentos dinámicos de eJairo |
| Panel | Panel superior con menú Etternhall, búsqueda, tareas, conectividad, audio, batería y reloj |
| Launcher | Menú de aplicaciones con lista, búsqueda y mosaicos redimensionables |
| Ventanas | Marco limpio con título, icono, minimizar, maximizar, cerrar y estados snap |
| Multitarea | Vista de tareas, escritorios virtuales y back stack separado por actividad |
| Notificaciones | Centro BlinkE anclado al panel, sin bloquear el área de trabajo |
| Touch | Gestos opcionales sobre ventanas, panel y actividades; teclado/ratón son ciudadanos de primera clase |
| Estilo | EOS CSS con superficies, radios, sombras, foco visible y safe areas |

## Capas

`eos-displayd` describe monitores, resolución, orientación y safe areas. `eos-windowd` administra ventanas físicas del escritorio: geometría, foco, z-order, maximizado, minimizado, snap y workspaces. `eos-activityd` administra las pantallas internas de una aplicación. `eos-launcherd` descubre `.eapp` auditables y abre su actividad principal. `eos-blinked` presenta notificaciones. El compositor Qt 6 futuro será responsable de combinar estas superficies; el shell actual es una implementación de desarrollo.

> Una ventana de escritorio es un contenedor de sistema. Una actividad es una pantalla interna de una aplicación. No son la misma cosa y ninguna se ejecuta como una Activity de Android.

## Estados de ventana

Cada ventana EOS tendrá un identificador de aplicación, actividad activa, workspace, rectángulo lógico, estado (`normal`, `maximized`, `minimized`, `snapped-left`, `snapped-right`, `fullscreen`), foco y safe-area policy. Las aplicaciones no reciben el socket del compositor ni pueden mover ventanas fuera de sus permisos; solicitan cambios mediante EOSKit y `eos-windowd` los valida.

## Compatibilidad de interacción

El escritorio soporta pointer, teclado, touch y swipe. Un swipe horizontal dentro de una actividad se entrega primero al árbol de UI de esa actividad; un swipe sobre el borde del escritorio puede activar el workspace o la vista de tareas; un gesto sobre el panel se reserva para notificaciones y quick settings. El sistema debe evitar que un gesto global robe eventos a un control que tenga captura explícita.

## Alcance actual

Los contratos de display, window, input, actividades y UI ya existen y tienen autopruebas. La siguiente implementación convierte el shell de teléfono actual en una ventana de escritorio de desarrollo con panel, launcher, tareas y escritorios virtuales. Esto no implica todavía un compositor Wayland/Qt de producción ni compatibilidad con aplicaciones Linux genéricas.

## Base de referencia temporal

Para estudiar un escritorio completo se selecciona **Kubuntu con KDE Plasma** como referencia de laboratorio, no como dependencia de la ABI final. La documentación oficial de KDE describe Plasma con launcher, bandeja del sistema, notificaciones, Discover, paneles, widgets, escritorios y configuración de hardware; Kubuntu combina Ubuntu con Plasma como distribución lista para usar [[1]](https://kde.org/plasma-desktop/) [[2]](https://kubuntu.org/).

La instalación debe hacerse en una VM/QEMU o en una máquina/carpeta vinculada, no sobre el root del sandbox ni mezclando paquetes de Plasma con el userland EOS. Se estudiarán sus capacidades visuales y de sesión para reproducirlas mediante `eos-windowd`, `eos-displayd`, `eos-launcherd`, `eos-blinked`, `eos-activityd` y el futuro compositor EOS. No se distribuirá Kubuntu dentro de EOS como formato de aplicaciones ni se aceptarán paquetes `.deb` como aplicaciones EOS.

### Referencias

[1]: https://kde.org/plasma-desktop/ "KDE Plasma Desktop"
[2]: https://kubuntu.org/ "Kubuntu"
