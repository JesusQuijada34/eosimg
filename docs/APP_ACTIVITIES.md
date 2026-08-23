# Actividades y pantallas internas EOS

## Concepto

Una aplicación `.eapp` puede contener varias **actividades EOS**. Una actividad es una unidad de interacción con su propia pantalla declarativa, estado y ciclo de vida. Es parecida conceptualmente a una Activity de Android, pero no es la misma API: EOS no ejecuta APK, no expone `android.app.Activity` y no comparte la ABI Android.

La actividad principal es el punto de entrada visual elegido por el sistema al abrir la aplicación. El `entrypoint` del paquete sigue siendo el programa EOSBC; `activities.main` identifica la primera pantalla que el navegador de aplicaciones debe montar.

## Declaración en `manifest.json`

```json
{
  "activities": {
    "main": "notes.home",
    "definitions": [
      {
        "id": "notes.home",
        "title": "Notas",
        "ui": "ui/home.eosui",
        "entry": "on_home_create",
        "exported": true,
        "orientation": "any",
        "restore": true
      },
      {
        "id": "notes.editor",
        "title": "Editar nota",
        "ui": "ui/editor.eosui",
        "entry": "on_editor_create",
        "exported": false,
        "orientation": "portrait",
        "restore": true
      }
    ]
  }
}
```

`main` debe coincidir con una definición. Las rutas de UI y handlers deben estar dentro del payload y los handlers deben existir en EOSBC. Una actividad no puede abrir directamente una actividad privada de otra aplicación; la navegación entre apps se realiza mediante intents EOS autorizados.

## Ciclo de vida

EOS entrega estados ordenados a cada actividad:

| Estado | Significado |
|---|---|
| `created` | Se creó la instancia y se restauró el estado permitido |
| `started` | Está preparada para recibir eventos |
| `resumed` | Es la actividad visible y con foco de interacción |
| `paused` | Perdió el foco, pero puede conservar recursos ligeros |
| `stopped` | Ya no es visible; debe liberar recursos temporales |
| `destroyed` | Se cerró o se eliminó por política/sistema |

Los handlers EosLang son `on_<activity>_<state>` o los nombres declarados en `lifecycle`. El sistema nunca entrega eventos touch/swipe a una actividad `paused`, `stopped` o `destroyed`.

## Navegación y back stack

`eos.navigation.push(route, params)` crea una actividad autorizada y la coloca en el back stack. `eos.navigation.replace(route, params)` sustituye la actividad visible. `eos.navigation.back()` vuelve a la actividad anterior y entrega el lifecycle correspondiente. El stack pertenece a la instancia de la app y se guarda mediante `eos.storage` cuando `restore` es verdadero.

Los parámetros de navegación son datos JSON serializables y están limitados por tamaño. No pueden transportar handles de kernel, punteros, ejecutables ni rutas arbitrarias.

## Touch/swipe en actividades

El pipeline de entrada resuelve primero el display físico y la ventana EOS; después el router de actividad selecciona la actividad `resumed`. El hit-testing de EOS UI elige el control. Finalmente `eos-ipcd` entrega un evento como `gesture.swipe-left` al handler declarado por esa actividad o por la aplicación.

```yaml
schema: eos-triggers-0.2
triggers:
  - id: gesture.swipe-left
    activity: notes.home
    handler: on_home_swipe_left
    delivery: resumed-only
  - id: ui.action.save
    activity: notes.editor
    handler: save_note
    delivery: resumed-only
```

La misma actividad puede declarar acciones de botones y gestos. Un swipe global del sistema, como abrir el panel EOS, se consume antes del app cuando la región pertenece a un overlay protegido.

## Diferencia con la pantalla física

`eos-displayd` administra el display físico, orientación, notch y safe area. `eos-activityd` administra pantallas internas de la app. `eos-windowd` mantiene la ventana de la app y `eos-ui` monta la vista de la actividad visible. Son capas separadas:

| Capa | Responsabilidad |
|---|---|
| `eos-displayd` | Display físico, resolución, orientación, safe area |
| `eos-windowd` | Ventanas, foco, z-order, hit-testing |
| `eos-activityd` | Instancias, rutas, lifecycle, back stack |
| `eos-ui` | Controles, bindings y composición de la pantalla |
| `eos-ipcd` | Eventos y llamadas brokered entre servicios |

La implementación inicial de EOS ofrece contratos y autopruebas locales. El compositor Qt 6 real, el IPC completo y la restauración en una sesión de producción seguirán desarrollándose incrementalmente.
