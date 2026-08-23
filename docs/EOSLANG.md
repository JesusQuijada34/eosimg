# EosLang 0.1

EosLang es el lenguaje propio de EOS para describir aplicaciones y servicios. La primera versión es deliberadamente pequeña: sirve para validar el pipeline de compilación antes de diseñar un lenguaje general completo.

## Sintaxis inicial

```text
app com.etternhall.hello
version "0.1.0"
let title = "Etternhall"
text "Hola desde EOS"
print title
end
```

El compilador produce un bytecode JSON con versión, nombre de aplicación e instrucciones. El bytecode no es todavía una ABI estable y no debe considerarse un formato final de distribución. El futuro backend podrá producir `.eapp`, LLVM IR o código nativo según el destino.

## Decisiones

| Elemento | Decisión 0.1 |
|---|---|
| Frontend | Parser línea a línea con errores de línea claros |
| Tipos | String y entero como base experimental |
| Backend | Bytecode JSON legible para depuración |
| Runtime | Intérprete de referencia Python |
| Integración | C++/Qt 6 después de estabilizar la gramática |
| Seguridad | El compilador no ejecuta código del fuente |
