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

<h3 align="center">Un client GUI Kafka moderno e pratico</h3>

</div>
<h4 align="center">
<a href="../../readme.md">English</a> | <a href="../../README-CN.md">简体中文</a> | <a href="readme-ja.md">日本語</a> | <a href="readme-ru.md">рускі</a> | <a href="readme-ko.md">한국인</a> | <a href="readme-es.md">Español</a> | <a href="readme-fr.md">Français</a> | <a href="readme-de.md">Deutsch</a> | <a href="readme-pt.md">Português</a> | <a href="readme-it.md">Italiano</a> | <a href="readme-vi.md">Tiếng Việt</a> | <a href="readme-id.md">Bahasa Indonesia</a>  
</h4>

Rendi Kafka più facile da usare, make kafka great again!

Questo progetto è un client GUI Kafka compatibile con vari sistemi desktop (eccetto Win7), supporta Kafka 0.8.0 fino a 3.8+, costruito con Wails e franz-go. Metti una stella per supportare l'autore! ❤❤

> Dai un'occhiata anche al client Elasticsearch `ES-King`, altrettanto pratico: https://github.com/Bronya0/ES-King

**Doc（AI）**：[https://zread.ai/Bronya0/Kafka-King](https://zread.ai/Bronya0/Kafka-King)

# Funzionalità di Kafka-King
- [x] Visualizzazione elenco nodi del cluster, configurazione dinamica di broker e topic.
- [x] Supporto client consumatore, consumo di topic con gruppo, dimensione e timeout, dettagli in tabella.
- [x] Supporto per PLAIN, SSL, SASL, Kerberos, sasl_plaintext, ecc.
- [x] Supporto compressione/decompressione gzip, lz4, snappy, zstd.
- [x] Creazione (lotti supportati) ed eliminazione topic, specifica repliche e partizioni.
- [x] Statistiche su messaggi totali, offset confermati e accumulo per gruppo consumatore.
- [x] Dettagli partizioni (offset), supporto aggiunta partizioni extra.
- [x] Simulazione produttore, invio messaggi in lotto con header e partizione.
- [x] Controllo salute topic e partizioni (completato).
- [x] Visualizzazione gruppi consumatori e consumatori individuali.
- [x] Report ispezione offset.
- [x] Supporto Schema Registry: gestione di Subject/versioni, compatibilità e decodifica messaggi Avro, JSON e Protobuf.
- [x] Consumo in streaming multiplo: streaming in tempo reale, ordine inverso, gestione schede e commit degli offset.
- [x] Ripristino degli offset dei gruppi: ripristino su Start (più vecchi), End (più recenti), timestamp o offset specifico.
- [x] Eliminazione messaggi (DeleteRecords): cancellazione messaggi per partizione o intero topic fino all'offset specificato.
- [x] Riassegnazione repliche di partizione: ispezione visiva e modifica delle repliche, con supporto all'annullamento.
- [x] Vista nodi avanzata: indicatore Controller, analisi spazio disco LogDirs e gestione quote client.
- [x] Importazione ed esportazione connessioni: esportazione in YAML e importazione da YAML/JSON con deduplicazione.
- [x] Autenticazione estesa: supporto OAUTHBEARER (token statico), AWS MSK IAM e tunneling SSH per più broker.
- [x] Riproduzione ed esportazione messaggi: reinvio messaggi selezionati ad altri topic ed esportazione in JSON/CSV.

# Download
Scarica dal lato destro o visita la [pagina delle release](https://github.com/Bronya0/Kafka-King/releases). Espandi 【Assets】 e scegli la versione adatta alla tua piattaforma: Windows, macOS, Linux.

**Utenti macOS: se l'app mostra "danneggiata" all'apertura, esegui `xattr -dr com.apple.quarantine /Applications/Kafka-King.app` nel terminale (l'app non è firmata ed è bloccata da Gatekeeper).**

`Note importanti:`
1. **Prima dell'uso, assicurati che l'impostazione `advertised.listeners` del tuo cluster Kafka sia corretta. Se non configurata o se usa nomi di dominio, aggiungi la risoluzione corrispondente nel file hosts del tuo computer.**
2. **Se la connessione richiede SSL, abilita TLS e disabilita la verifica a meno che tu non abbia un certificato, nel qual caso abilita la verifica TLS e fornisci il percorso del certificato.**
3. **Gli utenti SASL devono abilitare SASL, selezionare il protocollo SASL appropriato (di solito plain) e inserire utente e password.**
4. **In caso di errori di runtime webview2, scarica e reinstalla il runtime dal sito ufficiale Microsoft: https://developer.microsoft.com/it-it/microsoft-edge/webview2**


# Compilazione
La compilazione manuale è necessaria solo per studiare il codice sorgente.

cd app

wails dev

# Licenza
Licenza Apache-2.0

# Ringraziamenti
- wails: https://wails.io/docs/gettingstarted/installation
- naive ui: https://www.naiveui.com/
- franz-go: https://github.com/twmb/franz-go/
- xicons: https://xicons.org/#/

# Traduzione
Supporta cinese, giapponese, inglese, coreano, russo e altre lingue.

Correggere o aggiungere una nuova lingua: https://github.com/Bronya0/Kafka-King/issues/51
