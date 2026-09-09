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

<h3 align="center">Un client GUI Kafka moderne et pratique</h3>

</div>
<h4 align="center">
<a href="../../readme.md">English</a> | <a href="../../README-CN.md">简体中文</a> | <a href="readme-ja.md">日本語</a> | <a href="readme-ru.md">рускі</a> | <a href="readme-ko.md">한국인</a> | <a href="readme-es.md">Español</a> | <a href="readme-fr.md">Français</a> | <a href="readme-de.md">Deutsch</a> | <a href="readme-pt.md">Português</a> | <a href="readme-it.md">Italiano</a> | <a href="readme-vi.md">Tiếng Việt</a> | <a href="readme-id.md">Bahasa Indonesia</a>  
</h4>

Rendez Kafka plus facile à utiliser, make kafka great again!

Ce projet est un client GUI Kafka compatible avec tous les systèmes de bureau (sauf Win7), supportant Kafka 0.8.0 à 3.8+, construit avec Wails et franz-go. Mettez une étoile pour soutenir l'auteur ! ❤❤

> Consultez également le client Elasticsearch `ES-King`, tout aussi pratique : https://github.com/Bronya0/ES-King

**Doc（AI）**：[https://zread.ai/Bronya0/Kafka-King](https://zread.ai/Bronya0/Kafka-King)

# Fonctionnalités de Kafka-King
- [x] Affichage de la liste des nœuds du cluster, configuration dynamique des brokers et topics.
- [x] Support client consommateur, consommation de topics avec groupe, taille et timeout, affichage des détails en tableau.
- [x] Support PLAIN, SSL, SASL, Kerberos, sasl_plaintext, etc.
- [x] Compression et décompression gzip, lz4, snappy, zstd.
- [x] Création (par lots) et suppression de topics, spécification des répliques et partitions.
- [x] Statistiques du nombre total de messages, offset validé et accumulation par groupe de consommateurs.
- [x] Détails des partitions (offsets), ajout de partitions supplémentaires.
- [x] Simulation de producteur, envoi de messages par lots avec en-têtes et partition.
- [x] Vérification de l'état des topics et partitions (terminé).
- [x] Affichage des groupes de consommateurs et des consommateurs individuels.
- [x] Rapport d'inspection des offsets.
- [x] Prise en charge de Schema Registry : gestion des sujets et versions, compatibilité, décodage Avro, JSON et Protobuf.
- [x] Consommation en streaming multiple : streaming en temps réel, tri inversé, onglets multiples et commit d'offsets.
- [x] Réinitialisation des offsets de groupes : réinitialisation au début (Start), à la fin (End), par horodatage ou offset spécifique.
- [x] Purge de messages (DeleteRecords) : suppression de messages par partition ou sur tout le topic jusqu'à un offset donné.
- [x] Réassignation des répliques de partitions : inspection et ajustement visuel des répliques, annulation des tâches en cours.
- [x] Vue des nœuds enrichie : indicateur de Controller, analyse de l'espace disque LogDirs et gestion des quotas clients.
- [x] Import/Export des connexions : exportation au format YAML et importation depuis YAML/JSON avec déduplication.
- [x] Authentification étendue : prise en charge d'OAUTHBEARER (jeton statique), AWS MSK IAM et tunnels SSH multi-brokers.
- [x] Rejeu et exportation de messages : renvoi de messages sélectionnés vers d'autres topics et export en JSON/CSV.

# Téléchargement
Téléchargez depuis la droite ou visitez la [page des versions](https://github.com/Bronya0/Kafka-King/releases). Développez 【Assets】 et choisissez la version adaptée à votre plateforme : Windows, macOS, Linux.

**Utilisateurs macOS : si l'application indique "endommagée" à l'ouverture, exécutez `xattr -dr com.apple.quarantine /Applications/Kafka-King.app` dans le terminal (l'app n'est pas signée et est bloquée par Gatekeeper).**

`Remarques importantes :`
1. **Avant utilisation, vérifiez que le paramètre `advertised.listeners` de votre cluster Kafka est correct. S'il n'est pas configuré ou utilise des noms de domaine, ajoutez la résolution correspondante dans le fichier hosts de votre machine.**
2. **Si votre connexion nécessite SSL, activez TLS et désactivez la vérification sauf si vous avez un certificat, auquel cas activez la vérification TLS et fournissez le chemin du certificat.**
3. **Les utilisateurs SASL doivent activer SASL, sélectionner le protocole SASL approprié (généralement plain) et saisir l'utilisateur et le mot de passe.**
4. **En cas d'erreur webview2, téléchargez et réinstallez le runtime depuis le site officiel de Microsoft : https://developer.microsoft.com/fr-fr/microsoft-edge/webview2**


# Compilation
La compilation manuelle n'est nécessaire que pour étudier le code source.

cd app

wails dev

# Licence
Licence Apache-2.0

# Remerciements
- wails: https://wails.io/docs/gettingstarted/installation
- naive ui: https://www.naiveui.com/
- franz-go: https://github.com/twmb/franz-go/
- xicons: https://xicons.org/#/

# Traduction
Prend en charge le chinois, le japonais, l'anglais, le coréen, le russe et d'autres langues.

Corriger ou ajouter une nouvelle langue : https://github.com/Bronya0/Kafka-King/issues/51
