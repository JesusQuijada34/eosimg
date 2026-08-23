# Integración real de llama.cpp en EOS

## Estado actual

Se compiló desde el repositorio oficial `ggml-org/llama.cpp` una revisión fija:

```text
c060ca974c773c7c3d17fd1b66dc9d312bc292c0
```

La build local produjo `llama-simple-chat` en el área ignorada `build/third_party/llama.cpp/build/bin/`. La compilación usó CPU, `GGML_NATIVE=OFF`, ejemplos activados, tests desactivados y servidor desactivado. La revisión y los binarios no se agregan al repositorio EOS.

El proyecto oficial describe su producto principal como la biblioteca `llama` con interfaz C en `include/llama.h`, además de herramientas y servidores que usan esa biblioteca.[^1] Su guía oficial muestra la compilación CMake básica y documenta que el formato utilizado por el flujo moderno de inferencia es GGUF.[^2]

## Frontera EOS

`tools/eos_llama_backend.py` es la frontera provisional entre EOS y llama.cpp. No expone el CLI como aplicación de usuario; lo ejecuta como backend interno seleccionado por EOS. El adaptador:

| Control | Comportamiento |
|---|---|
| Ejecutable | Debe ser una ruta local ejecutable explícita o la build fijada en `build/third_party` |
| Modelo | Debe existir localmente y terminar en `.gguf` |
| Integridad | `--sha256` es obligatorio para ejecutar y debe coincidir byte a byte |
| Red | `HF_HUB_OFFLINE=1` y `NO_PROXY=*`; no se descarga desde Hugging Face |
| Contexto | Se limita al rango EOS 256–131072 tokens |
| GPU | `-ngl 0` por defecto; la selección posterior dependerá de capacidades del dispositivo |
| Fallo | Sin modelo, hash o backend válido, el proceso termina sin inferencia |

El modo predeterminado es **plan-only**: muestra backend, revisión, arquitectura y política offline. La ejecución requiere simultáneamente `--run`, `--model` local y `--sha256` coincidente. Así, un modelo de Hugging Face no se convierte en una descarga implícita ni en código ejecutable remoto.

## Flujo de ejecución en un dispositivo EOS

1. `eos-modeld` obtiene un manifiesto previamente aceptado con repositorio, revisión fijada, hash, licencia, tamaño y arquitectura.
2. El Model Store descarga únicamente después de consentimiento y verifica el archivo antes de moverlo al almacén de modelos.
3. El selector de RAM calcula presupuesto para kernel, shell, caché y contexto; no basta con que el tamaño del archivo quepa en disco.
4. `eos-assistantd` solicita al backend un modelo ya verificado y un perfil de contexto permitido.
5. El backend inicia el proceso interno con permisos mínimos, sin acceso de red y con límites de memoria/CPU.
6. Los eventos `listening`, `thinking` y `speaking` se publican hacia `eos-immersived`; la interfaz visual no implica que exista todavía entrada de micrófono ni síntesis de voz.

## Próxima evolución técnica

El adaptador de CLI debe reemplazarse progresivamente por una biblioteca EOS enlazada contra `libllama`, manteniendo el mismo contrato de validación. Esa migración permitirá controlar el ciclo de vida del modelo, los callbacks de tokens, cancelación, memoria y sesiones sin depender del protocolo interactivo de `llama-simple-chat`. La primera API C++ debe envolver únicamente funciones documentadas y fijar la revisión de llama.cpp en el sistema de build.

No se debe añadir un modelo grande al repositorio. Para pruebas unitarias se usarán fixtures mínimos que validen rechazo de extensión, hash, revisión y límites; una prueba de generación real requerirá que el usuario suministre un GGUF compatible o que se confirme explícitamente una descarga con licencia y checksum.

## Referencias

[^1]: [ggml-org/llama.cpp — repositorio oficial](https://github.com/ggml-org/llama.cpp).
[^2]: [ggml-org/llama.cpp — guía oficial de compilación](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).
