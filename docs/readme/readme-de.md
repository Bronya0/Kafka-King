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

<h3 align="center">Ein moderner, praktischer Kafka-GUI-Client</h3>

</div>
<h4 align="center">
<a href="../../readme.md">English</a> | <a href="../../README-CN.md">简体中文</a> | <a href="readme-ja.md">日本語</a> | <a href="readme-ru.md">рускі</a> | <a href="readme-ko.md">한국인</a> | <a href="readme-es.md">Español</a> | <a href="readme-fr.md">Français</a> | <a href="readme-de.md">Deutsch</a> | <a href="readme-pt.md">Português</a> | <a href="readme-it.md">Italiano</a> | <a href="readme-vi.md">Tiếng Việt</a> | <a href="readme-id.md">Bahasa Indonesia</a>  
</h4>

Machen Sie Kafka einfacher zu bedienen, make kafka great again!

Dieses Projekt ist ein Kafka-GUI-Client, der auf verschiedenen Desktopsystemen (außer Win7) läuft und Kafka 0.8.0 bis 3.8+ unterstützt, basierend auf Wails und franz-go. Gib einen Star, um den Autor zu unterstützen! ❤❤

> Auch der praktische Elasticsearch-Client `ES-King` ist einen Blick wert: https://github.com/Bronya0/ES-King

**Doc（AI）**：[https://zread.ai/Bronya0/Kafka-King](https://zread.ai/Bronya0/Kafka-King)

# Kafka-King Funktionen
- [x] Cluster-Knotenliste anzeigen, dynamische Broker- und Topic-Konfiguration.
- [x] Consumer-Client: Nachrichten von Topics mit Gruppe, Größe und Timeout konsumieren, Details in Tabellenform.
- [x] Unterstützung für PLAIN, SSL, SASL, Kerberos, sasl_plaintext, etc.
- [x] gzip-, lz4-, snappy-, zstd-Kompression und -Dekompression.
- [x] Topics erstellen (Batch-Support) und löschen, Replikate und Partitionen festlegen.
- [x] Statistiken zu Nachrichtenanzahl, bestätigten Offsets und Rückstau pro Consumer-Gruppe.
- [x] Detaillierte Partitionsinformationen (Offsets), zusätzliche Partitionen hinzufügbar.
- [x] Producer simulieren, Batch-Nachrichten mit Headern und Partition versenden.
- [x] Topic- und Partitions-Gesundheitsprüfung (abgeschlossen).
- [x] Consumer-Gruppen und einzelne Consumer anzeigen.
- [x] Offsets-Prüfbericht.
- [x] Schema Registry Unterstützung: Verwaltung von Subjects/Versionen, Kompatibilitätseinstellungen, Avro/JSON/Protobuf-Dekodierung.
- [x] Multi-Stream-Konsumierung: Echtzeit-Streaming mit mehreren Streams, umgekehrte Sortierung, Tab-Verwaltung und Offset-Commits.
- [x] Verbrauchergruppen-Offset-Reset: Zurücksetzen auf Start (früheste), End (neueste), Zeitstempel oder spezifischen Offset.
- [x] Nachrichtenbereinigung (DeleteRecords): Löschen von Datensätzen bis zu Ziel-Offsets für einzelne oder alle Partitionen.
- [x] Partitionsreplik-Neuzuweisung: Visuelle Überprüfung und Anpassung der Repliken mit Abbruchfunktion.
- [x] Erweiterte Knotenübersicht: Controller-Kennzeichnung, LogDirs-Speicherplatzanalyse und Client-Quotas-Verwaltung.
- [x] Verbindungskonfiguration Import/Export: Export als YAML und Import aus YAML/JSON mit automatischer Deduplizierung.
- [x] Erweiterte Authentifizierung: Unterstützung für OAUTHBEARER (statischer Token), AWS MSK IAM und Multi-Broker SSH-Tunnel.
- [x] Wiedergabe und Export von Nachrichten: Erneutes Senden ausgewählter Nachrichten an andere Topics und Export als JSON/CSV.

# Download
Laden Sie von der rechten Seite herunter oder besuchen Sie die [Release-Seite](https://github.com/Bronya0/Kafka-King/releases). Klappen Sie 【Assets】 auf und wählen Sie die passende Version für Ihre Plattform: Windows, macOS, Linux.

**macOS-Benutzer: Falls die App beim Öffnen als "beschädigt" gemeldet wird, führen Sie `xattr -dr com.apple.quarantine /Applications/Kafka-King.app` im Terminal aus (die App ist nicht signiert und wird von Gatekeeper blockiert).**

`Wichtige Hinweise:`
1. **Stellen Sie vor der Nutzung sicher, dass die `advertised.listeners`-Einstellung Ihres Kafka-Clusters korrekt ist. Falls nicht konfiguriert oder Domänen verwendet werden, fügen Sie die entsprechende Auflösung in die hosts-Datei Ihres Rechners ein.**
2. **Falls Ihre Verbindung SSL erfordert, aktivieren Sie TLS und deaktivieren Sie die Überprüfung, es sei denn, Sie haben ein Zertifikat – dann aktivieren Sie die TLS-Überprüfung und geben Sie den Zertifikatspfad an.**
3. **SASL-Benutzer müssen SASL aktivieren, das entsprechende SASL-Protokoll (normalerweise plain) auswählen und Benutzername sowie Passwort eingeben.**
4. **Bei webview2-Laufzeitfehlern laden Sie die Laufzeit von der offiziellen Microsoft-Website herunter und installieren Sie sie neu: https://developer.microsoft.com/de-de/microsoft-edge/webview2**


# Build
Manuelles Build ist nur zum Studieren des Quellcodes erforderlich.

cd app

wails dev

# Lizenz
Apache-2.0-Lizenz

# Danksagung
- wails: https://wails.io/docs/gettingstarted/installation
- naive ui: https://www.naiveui.com/
- franz-go: https://github.com/twmb/franz-go/
- xicons: https://xicons.org/#/

# Übersetzung
Unterstützt Chinesisch, Japanisch, Englisch, Koreanisch, Russisch und weitere Sprachen.

Korrigieren oder neue Sprache hinzufügen: https://github.com/Bronya0/Kafka-King/issues/51
