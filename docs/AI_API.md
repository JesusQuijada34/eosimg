# EOS Intelligence API 0.1

EOS ofrecerá asistentes y capacidades de machine learning mediante servicios del sistema, no como permisos implícitos de todas las aplicaciones. La API pública inicial se llamará `eos-ai-0.1`.

## Servicios

| Servicio | Función | Requisito |
|---|---|---|
| `eos-assistantd` | Conversación, acciones y contexto | permiso `assistant.invoke` |
| `eos-inference` | Inferencia de modelos locales | permiso `ml.inference` |
| `eos-speechd` | Voz a texto y texto a voz | permisos de micrófono/salida |
| `eos-keyboardd` | Predicción y composición del teclado | consentimiento del usuario |
| `eos-modeld` | Registro, versión y carga de modelos | modelos firmados |

## Principios

Los modelos se tratarán como recursos versionados y verificables, con límites de memoria, CPU y almacenamiento. Las aplicaciones no obtendrán el contenido de conversaciones, audio o teclado salvo consentimiento y permiso específico. El modo local será la opción predeterminada; la comunicación con servicios remotos será una extensión separada que requerirá configuración y consentimiento.

La primera implementación será un contrato y un stub de servicio que devuelva capacidades disponibles. No se incorporará un modelo grande al sistema base ni se enviarán datos del usuario durante las pruebas.

## Evolución

La API se versionará junto con `.eapp` y EosLang. Si EosLang cambia de forma incompatible, el paquete declarará la API requerida y el instalador rechazará el paquete o utilizará una capa de adaptación documentada.
