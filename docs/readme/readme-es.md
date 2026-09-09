<p align="center">
  <img src="../../app/build/appicon.png" width="200" alt="Image">
</p>
<h1 align="center">Kafka King </h1>

<div align="center">

![License](https://img.shields.io/github/license/Bronya0/Kafka-King)
![GitHub release](https://img.shields.io/github/release/Bronya0/Kafka-King)
![GitHub All Releases](https://img.shields.io/github/downloads/Bronya0/Kafka-King/total)
![GitHub stars](https://img.shields.io/github/stars/Bronya0/Kafka-King)
![GitHub forks](https://img.shields.io/github/forks/Bronya0/Kafka-King.svg?style=flat-square)

<h3 align="center">Un cliente GUI de Kafka moderno y práctico</h3>

</div>
<h4 align="center">
<a href="../../readme.md">English</a> | <a href="../../README-CN.md">简体中文</a> | <a href="readme-ja.md">日本語</a> | <a href="readme-ru.md">рускі</a> | <a href="readme-ko.md">한국인</a> | <a href="readme-es.md">Español</a> | <a href="readme-fr.md">Français</a> | <a href="readme-de.md">Deutsch</a> | <a href="readme-pt.md">Português</a> | <a href="readme-it.md">Italiano</a> | <a href="readme-vi.md">Tiếng Việt</a> | <a href="readme-id.md">Bahasa Indonesia</a>  
</h4>

Haga que Kafka sea más fácil de usar, ¡make kafka great again!

Este proyecto es un cliente GUI de Kafka compatible con varios sistemas de escritorio (excepto Win7), compatible con Kafka 0.8.0 hasta 3.8+, construido con Wails y franz-go. ¡Dale una estrella para apoyar al autor! ❤❤

> También puede consultar el cliente de Elasticsearch `ES-King`, igualmente práctico: https://github.com/Bronya0/ES-King

**Doc（AI）**：[https://zread.ai/Bronya0/Kafka-King](https://zread.ai/Bronya0/Kafka-King)

# Características de Kafka-King
- [x] Ver lista de nodos del clúster, soporte para configuración dinámica de brokers y topics.
- [x] Soporte para cliente consumidor, consumir mensajes de topics específicos con grupo, tamaño y timeout, mostrando detalles en tabla.
- [x] Soporte para PLAIN, SSL, SASL, Kerberos, sasl_plaintext, etc.
- [x] Soporte para compresión y descompresión gzip, lz4, snappy, zstd.
- [x] Crear (soporta lotes) y eliminar topics, especificar réplicas y particiones.
- [x] Estadísticas de mensajes totales, offset confirmado y acumulación por grupo consumidor.
- [x] Información detallada de particiones (offsets), soporte para añadir particiones adicionales.
- [x] Simular productor, enviar mensajes en lote con cabeceras y partición específica.
- [x] Verificación de salud de topics y particiones (completado).
- [x] Visualización de grupos de consumidores y consumidores individuales.
- [x] Informe de inspección de offsets.
- [x] Compatibilidad con Schema Registry: gestión de Subject/versiones, compatibilidad y decodificación Avro, JSON y Protobuf.
- [x] Consumo en streaming múltiple: consumo en tiempo real de múltiples flujos, orden inverso, pestañas y commit de offsets.
- [x] Restablecimiento de offsets de grupos: restablecimiento a Start (más antiguos), End (más recientes), marca de tiempo u offset específico.
- [x] Purga de mensajes (DeleteRecords): eliminación de mensajes por partición o en todo el topic hasta el offset indicado.
- [x] Reasignación de réplicas de particiones: inspección y ajuste visual de réplicas, con soporte para cancelación.
- [x] Inspección de nodos mejorada: indicador de Controller, análisis de espacio en disco LogDirs y gestión de cuotas de clientes.
- [x] Importación y exportación de conexiones: exportación a YAML e importación desde YAML/JSON con deduplicación inteligente.
- [x] Autenticación extendida: soporte para OAUTHBEARER (token estático), AWS MSK IAM y túneles SSH para múltiples brokers.
- [x] Reproducción y exportación de mensajes: reenviar mensajes seleccionados a otros topics y exportar a JSON/CSV.

# Descarga
Descargue desde la derecha o visite la [página de versiones](https://github.com/Bronya0/Kafka-King/releases). Despliegue 【Assets】 y elija la versión adecuada para su plataforma: Windows, macOS, Linux.

**Usuarios de macOS: si la aplicación muestra "dañada" al abrirla, ejecute `xattr -dr com.apple.quarantine /Applications/Kafka-King.app` en la terminal (la app no está firmada y está bloqueada por Gatekeeper).**

`Notas importantes:`
1. **Antes de usar, asegúrese de que la configuración `advertised.listeners` de su clúster Kafka sea correcta. Si no está configurada o usa nombres de dominio, agregue la resolución correspondiente en el archivo hosts de su máquina local.**
2. **Si su conexión requiere SSL, habilite TLS y desactive la verificación a menos que tenga un certificado, en cuyo caso habilite la verificación TLS y proporcione la ruta del certificado.**
3. **Los usuarios de SASL deben habilitar SASL, seleccionar el protocolo SASL adecuado (generalmente plain) e ingresar usuario y contraseña.**
4. **Si encuentra errores de webview2, descargue y reinstale el runtime desde el sitio web oficial de Microsoft: https://developer.microsoft.com/en-us/microsoft-edge/webview2**


# Compilación
Solo se necesita compilación manual para estudiar el código fuente.

cd app

wails dev

# Licencia
Licencia Apache-2.0

# Agradecimientos
- wails: https://wails.io/docs/gettingstarted/installation
- naive ui: https://www.naiveui.com/
- franz-go: https://github.com/twmb/franz-go/
- xicons: https://xicons.org/#/

# Traducción
Soporta chino, japonés, inglés, coreano, ruso y otros idiomas.

Corregir o añadir nuevo idioma: https://github.com/Bronya0/Kafka-King/issues/51
