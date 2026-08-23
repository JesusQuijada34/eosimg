# Etternhall Operating System (EOS)

**Estado:** especificación inicial de arquitectura 0.1  
**Autor:** Manus AI  
**Lenguajes base:** C++20/23, Python 3.11+, Qt 6  
**Núcleo base:** Linux, con userland y servicios propios de EOS  
**Objetivo:** ofrecer una experiencia de teléfono tipo iPhone en PC mediante una plataforma original, arrancable y extensible.

> EOS no redistribuirá una imagen de iOS ni copiará frameworks, marcas, recursos o componentes propietarios de Apple. La compatibilidad con `.ipa` se tratará como un proyecto de ingeniería independiente y limitado a software autorizado por sus titulares.

## 1. Alcance realista

EOS será una distribución/plataforma basada en Linux, no un kernel completamente nuevo. El kernel Linux aportará planificación, memoria virtual, procesos, dispositivos, red, almacenamiento y seguridad de bajo nivel. La identidad propia estará en el arranque, el userland, el gestor de paquetes, la interfaz, el lenguaje, el SDK, el runtime de aplicaciones y los servicios de dispositivo.

La ejecución de `.ipa` no se conseguirá simplemente cambiando la extensión o descomprimiendo el archivo. Un `.ipa` suele contener un bundle con metadatos y un ejecutable Mach-O que espera un ABI de Apple, un runtime Objective-C/Swift, frameworks y servicios que no existen en Linux. EOS implementará un **EOS Apple Compatibility Runtime (EACR)** nativo, compuesto por un cargador Mach-O, un runtime Objective-C compatible en lo necesario y una superficie de APIs propia. El primer objetivo serán apps de prueba creadas por el equipo, no la compatibilidad universal con apps comerciales.

## 2. Arquitectura por capas

| Capa | Componente EOS | Responsabilidad | Primera versión |
|---|---|---|---|
| Hardware físico | PC x86-64 | CPU, GPU, RAM, disco, audio, red, pantalla | Soporte x86-64 |
| Kernel | Linux configurado por EOS | Procesos, memoria, drivers, seguridad | Kernel LTS |
| Arranque | EOS Boot | UEFI, selección de sistema, recuperación | UEFI + initramfs |
| Servicios base | EOS Core Services | IPC, permisos, sesiones, energía, red y almacenamiento | C++ |
| Gráficos | EOS Display + Qt 6 | Compositor, ventanas, gestos, escalado y teclado | Wayland/Qt 6 |
| Shell | EOS Phone Shell | Escritorio de teléfono, launcher, multitarea y ajustes | Qt 6/QML |
| Apps | EOS App Runtime | Ciclo de vida, sandbox, permisos y notificaciones | `.eapp` |
| Compatibilidad | EACR | `.ipa`, Mach-O y APIs limitadas | Experimental |
| Desarrollo | EOS SDK + EosLang | Lenguaje propio, compilador, linker y herramientas | Host Linux |
| Distribución | EPK/EAPP Manager | Repositorios, firma, actualización y rollback | Python + C++ |

## 3. Emulación vertical y compatibilidad horizontal

En EOS, **emulación vertical** significará reproducir el flujo completo de la plataforma: hardware virtual o físico, firmware, kernel, drivers, servicios, compositor, runtime y aplicación. No se pretende que la primera versión traduzca cada componente de un SoC Apple real; se utilizarán dispositivos PC estándar y un modelo abstracto de dispositivo móvil.

**Compatibilidad horizontal** significará traducir interfaces entre ecosistemas en un mismo nivel. Por ejemplo, EACR puede recibir una llamada de una app compatible, resolverla en una biblioteca EOSKit, convertir eventos táctiles a eventos Qt y utilizar los servicios EOS de archivos, red, audio, cámara o notificaciones. Esta estrategia reduce el alcance y permite avanzar por APIs medibles.

## 4. Perfil de hardware EOS-M+

El nombre **EOS-M+** designará una familia de perfiles abstractos, no una copia de un chip Apple. El perfil inicial podrá describir:

| Perfil | Uso | Modelo inicial |
|---|---|---|
| `EOS-M+ Performance` | Cargas intensivas | Núcleos AArch64 conceptuales o hilos host x86-64 |
| `EOS-M+ Efficiency` | Servicios de fondo | Núcleos de bajo consumo simulados por políticas del scheduler |
| `EOS-M+ Secure` | Claves, identidad y arranque | TPM/secure storage del PC, sin copiar Secure Enclave |
| `EOS-M+ Control` | Energía, sensores y periféricos | Microcontrolador M-profile abstracto o servicio determinista |
| `EOS-M+ Media` | Audio, vídeo y cámara | Interfaces virtuales sobre PipeWire/V4L2/VA-API |

La implementación no afirmará ser compatible con instrucciones o periféricos privados de Apple. Cuando se requiera arquitectura ARM64, se añadirá un backend de traducción de instrucciones o un destino de compilación separado; eso será un componente del runtime, no el sistema operativo completo.

## 5. Modelo de hardware y circuitos

Los transformadores, resistencias, reguladores, batería y sensores se representarán en una biblioteca de simulación eléctrica separada de los drivers. La biblioteca incluirá un solver de circuitos para redes resistivas mediante análisis nodal, modelos de fuentes, capacitores, inductores, transformadores ideales y pérdidas, límites térmicos y estados de batería. Los servicios de EOS consumirán lecturas de esa simulación como si fueran sensores del dispositivo.

Esto permite dos modos:

1. **Modo físico:** usar los dispositivos reales del PC y exponer solo las abstracciones móviles.
2. **Modo laboratorio:** simular alimentación, temperatura, carga, sensores y fallos para probar el comportamiento de EOS de forma reproducible.

## 6. Lenguaje EosLang

El lenguaje propio se llamará provisionalmente **EosLang**. El compilador se dividirá en lexer, parser, AST, verificador semántico, IR, optimizador, backend y empaquetador. La primera implementación podrá compilar a LLVM IR o C++ como backend provisional, mientras la sintaxis, el type system y el modelo de paquetes se estabilizan. Una etapa posterior podrá añadir un backend nativo para EOS.

El lenguaje deberá incluir tipos estáticos, módulos, manejo explícito de errores, concurrencia estructurada, FFI controlada con C/C++ y anotaciones para permisos de aplicación. Python se utilizará en herramientas de prototipado, generación de metadatos y pruebas; C++ será el lenguaje de los componentes de sistema y runtime; Qt 6 será la base del shell y SDK gráfico.

## 7. Formato `.eapp`

`.eapp` será un contenedor versionado y reproducible, no un binario opaco sin especificación. El paquete tendrá una cabecera identificable, manifiesto, recursos, bytecode o binario, permisos declarados, firma, hash de contenido y datos opcionales de actualización. La compresión podrá ser zstd y el cifrado solo se usará para secretos o contenido con autorización; la ofuscación no debe sustituir la criptografía ni el control de acceso.

Ejemplo conceptual:

```text
EAPP-1
├── manifest.toml
├── payload/eos-x86_64/app.bin
├── payload/eos-arm64/app.bin
├── resources/
├── permissions.cbor
├── signature.ed25519
└── content.sha256
```

El gestor de paquetes verificará tamaño, límites de extracción, rutas seguras, hashes, firma y permisos antes de instalar. Se evitarán técnicas diseñadas para ocultar malware, evadir análisis de seguridad o persistir sin consentimiento.

## 8. Protección antiingeniería inversa

EOS podrá ofrecer protección legítima para propiedad intelectual mediante firma de código, verificación de integridad, compilación reproducible, eliminación controlada de símbolos, cifrado de secretos fuera del binario, separación de módulos sensibles, hardening del loader y actualización revocable. La ofuscación puede elevar el coste del análisis, pero no hace que un programa sea imposible de descompilar, especialmente si debe ejecutarse en el equipo del usuario.

## 9. Orden recomendado de desarrollo

La primera entrega técnica no intentará ejecutar una app comercial arbitraria. Construirá un sistema de arranque mínimo, shell Qt 6, formato `.eapp`, una app EosLang de demostración y una herramienta de análisis que abra un `.ipa` sin ejecutarlo. Después se añadirá un loader Mach-O para binarios de prueba controlados. La compatibilidad con UIKit/SwiftUI, servicios de Apple y apps comerciales quedará explícitamente fuera del MVP hasta que existan pruebas técnicas y autorizaciones adecuadas.

## 10. Criterios del MVP

| Criterio | Resultado esperado |
|---|---|
| Arranque | EOS inicia desde ISO/USB en PC x86-64 o máquina virtual de desarrollo |
| Shell | Interfaz táctil/ratón tipo teléfono, original y funcional |
| Paquetes | Instalar, ejecutar, actualizar y desinstalar un `.eapp` firmado |
| Lenguaje | Compilar una app EosLang con UI Qt 6 mínima |
| Seguridad | Sandbox, permisos, hashes y firma verificada |
| IPA | Inspeccionar bundle y Mach-O; ejecutar solo una app de prueba compatible |
| Circuitos | Simular una red de alimentación y exponer telemetría al shell |
| Portabilidad | Ejecutor `.eapp` preliminar en Linux; Windows después del MVP |

## Referencias técnicas

[1]: https://www.darlinghq.org/ "Darling: capa de traducción macOS para Linux"
[2]: https://docs.darlinghq.org/ "Darling Docs"
[3]: https://developer.apple.com/documentation/bundleresources/entitlements "Apple: Entitlements"
[4]: https://developer.apple.com/documentation/technotes/tn3125-inside-code-signing-provisioning-profiles "Apple TN3125: Inside Code Signing: Provisioning Profiles"
[5]: https://developer.apple.com/library/archive/documentation/Performance/Conceptual/CodeFootprint/Articles/MachOOverview.html "Apple: Overview of the Mach-O Executable Format"
[6]: https://developer.apple.com/documentation/objectivec/objective-c-runtime "Apple: Objective-C Runtime"
[7]: https://www.qemu.org/docs/master/system/target-arm.html "QEMU: Arm System Emulator"


## 11. Referencia arquitectónica tipo Android

AOSP sirve como referencia de organización, no como código a copiar. Su documentación separa kernel, HAL, demonios y bibliotecas nativas, runtime y framework de aplicación. EOS adoptará el mismo principio de capas con nombres, APIs y contratos propios:

| Patrón de referencia | Equivalente EOS |
|---|---|
| Linux kernel | EOS Linux Kernel Base |
| Hardware Abstraction Layer | EOS Device Abstraction Layer (EDAL) |
| init y demonios nativos | `eos-init`, `eos-logd`, `eos-storaged`, `eos-powerd` |
| Runtime de aplicaciones | EosRuntime + EACR para compatibilidad experimental |
| Framework de aplicación | EOS Foundation / EOSKit |
| Apps | `.eapp` y, en una superficie limitada, `.ipa` autorizados |

El modelo confirma que EOS puede ser una plataforma propia aun usando Linux como kernel. El trabajo principal estará en los contratos entre capas, el ciclo de vida de apps, los permisos, la actualización del sistema y el SDK, no en reescribir desde cero todas las funciones que ya proporciona Linux.

Fuente: https://source.android.com/docs/core/architecture


## 12. Consideración sobre Swift

Swift añade una capa de compatibilidad distinta de Objective-C. Su ABI abarca layout de tipos, metadatos, símbolos mangled, convenciones de llamada, runtime y biblioteca estándar. Por eso el MVP de EACR no prometerá ejecutar cualquier aplicación Swift ya compilada. El camino práctico será soportar primero apps `.eapp` nativas y después aplicaciones de prueba `.ipa` Objective-C/arm64 controladas; el soporte Swift se evaluará por versiones concretas del runtime y por un catálogo explícito de APIs.

Fuente: https://github.com/swiftlang/swift/blob/main/docs/ABIStabilityManifesto.md
