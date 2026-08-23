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

## Imagen de desarrollo y primer arranque

La compilación se realiza en tiempo de build; el arranque no recompila C++ ni Qt. `tools/build_initramfs.sh` genera una initramfs autónoma con BusyBox, `eos-init`, contratos de servicios, SDK, documentación y `eos-userland-manifest.json`, cuyos hashes describen los targets compilados del build local. El poblador de imagen mantiene el sistema EOS separado del ABI de aplicaciones: los ejecutables C++ copiados son componentes internos de plataforma y las aplicaciones de usuario siguen siendo paquetes firmados `.eapp` ejecutados mediante EOSBC.

```bash
# Compilar y generar el payload local
python3 tools/eos_build.py --configuration Debug --jobs 2 --skip-initramfs
tools/build_initramfs.sh
tools/build_bootable_iso.sh

# Probar el arranque normal de la ISO sin tocar el disco del anfitrión
qemu-system-x86_64 -m 512 \\
  -kernel build/vmlinuz-eos-dev -initrd build/eos-initramfs.img \\
  -append 'console=ttyS0 rdinit=/init' -nographic
```

Para probar persistencia en QEMU se usa un archivo ext4 local como disco de datos, nunca `/dev/*` del anfitrión. La initramfs reconoce las particiones EOS-DATA esperadas (`/dev/vda4` o `/dev/sda4`) y, para la prueba directa, un volumen virtio completo (`/dev/vda`) marcado con `.eos-data`.

```bash
truncate -s 64M build/eos-data-test.img
mkfs.ext4 -F build/eos-data-test.img
# Crear .eos-data y /var/lib/eos montando únicamente este archivo local.
qemu-system-x86_64 -m 512 -kernel build/vmlinuz-eos-dev \\
  -initrd build/eos-initramfs.img \\
  -append 'console=ttyS0 rdinit=/init eos.firstboot=1 eos.reboot=1' \\
  -drive file=build/eos-data-test.img,format=raw,if=virtio -nographic
```

El resultado esperado del ciclo es **una** línea de marcador comprometido, **una** solicitud de reinicio y, tras el reinicio real de QEMU con el mismo disco, una o más detecciones de `marker found`; esto demuestra que la provisión es idempotente y que el estado sobrevive al reinicio. El `reboot` se limita al invitado QEMU y no reinicia ni modifica el sandbox anfitrión. Esta evidencia sigue siendo de desarrollo: el arranque confirmado llega a la initramfs y al contrato de `eos-init`; no implica todavía que el escritorio Qt, Gecko, Studio o todos los demonios dinámicos arranquen desde la ISO.

## Publicación

No usar `gh release create`. No subir `.img`, `.edisk`, `.eapp` generado, `.gguf`, claves privadas ni builds. Antes de cada commit:

```bash
git diff --check
git status --short
gh release list --repo JesusQuijada34/eosimg
```

El resultado esperado para releases sigue siendo `no releases found`.
