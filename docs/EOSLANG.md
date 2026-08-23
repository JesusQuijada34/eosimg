# EosLang 0.2

EosLang es el lenguaje propio de EOS para aplicaciones y servicios. Está diseñado para resultar familiar a quienes conocen JavaScript o Python, pero el runtime mantiene una frontera explícita: el código compilado solo puede usar módulos EOSKit declarados y no puede ejecutar shell, cargar ELF Linux ni acceder directamente al host.

## Programa mínimo

```elang
app com.etternhall.eos.hello
version "0.2.0"
use eos.ui as ui

state title: string = "Etternhall"

fn on_launch() -> void
  call ui.show "hello-main"
  text "Hola desde EOS"
endfn

on app.launch => on_launch
print title
end
```

El compilador produce EOSBC 2, un bytecode JSON para el runtime de referencia y para futuros runtimes C++/Qt 6. El JSON del bytecode es legible durante esta etapa para facilitar auditoría y pruebas; no es una promesa de que las aplicaciones distribuidas serán simples archivos de texto.

## Características 0.2

| Elemento | Estado |
|---|---|
| Variables | `let` y `state`, con tipos `string`, `int`, `float`, `bool`, `any` e inferencia básica |
| Funciones | Parámetros tipados, tipo de retorno y bloques `fn`/`endfn` |
| Eventos | Declaraciones `on evento => handler` validadas contra handlers compilados |
| Módulos | `use eos.ui`, `use eos.storage`, `use eos.events` con alias opcional |
| UI | `text`, `ui.show` y llamadas a EOS UI; la interfaz completa vive en `.eosui` |
| Servicios | `call` limitado a APIs EOSKit declaradas, nunca a shell o ELF |
| Estado | Variables persistentes lógicas preparadas para el almacenamiento EOS |
| Control | `return`, literales string/entero/float/bool/null y referencias verificadas |
| Backend | EOSBC 2, con intérprete de referencia Python |

## Diseño de lenguaje

EosLang separa el código de la política de la aplicación. El fuente `.elang` expresa estado, lógica y handlers. La interfaz declarativa `.eosui` expresa ventanas, controles y bindings. `policy/permissions.yml` solicita capacidades y `policy/triggers.yml` declara eventos. `manifest.json` identifica el paquete. Los archivos `.mf` registran hashes y firmas. Ninguna de esas capas puede conceder por sí sola privilegios al proceso.

Los módulos EOSKit son nombres de API, no importaciones arbitrarias de Python, JavaScript o Linux. En la versión 0.2 el compilador reconoce el módulo utilizado para documentación y el runtime comprueba una lista cerrada de prefijos `eos.ui.*`, `eos.storage.*` y `eos.events.*`. La resolución real pasará por `eos-ipcd` y `eos-policyd` cuando el bus de servicios sustituya el runtime de referencia.

## Evolución prevista

Las siguientes etapas añadirán expresiones, colecciones inmutables, errores tipados, `async` cooperativo, paquetes de librerías EOS versionados y un sistema de pruebas. Se añadirán solo con contratos de bytecode versionados y compatibilidad explícita; no se incorporarán `eval`, FFI libre, ejecución nativa del usuario ni mecanismos para evadir el sandbox.

EosLang no pretende ser una copia de JavaScript o Python. Toma su ergonomía, pero EOS conserva control de tipos, módulos, permisos, eventos, ciclo de vida y aislamiento como partes del lenguaje y del runtime.
