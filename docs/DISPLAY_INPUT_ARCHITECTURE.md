# Administración de pantallas y entrada EOS

## Objetivo

EOS tendrá un administrador propio de pantallas y entrada. Linux solo aporta los drivers y los dispositivos de entrada subyacentes; las aplicaciones reciben eventos a través de APIs EOS versionadas, no mediante `/dev/input`, X11, Wayland ni la ABI de Android.

La ruta de eventos es:

```text
kernel/driver → eos-deviced → eos-inputd → eos-displayd → eos-windowd → EOS UI/eos-ipcd → app trigger
```

`eos-deviced` identifica el dispositivo y aplica la política de hardware. `eos-inputd` normaliza puntos táctiles y clasifica gestos. `eos-displayd` transforma coordenadas según orientación, resolución, densidad y safe area. `eos-windowd` hace hit-testing y decide la ventana receptora respetando notch y regiones reservadas. El bus EOS entrega un evento serializado al handler declarado en `triggers.yml`.

## Contrato de pantalla

Cada display expone un perfil EOS, no una estructura del driver Linux:

| Campo | Ejemplo | Propósito |
|---|---|---|
| `display_id` | `internal-0` | Identificador estable del display |
| `logical_size` | `1080x2400` | Coordenadas lógicas de la UI |
| `physical_size` | `1080x2400` | Resolución física conocida, si existe |
| `orientation` | `portrait` | Orientación actual |
| `allowed_orientations` | `portrait,landscape` | Orientaciones autorizadas por la app/sistema |
| `safe_insets` | `top=80` | Área protegida por notch, barra o cámara |
| `touch` | `enabled` | Capacidad táctil publicada por EDAL |
| `scale` | `1.0` | Conversión físico→lógico |
| `vsync` | `managed` | Presentación gestionada por el shell |

Las aplicaciones usan `eos.display.bounds()`, `eos.display.safe_area()` y `eos.display.orientation()`. No controlan directamente el modo físico ni pueden dibujar fuera de sus límites autorizados.

## Eventos táctiles

El evento normalizado `eos.touch-0.2` contiene:

```json
{
  "type": "touch.end",
  "pointer_id": 7,
  "phase": "end",
  "position": {"x": 420, "y": 1180},
  "start": {"x": 420, "y": 1180},
  "delta": {"x": 0, "y": 0},
  "duration_ms": 83,
  "display_id": "internal-0",
  "window_id": "notes-main",
  "safe_area": true
}
```

Los eventos `touch.start`, `touch.move` y `touch.end` se mantienen separados de los gestos de alto nivel. Un app puede solicitar `touch` dentro de su ventana, pero no interceptar globalmente la pantalla salvo APIs del sistema autorizadas.

## Gestos

`eos-inputd` clasifica gestos con umbrales del perfil de entrada y entrega:

| Evento | Requisito | Campos relevantes |
|---|---|---|
| `gesture.tap` | Distancia corta y duración válida | posición, ventana, target |
| `gesture.swipe-left` | Desplazamiento horizontal dominante | delta, velocidad, dirección |
| `gesture.swipe-right` | Desplazamiento horizontal dominante | delta, velocidad, dirección |
| `gesture.swipe-up` | Desplazamiento vertical dominante | delta, velocidad, dirección |
| `gesture.swipe-down` | Desplazamiento vertical dominante | delta, velocidad, dirección |
| `gesture.cancel` | Cancelación por foco, ventana u overlay | motivo |

Los triggers se declaran en `policy/triggers.yml` y apuntan a handlers EosLang. Por ejemplo:

```yaml
triggers:
  - id: gesture.swipe-left
    handler: on_swipe_left
    delivery: foreground
    target: notes-main
```

El handler recibe un objeto de evento, nunca acceso al dispositivo. La entrega pasa por `eos-policyd` y `eos-ipcd`; la versión actual implementa el contrato y el despacho de referencia, mientras que el IPC de producción y el compositor real siguen pendientes.

## Ventanas, hit-testing y notch

`eos-windowd` registra ventanas con `content_rect`, `safe_area`, z-order y política de foco. Antes de enviar un evento, transforma la coordenada al espacio lógico, descarta puntos fuera del display, comprueba la región reservada por notch y realiza hit-testing sobre controles EOS UI. El notch puede mostrar controles del sistema por encima de la app, pero una app no puede ocultarlo ni capturar sus acciones.

La orientación modifica la transformación, no la semántica del gesto. Un swipe físico se normaliza en el espacio lógico de la orientación actual para que una app reciba `swipe-up` de manera coherente en portrait y landscape.

## Compatibilidad y límites

Este contrato ofrece capacidades táctiles parecidas a las que un usuario espera de Android, pero **no es compatibilidad Android**. EOS no ejecuta APK, no expone `android.view`, no usa SurfaceFlinger y no importa la ABI Android. Las aplicaciones EOS usan EosLang, EOS UI, EOSKit, `.eapp` y los servicios EOS.

La implementación actual es incremental: los contratos y autopruebas son funcionales; el compositor Qt 6, el lector de dispositivos físicos, el hit-testing conectado por IPC y la enforcement fuerte de permisos aún deben integrarse antes de afirmar soporte de hardware de producción.
