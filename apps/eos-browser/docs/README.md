# EOS Browser

EOS Browser es la superficie de navegación de Etternhall Operating System. El paquete fuente no incluye un navegador Linux ni una copia de Safari. La UI pertenece a EOS y solicita sesiones al servicio `eos-browserd`; el motor Gecko será un componente interno separado, revisado, firmado y aislado.

El permiso de red es de consentimiento y política por página. Las descargas pasan por `eos_downloads.py`, con destino lógico, confirmación y SHA-256. El paquete no puede abrir rutas `file://` ni cargar ELF Linux de usuario.

Este directorio contiene código fuente EosLang, manifiesto y recursos. El `.eapp` generado, las claves y el motor Gecko no se versionan.
