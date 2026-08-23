# Especificación `.eapp` 0.3

## Propósito

`.eapp` es el formato de distribución de aplicaciones de Etternhall Operating System. Es un contenedor binario versionado que transporta una aplicación EOS completa: código EosLang compilado a EOSBC, interfaz declarativa, recursos, metadata, política declarativa y pruebas de integridad. Linux aporta el kernel y los drivers; una aplicación `.eapp` no es un ELF Linux, un `.deb`, un AppImage ni una aplicación de escritorio Linux.

La herramienta oficial `eapp.py` es la implementación de referencia del prototipo. El formato separa deliberadamente responsabilidades: JSON describe la identidad y metadata estable, YAML describe la política legible de permisos y triggers, y los archivos MF contienen los registros criptográficos verificables.

## Estructura del payload

Cada paquete debe incluir esta estructura relativa:

```text
manifest.json                 # metadata canónica de aplicación
policy/permissions.yml        # permisos solicitados y justificación
policy/triggers.yml           # eventos que pueden despertar la aplicación
signatures/manifest.mf         # digest y firma del manifest.json
signatures/payload.mf          # digest y firma del payload comprimido
src/*.elang                    # fuente opcional incluida para desarrollo/auditoría
bin/main.eosbc                 # bytecode ejecutable EOSBC
ui/main.eosui                  # interfaz declarativa EOS UI
resources/icon.svg             # icono
resources/splash.svg           # splash
resources/...                  # recursos de la aplicación
docs/README.md                 # documentación
LICENSE                        # licencia
```

La fuente EosLang puede omitirse en una distribución optimizada, pero `bin/main.eosbc` y la interfaz declarativa siguen siendo obligatorios para una aplicación visual. Las librerías EOS se identifican por módulo y versión en metadata; no se copian arbitrariamente como binarios Linux de usuario.

## `manifest.json`: metadata

`manifest.json` es el único documento de identidad y metadata. Se serializa en JSON canónico, UTF-8, ordenado por claves y con una terminación de línea. Debe contener:

| Campo | Obligatorio | Significado |
|---|---:|---|
| `format` | Sí | Debe ser `eapp` |
| `format_version` | Sí | `3` para este contrato |
| `identity.bundle_id` | Sí | Identidad estable de la aplicación |
| `identity.publisher` | Sí | Entidad publicadora |
| `identity.author` | Sí | Autoría declarada |
| `name` | Sí | Nombre visible |
| `version` | Sí | Versión semántica de la app |
| `api` | Sí | API de EosLang/EOS utilizada |
| `min_eos` | Sí | Versión mínima del sistema EOS |
| `entrypoint` | Sí | Ruta al EOSBC dentro del payload |
| `ui.entry` | Sí | Ruta al documento EOS UI |
| `targets` | Sí | Arquitecturas o perfiles EOS soportados |
| `resources` | Sí | Icono, splash, documentación y licencia |
| `libraries` | Sí | Módulos EOS requeridos con versión |
| `policy.permissions` | Sí | Ruta del YAML de permisos |
| `policy.triggers` | Sí | Ruta del YAML de triggers |
| `signatures.manifest` | Sí | Ruta del MF del manifest |
| `signatures.payload` | Sí | Ruta del MF del payload |
| `payload_sha256` | Sí | Hash del payload comprimido |
| `created_by` | Sí | Versión de las herramientas oficiales |

El JSON no decide por sí solo si una capacidad está permitida. Solo referencia los documentos de política y permite que el instalador detecte rápidamente una estructura inconsistente.

## `permissions.yml`: permisos

El YAML de permisos es declarativo y no ejecutable. Su forma inicial es:

```yaml
schema: eos-permissions-0.1
permissions:
  - id: storage.user-data
    access: read-write
    scope: app-data
    reason: "Guardar notas del usuario"
  - id: notifications.post
    access: request
    scope: app
    reason: "Avisar cuando una nota tenga recordatorio"
```

Los identificadores se validan contra el registro de APIs EOS. El instalador y `eos-policyd` aplican una política deny-by-default; la justificación no concede permisos automáticamente. No se permiten comodines, rutas arbitrarias, ejecución de shell, acceso a `/proc` fuera de la interfaz EOS ni acceso directo a dispositivos.

## `triggers.yml`: eventos

El YAML de triggers declara qué eventos del sistema pueden entregar control a la aplicación. No contiene código ni comandos del sistema:

```yaml
schema: eos-triggers-0.1
triggers:
  - id: app.launch
    handler: on_launch
    delivery: foreground
  - id: notification.action
    handler: on_notification_action
    delivery: foreground
```

Los handlers deben existir en el programa EosLang compilado y solo reciben payloads serializados por el bus EOS. Un trigger no habilita red, micrófono, cámara, ubicación ni ejecución en segundo plano sin el permiso correspondiente y sin aprobación del sistema.

## Archivos `.mf`: firmas

Los archivos MF son registros de integridad y autenticidad, no una extensión de código. La forma canónica inicial es texto UTF-8 con una línea por campo:

```text
MF-Version: 1
Algorithm: Ed25519
Key-ID: 0123456789abcdef
Subject: manifest.json
Digest-SHA256: <64 hex chars>
Signature-Base64: <base64>
```

`manifest.mf` firma el `manifest.json` canónico más el digest de los documentos de política. `payload.mf` firma el hash del payload comprimido y un inventario ordenado de rutas. EOS debe verificar ambos MF, la clave confiable del repositorio, los hashes y la ausencia de rutas peligrosas antes de instalar. La clave pública incluida no crea confianza por sí sola: la confianza proviene del almacén de claves de EOS y su política de rotación/revocación.

## Interfaz y código

Una aplicación visual no puede ser solamente metadata. Debe incluir un `entrypoint` EOSBC y un `ui.entry` EOS UI. EOS UI será una descripción declarativa de ventanas, páginas, controles, acciones y bindings; el código EosLang manejará estado y eventos mediante APIs de EOSKit. Ningún elemento de UI puede ejecutar shell, cargar un ELF o saltarse `eos-policyd`.

Ejemplo mínimo de UI:

```yaml
schema: eos-ui-0.1
window:
  id: notes-main
  title: "EOS Notes"
  safe_area: true
  children:
    - type: navigation
      id: notes-navigation
      action: open_note
    - type: text_input
      id: note-editor
      bind: state.current_text
    - type: button
      id: save
      text: "Guardar"
      action: save_note
```

El ejemplo es YAML porque la UI declarativa debe ser cómoda de revisar, pero su ruta se declara en `manifest.json` y se valida como un documento separado. La política de permisos y triggers sigue estando separada de la interfaz.

## Seguridad y límites honestos

> El objetivo correcto de `.eapp` es **autenticidad, integridad, aislamiento y resistencia al análisis**, no una promesa imposible de que el contenido nunca pueda inspeccionarse.

EOS no ejecuta paquetes sin firma salvo mediante una opción explícita de desarrollo local. No se admiten `.deb`, AppImage, ELF Linux de usuario, scripts de shell como entrypoint ni paquetes que declaren una ruta fuera de su payload. El código puede ser analizado por el sistema y por herramientas autorizadas; las firmas no son anti-ingeniería-inversa absoluta.

La versión 0.3 define el contrato y las validaciones. La enforcement fuerte mediante namespaces, seccomp, cgroups y un bus IPC completo continúa siendo una tarea separada y no debe sobredeclararse como terminada.
