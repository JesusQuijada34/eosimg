# Auditoría de integración local

## Resultado

La rama `main` está limpia en el commit `0b37b35`. Los contratos EOS `eos-assistantd`, `eos-browserd` y `eos-immersived` compilan, pero son servicios de protocolo/prototipo.

| Componente | Estado local | Consecuencia |
|---|---|---|
| `llama-cli`/`main` de llama.cpp | No instalado | Hay que integrar una build reproducible antes de ejecutar inferencia |
| Firefox de escritorio | No instalado | No se puede reutilizar un ELF Linux como aplicación EOS |
| `geckodriver` | No instalado | No sirve como sustituto de Gecko embebido |
| Modelos `.gguf`/`.safetensors` del proyecto | Ninguno | No se descarga nada automáticamente; la prueba inicial será con fixtures pequeños o un modelo suministrado por el usuario |
| RAM del sandbox | 3.8 GiB total, aproximadamente 2.9 GiB disponible | El sandbox solo permite compilar y hacer pruebas pequeñas; no es un dispositivo de inferencia grande |
| Artefactos publicables | Ninguno requerido | Se mantienen fuera de Git mediante `.gitignore` |

## Decisiones inmediatas

La integración de `llama.cpp` debe comenzar como dependencia fijada por commit/tag y una build CLI compartible; después se añadirá una biblioteca/adaptador de inferencia EOS que solo acepte modelos locales verificados. La descarga desde Hugging Face permanecerá separada en un Model Store con consentimiento, revisión de licencia, revisión fijada, hash y presupuesto de RAM/almacenamiento.

La integración Gecko no debe consistir en instalar Firefox para Linux. Primero se construirá una matriz de opciones: GeckoView como referencia de embedding orientada a Android, una build controlada de Gecko/Mozilla para el target EOS si es mantenible, o un backend WebKit con licencia compatible. `eos-browserd` permanecerá como frontera EOS y el motor se conectará detrás de ella mediante un bridge de procesos.

## Limitación del sandbox

El sandbox es adecuado para configurar, compilar y probar contratos. No contiene un modelo de inferencia ni una build Gecko y no representa hardware EOS. Para medir rendimiento real será necesario ejecutar posteriormente en un equipo local con la RAM/arquitectura objetivo; esta sesión no tiene una carpeta del usuario vinculada.
