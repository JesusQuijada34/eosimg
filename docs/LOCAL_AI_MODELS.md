# IA local de EOS y selección de modelos

## Decisión de arquitectura

EOS usará un **Model Broker** propio. El broker no descargará ni ejecutará un modelo arbitrario por el nombre del repositorio: primero resolverá una revisión fija, comprobará el manifiesto, validará hashes, revisará la licencia y elegirá un backend permitido.

Hugging Face documenta GGUF como un formato binario optimizado para carga rápida e inferencia y señala que incluye tensores y metadatos estandarizados [1]. La documentación también presenta SafeTensors como un formato recomendado y más seguro de cargar que serializaciones tradicionales basadas en pickle [2]. Por ello, EOS soportará inicialmente GGUF para backends C/C++ locales y SafeTensors únicamente mediante un loader controlado y revisado.

La carga de modelos grandes no depende solo del tamaño del archivo. Transformers explica que el uso de memoria puede incluir pesos, inicialización, activaciones y dispositivos disponibles [2]. Accelerate permite distribuir pesos entre GPU, RAM y disco, pero el offload a disco intercambia memoria por velocidad y no debe presentarse como una solución de tiempo real [3]. El selector de EOS aplicará un margen de seguridad y nunca intentará llenar toda la RAM disponible.

## Perfil de recursos

| Señal | Fuente prevista | Uso |
|---|---|---|
| RAM total y libre | `/proc/meminfo` o servicio EDAL | límite de carga |
| Arquitectura | `uname`/EDAL | filtro x86-64/ARM64 |
| GPU/NPU y memoria | EDAL/backend | aceleración opcional |
| Espacio disponible | `eos-storaged` | caché y modelos |
| Batería/temperatura | `eos-powerd`/EDAL | modo ahorro |
| Conectividad | `eos-networkd` | descarga solo con consentimiento |

El presupuesto del modelo será el menor entre la RAM libre utilizable, el límite del backend y el espacio disponible para caché. EOS reservará memoria para el sistema, la aplicación y el contexto. Como regla inicial de producto, se reservará al menos un 35 % de la RAM total para el sistema y se usará como máximo el 50 % de la RAM total para pesos y runtime de IA; son límites conservadores de EOS, no garantías universales de rendimiento.

## Escalones iniciales

| RAM total | Perfil EOS | Modelo preferido | Contexto inicial |
|---:|---|---|---:|
| 2–3 GiB | `tiny` | 0.5–1.5B, Q4/Q5 | 2k |
| 4–7 GiB | `small` | 1.5–3B, Q4/Q5 | 4k |
| 8–15 GiB | `medium` | 3–7B, Q4/Q5 | 8k |
| 16–31 GiB | `large` | 7–14B, Q4/Q5 | 8k–16k |
| 32 GiB o más | `xlarge` | selección por backend/GPU | política dinámica |

Estos escalones solo son un filtro de seguridad. El broker debe consultar el tamaño real del archivo, metadatos del modelo, cuantización, contexto y memoria del backend antes de cargarlo.

## Seguridad y privacidad

La descarga se hará a un caché EOS con revisión fijada, hash SHA-256, tamaño máximo y espacio reservado. No se usará `trust_remote_code` por defecto. La documentación de Transformers advierte que los modelos personalizados pueden incluir código ajeno y recomienda fijar una revisión concreta si se habilita ese modo [2]; EOS lo deshabilitará en el asistente de producción.

El asistente local tendrá permisos separados para texto, micrófono, cámara, archivos, red e imágenes. El modo local no enviará datos a Hugging Face ni a otro proveedor durante la inferencia. Hugging Face será un origen de modelos, no un servicio obligatorio en tiempo de ejecución.

## Referencias

[1]: https://huggingface.co/docs/hub/en/gguf "Hugging Face Hub: GGUF"
[2]: https://huggingface.co/docs/transformers/en/models "Hugging Face Transformers: Loading models"
[3]: https://huggingface.co/docs/accelerate/en/concept_guides/big_model_inference "Hugging Face Accelerate: Loading big models into memory"
[4]: https://github.com/ggml-org/llama.cpp "ggml-org/llama.cpp"
