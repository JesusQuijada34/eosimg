# Especificación `.eapp` 0.2

## Propósito

`.eapp` es el formato de distribución de aplicaciones de Etternhall Operating System. El formato es un contenedor binario versionado con un manifiesto canónico, un payload comprimido e integridad verificable. La herramienta oficial `eapp.py` es la implementación de referencia del prototipo.

## Manifiesto

El manifiesto incluye los siguientes campos:

| Campo | Obligatorio | Significado |
|---|---:|---|
| `format` | Sí | Debe ser `eapp` |
| `format_version` | Sí | Versión del contenedor |
| `identity.bundle_id` | Sí | Identidad estable de la aplicación |
| `identity.publisher` | Sí | Entidad que publica el paquete |
| `identity.key_id` | Con firma | Identificador de la clave pública |
| `name` | Sí | Nombre de la aplicación |
| `version` | Sí | Versión de la aplicación |
| `api` | Sí | API de EosLang/EOS utilizada |
| `min_eos` | Sí | Versión mínima del sistema EOS |
| `author` | Sí | Autoría declarada |
| `license` | Sí | Licencia del contenido |
| `entrypoint` | Sí | Punto de entrada relativo al payload |
| `targets` | Sí | Arquitecturas o perfiles soportados |
| `icon` | No | Ruta del icono dentro del payload |
| `splash` | No | Ruta de la pantalla de inicio |
| `documentation` | No | Ruta de la documentación incluida |
| `permissions` | Sí | Capacidades solicitadas por la app |
| `dependencies` | Sí | Dependencias de otros paquetes |
| `compression` | Sí | Método de compresión del payload |
| `payload_sha256` | Sí | Hash de integridad del payload |
| `signature` | No en desarrollo | Firma Ed25519 y clave pública |

## Firma y confianza

La firma cubre el manifiesto sin el campo `signature` más el payload comprimido. La clave pública se incluye para permitir verificación técnica, pero una clave incluida dentro del propio paquete no crea confianza por sí sola. EOS deberá distribuir posteriormente un almacén de claves raíz o claves de repositorio confiables, con rotación y revocación.

La instalación oficial verificará, en este orden, la estructura del contenedor, los límites de tamaño, el JSON, el hash del payload, la firma, la compatibilidad de `min_eos`, el identificador, las rutas y los permisos. Los paquetes sin firma solo podrán instalarse mediante una opción explícita de desarrollo local.

## “Solo con la herramienta oficial”

El sistema puede marcar `.eapp` como formato soportado únicamente por `eos-packaged` y rechazar instalaciones directas desde el shell. Sin embargo, la especificación no debe depender de que el archivo sea imposible de leer: el sistema necesita acceder a sus metadatos y, durante la ejecución, a los recursos y código. El objetivo correcto es **integridad, autenticidad, aislamiento y resistencia al análisis**, no una promesa imposible de inviolabilidad.

## Protección de contenido

Para proteger secretos, EOS no debe incrustarlos en el paquete. Las claves privadas se mantienen fuera del paquete y los secretos se solicitan a un almacén seguro o a un servicio del usuario. El cifrado opcional en reposo puede añadirse después, con gestión de claves explícita y sin impedir la recuperación legítima del usuario.
