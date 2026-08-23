# Integración Gecko en EOS

## Decisión técnica

EOS no instalará Firefox Linux ni Safari como aplicaciones de usuario. El navegador será `EOS Browser`, una aplicación `.eapp`/servicio EOS con un backend Gecko interno. El límite es importante: un ELF Linux genérico no se convierte en una aplicación EOS solo por copiarlo dentro de una imagen.

La documentación oficial de Mozilla describe Gecko como el motor que reúne parsing HTML, networking, JavaScript, IPC, DOM, widgets y gráficos.[^1] También describe `docshell` como la capa que gestiona documentos y carga de URI, y señala que `mobile/android` contiene Firefox para Android y GeckoView.[^2] GeckoView es explícitamente una biblioteca Android: expone `GeckoRuntime`, `GeckoSession` y `GeckoView`, y delega navegación, historial, permisos, prompts y medios al embedder.[^4] Su modelo interno es multiproceso, pero Mozilla indica que ese detalle no se expone normalmente a los embedders.[^4] GeckoView tiene una ruta pública de embedding orientada a Android, mientras que una build completa de Firefox para Linux requiere como mínimo 4 GB de RAM, recomienda 8 GB y necesita al menos 30 GB libres.[^3]

Por eso el sandbox actual sirve para diseñar y probar el contrato, pero no es el lugar adecuado para compilar una build completa de Firefox: tiene 3.8 GiB de RAM y no se ha reservado un volumen persistente de decenas de GB.

## Bridge actual

`tools/eos_gecko_bridge.py` es un primer adaptador de proceso. En modo predeterminado solo planifica el lanzamiento. Exige un ejecutable interno suministrado de forma explícita, un perfil separado y una URI limitada a `http(s)` o `about:`. Cuando se habilite `--run`, construye un comando equivalente a:

```text
<gecko-internal> --no-remote --profile <eos-profile> <uri>
```

El bridge no ejecuta Firefox instalado en el host automáticamente, no acepta `file://`, no mezcla perfiles y no pretende que un ejecutable temporal sea Gecko real. La autoprueba usa un runner sintético únicamente para verificar la frontera de permisos y argumentos. La API EOS se inspira en la separación runtime/session/delegates de GeckoView, pero su implementación final deberá ser C++/Qt 6 y no copiar la API Java de Android.

## Ruta para una integración real

| Etapa | Entregable | Criterio de aceptación |
|---|---|---|
| A | Elegir backend | Gecko/Mozilla o alternativa WebKit con licencia y target mantenibles |
| B | Build interna | Revisión fijada, toolchain EOS, reproducibilidad y avisos de licencia |
| C | Proceso web | Perfil aislado, IPC, límites de recursos y permisos EOS |
| D | UI | Superficie Qt 6 propia para pestañas, barra, descargas, permisos y notch |
| E | Compatibilidad | Web Platform Tests seleccionados, navegación HTTPS y pruebas de regresión |
| F | Distribución | Componente firmado dentro de la cadena EOS; sin binarios Linux genéricos como apps |

No se integrará el frontend XUL de Firefox de escritorio como UI EOS. EOS conservará su shell Qt 6 y consumirá el motor mediante un proceso/bridge con una API reducida. Esto reduce el acoplamiento visual y deja claro qué partes pertenecen a Mozilla y cuáles son código original de EOS.

## Licencias y marca

El código de Mozilla y sus binarios pueden tener licencias y obligaciones distintas según el componente. Antes de redistribuir una build se deben conservar avisos, revisar dependencias y separar el uso de código de cualquier uso de la marca Firefox. EOS usará una marca propia; no presentará una build modificada como Firefox oficial.

## Estado honesto

La build real de `llama.cpp` y una inferencia local ya funcionan. Para Gecko, el estado actual es **contrato y bridge de proceso probados, motor web real aún no integrado**. El siguiente paso no es descargar un Firefox arbitrario, sino preparar un entorno persistente/local con suficiente espacio, fijar una revisión de Mozilla y comprobar qué superficie de embedding puede mantenerse para el target de EOS.

## Referencias

[^1]: [Mozilla Firefox Source Docs — Gecko](https://firefox-source-docs.mozilla.org/overview/gecko.html).
[^2]: [Mozilla Firefox Source Docs — Firefox Source Code Directory Structure](https://firefox-source-docs.mozilla.org/contributing/directory_structure.html).
[^3]: [Mozilla Firefox Source Docs — Building Firefox on Linux](https://firefox-source-docs.mozilla.org/setup/linux_build.html).
[^4]: [Mozilla Firefox Source Docs — GeckoView Architecture](https://firefox-source-docs.mozilla.org/mobile/android/geckoview/contributor/geckoview-architecture.html) y [GeckoView](https://mozilla.github.io/geckoview/).
