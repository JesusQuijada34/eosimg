# Construir EOS en desarrollo

## Requisitos

EOS se construye actualmente con C++20, CMake, Qt 6 y Python 3. El build de servicios y shell es ligero. La build de `llama.cpp` CPU requiere su propio árbol ignorado y un modelo GGUF local verificado. Una build completa de Gecko no debe ejecutarse en un entorno pequeño: Mozilla documenta al menos 4 GiB de RAM, recomienda 8 GiB y requiere aproximadamente 30 GiB libres para Linux.

## Build del userland

Desde la raíz del repositorio:

```bash
python3 tools/eos_build.py --configuration Debug --jobs 2 --skip-initramfs
```

El comando configura CMake, compila todos los targets C++ de EOS, compila el fixture EosLang, audita las aplicaciones fuente y escribe `build/engine/build-manifest.json`. El manifiesto contiene la revisión Git, los targets y la política `source_only=true`.

También se pueden usar presets:

```bash
cmake --preset eos-debug
cmake --build --preset eos-debug-build
```

## Pruebas

```bash
python3 tests/test_eos.py
python3 tools/eos_service_graph.py config/eos-services.json --all
cmake --build build/cmake -j2
```

Los servicios disponen de `--self-test`; por ejemplo:

```bash
build/cmake/eos-deviced --self-test
build/cmake/eos-windowd --self-test
build/cmake/eos-modeld --self-test
build/cmake/eos-browserd --self-test
```

## Hi Eaid

La revisión local de `llama.cpp` y el modelo Qwen2.5 0.5B Q4_K_M no se guardan en Git. El flujo requiere preflight GGUF, SHA-256, manifiesto y ejecución offline:

```bash
python3 tools/eos_gguf_validate.py build/models/qwen2.5-0.5b-instruct-q4_k_m.gguf --sha256 <sha256>
python3 tools/eos_llama_backend.py "Hola desde EOS" \
  --model build/models/qwen2.5-0.5b-instruct-q4_k_m.gguf \
  --sha256 <sha256> --context-size 512 --gpu-layers 0 --run
```

El modelo se descargó con autorización explícita y quedó fuera del repositorio. El broker mantiene las descargas desactivadas durante el runtime.

## Browser

EOS Browser se construye como app fuente EosLang/EOSBC y solicita una sesión a `eos-browserd`. El bridge Gecko se ejecuta en modo plan-only por defecto. El motor Gecko real necesita un checkout Mozilla interno, revisión fija, toolchain y almacenamiento suficiente; no se debe copiar un Firefox Linux arbitrario dentro de una app `.eapp`.

## Publicación

No usar `gh release create`. No subir `.img`, `.edisk`, `.eapp` generado, `.gguf`, claves privadas ni builds. Antes de cada commit:

```bash
git diff --check
git status --short
gh release list --repo JesusQuijada34/eosimg
```

El resultado esperado para releases sigue siendo `no releases found`.
