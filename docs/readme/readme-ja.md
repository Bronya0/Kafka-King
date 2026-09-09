<p align="center">
  <img src="../../app/build/appicon.png" width="200" alt="图片标题">
</p>
<h1 align="center">Kafka King </h1>

<div align="center">

![License](https://img.shields.io/github/license/Bronya0/Kafka-King)
![GitHub release](https://img.shields.io/github/release/Bronya0/Kafka-King)
![GitHub All Releases](https://img.shields.io/github/downloads/Bronya0/Kafka-King/total)
![GitHub stars](https://img.shields.io/github/stars/Bronya0/Kafka-King)
![GitHub forks](https://img.shields.io/github/forks/Bronya0/Kafka-King.svg?style=flat-square)

<h3 align="center">現代的で実用的なKafka GUIクライアント</h3>

</div>
<h4 align="center">
<a href="../../readme.md">English</a> | <a href="../../README-CN.md">简体中文</a> | <a href="readme-ja.md">日本語</a> | <a href="readme-ru.md">рускі</a> | <a href="readme-ko.md">한국인</a> | <a href="readme-es.md">Español</a> | <a href="readme-fr.md">Français</a> | <a href="readme-de.md">Deutsch</a> | <a href="readme-pt.md">Português</a> | <a href="readme-it.md">Italiano</a> | <a href="readme-vi.md">Tiếng Việt</a> | <a href="readme-id.md">Bahasa Indonesia</a>  
</h4>

Kafkaの使い勝手を向上させる。

このプロジェクトは、複数のプラットフォームに対応したKafka GUIクライアントです。オープンソースへの支援としてスターマークをお願いします。ありがとうございます！

> 同様に便利なElasticsearchクライアント `ES-King` もご確認ください：https://github.com/Bronya0/ES-King

**Doc（AI）**：[https://zread.ai/Bronya0/Kafka-King](https://zread.ai/Bronya0/Kafka-King)

# Kafka-Kingの機能一覧
- [x] クラスタノードリストの表示、BrokerとTopic設定の動的構成サポート。
- [x] 消費者クライアントのサポート、指定されたグループによる特定のトピック、サイズ、タイムアウトでの消費、メッセージの詳細情報を表形式で表示。
- [x] PLAIN、SSL、SASL、Kerberos、sasl_plaintextなどへの対応。
- [x] メッセージのgzip、lz4、snappy、zstd圧縮と解凍をサポート
- [x] トピックの作成（バッチ処理もサポート）、削除、レプリカとパーティションの指定。
- [x] 各コンシューマーグループごとに各トピックの全メッセージ数、コミット数、遅延量の統計。
- [x] トピックのパーティションの詳細情報（オフセット）の表示、追加のパーティションの追加サポート。
- [x] 生産者のシミュレーション、ヘッダーとパーティション指定でのメッセージの一括送信。
- [x] トピックとパーティションのヘルスチェック（完了済み）。
- [x] コンシューマーグループと個々の消費者の表示。
- [x] オフセット検査レポート。
- [x] Schema Registryのサポート：Subject/バージョンの管理、互換性設定、Avro/JSON/Protobufメッセージのデコード。
- [x] マルチストリーミング消費：複数ストリームのリアルタイム消費、逆順表示、タブ管理、Offsetコミット。
- [x] コンシューマーグループのOffsetリセット：最早（Start）、最新（End）、タイムスタンプ、指定Offsetへのリセット。
- [x] メッセージ削除（DeleteRecords）：特定または全パーティションのメッセージ削除、全削除サポート。
- [x] パーティションレプリカの再割り当て：レプリカ配置の可視化・調整、実行中タスクのキャンセル。
- [x] ノード詳細とLogDirs：Controller表示、LogDirsディスク使用量分析、クライアントQuotas（クォータ）管理。
- [x] 接続設定のエクスポート/インポート：全クラスタ接続をYAML/JSON形式で出力・取り込み。
- [x] 認証の拡張：OAUTHBEARER（静的トークン）、AWS MSK IAM認証、SSHトンネル経由のマルチBroker接続。
- [x] メッセージの再生とエクスポート：選択したメッセージを他Topicへ再送、JSON/CSVでのエクスポート。

# ダウンロード
右側からダウンロードするか、[ダウンロードページ](https://github.com/Bronya0/Kafka-King/releases) を開いて 【Assets】 を展開し、自分のプラットフォーム向けのバージョンを選択してください。Windows、macOS、Linuxをサポートしています。

**macOSユーザーへ：「壊れている」と表示されて開けない場合、ターミナルで `xattr -dr com.apple.quarantine /Applications/Kafka-King.app` を実行してください（アプリが署名されておらず、Gatekeeperにブロックされているため）。**

`重要な注意点:`

1. **使用前に、Kafkaクラスタの`advertised.listeners`設定が正しく行われていることを確認してください。未設定またはドメイン名を使用している場合、接続先のドメイン名解像度エントリをローカルマシンのhostsファイルに追加して、ドメイン名の解像度により引き起こされる接続問題を避けてください。**
2. **SSLが必要な接続の場合、TLSを有効にして認証を無視してください（証明書がある場合は、TLS認証を有効にして証明書パスを入力）。**
3. **SASLユーザーはSASLを有効にし、適切なSASLプロトコル（通常はplain）を選択し、ユーザー名とパスワードを入力してください。**
4. **webview2ランタイムエラーが発生した場合は、Microsoftの公式ウェブサイトから最新のランタイムをダウンロードして再インストールしてください：https://developer.microsoft.com/ja-jp/microsoft-edge/webview2**



# ビルド
ソースコードを研究する場合のみ、手動でビルドが必要です。

cd app

wails dev


# ライセンス
Apache-2.0ライセンス

# 感謝
- wails: https://wails.io/docs/gettingstarted/installation
- naive ui: https://www.naiveui.com/
- franz-go: https://github.com/twmb/franz-go/
- xicons: https://xicons.org/#/

# 翻訳する
中国語、日本語、英語、韓国語、ロシア語などの言語をサポート

新しい言語の修正または追加：https://github.com/Bronya0/Kafka-King/issues/51
