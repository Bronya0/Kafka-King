/*
 * Copyright 2025 Bronya0 <tangssst@163.com>.
 * Author Github: https://github.com/Bronya0
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

export default {
    common: {
        enter: "確認",
        cancel: "キャンセル",
        name: "ニックネーム",
        save: "保存",
        check: "選択してください",
        add: "作成",
        edit: "編集",
        delete: "削除",
        deleteFinish: "削除成功",
        deleteOk: "本当に削除しますか？",
        count: "数量",
        refresh: "更新",
        read: "読み取り",
        config: "設定",
        csv: "CSVとしてエクスポート",
        connecting: "接続中...",
        action: "操作",
        compress: '圧縮',
        decompress: '解凍',
    },
    aside: {
        cluster: "クラスタ",
        node: "ノード",
        topic: "トピック",
        producer: "プロデューサー",
        consumer: "コンシューマー",
        group: "コンシューマグループ",
        monitor: "巡回",
        settings: "設定"
    },
    conn: {
        title: "クラスタ",
        add: "クラスタを追加",
        edit: "接続を編集",
        test: "接続テスト",
        add_link: "接続を追加",
        please_add_name: "ニックネームを入力してください",
        please_add_link: "接続アドレスを入力してください",
        input_name: "名前を入力してください",
        bootstrap_servers: "接続アドレス",
        tip: "注意: Kafka クラスター内のすべてのノードの IP アドレスの DNS 解決にホスト名をローカル ホスト ファイルに追加する必要があります。そうしないと、通信異常が発生する可能性があります。",
        tls: "TLSを使用",
        skipTLSVerify: "TLS検証をスキップ",
        tls_cert_file: "PEM証明書パスを入力",
        tls_key_file: "秘密鍵ファイルパスを入力",
        tls_ca_file: "CA証明書パスを入力",
        use_sasl: "SASLを使用",
        sasl_mechanism: "SASLメカニズム",
        sasl_user: "SASLユーザー名",
        sasl_pwd: "SASLパスワード",
        kerberos_user_keytab: "Kerberos keytabファイルパス",
        kerberos_krb5_conf: "Kerberos krb5.confパス",
        Kerberos_user: "Kerberosユーザー",
        Kerberos_realm: "Kerberos領域",
        kerberos_service_name: "Kerberosサービス名"
    },
    node: {
        title: "ノード",
        source: "ソース",
        value: "値（ダブルクリックで編集）",
        sensitive: "感度はありますか？",
        ok_message: "編集成功、設定を更新"
    },
    topic: {
        title: "トピック",
        add: "トピックを作成",
        add_name: "トピック名を入力",
        selectedGroup: "グループを選択してオフセットを読み取る",
        partition: "パーティション",
        add_partition: "パーティションを追加",
        add_partition_count: "追加するパーティション数",
        replication_factor: "レプリケーションファクター",
        err: "トピックエラー",
        lag: "遅延",
        viewProduce: "メッセージの生成",
        viewConsumer: "メッセージの表示/消費",
        viewOffset: "オフセットの読み取り",
        viewConfig: "トピック設定",
        viewPartition: "パーティションの表示",
        deleteTopic: "トピックを削除"
    },
    producer: {
        title: "プロデューサー",
        desc: "指定されたトピックにメッセージを送信するプロデューサークライアント。",
        selectTopic: "トピックを選択",
        topicPlaceholder: "必須：トピックを選択または検索",
        optionalMessageKey: "オプション：メッセージキーを入力",
        keyPlaceholder: "オプション：メッセージキーを入力",
        specifyPartition: "オプション：パーティション番号を指定",
        messageContentPlaceholder: "必須：メッセージ内容、文字列形式、JSONもサポート",
        headersTitle: "メッセージヘッダー:",
        addHeader: "ヘッダーを追加",
        removeHeader: "削除",
        headerKeyPlaceholder: "ヘッダーキー",
        headerValuePlaceholder: "ヘッダーバリュー",
        sendTimes: "送信回数",
        sendTimesPlaceholder: "送信回数",
        sendMessage: "メッセージを送信"
    },
    consumer: {
        title: "コンシューマー",
        desc: "トピックからのメッセージを表示するシンプルなコンシューマクライアント。",
        requiredTopic: "必須：トピック",
        topicPlaceholder: "トピックを選択または検索",
        requiredMessagesCount: "必須：消費するメッセージ数",
        messagesCountPlaceholder: "消費するメッセージ数",
        pollTimeoutDescription: "ポールタイムアウト：デフォルトは10秒。異常または消費可能なメッセージがない場合、タイムアウトします",
        pollTimeoutPlaceholder: "ポールタイムアウト",
        optionalGroup: "オプション：グループ（一度選択すると、消費時にオフセットが自動的にコミットされます。新しいグループの作成もサポート）",
        groupPlaceholder: "コンシューマグループを選択または作成",
        consumeMessage: "メッセージを消費",
        subscribe: "サブスクライブ",
        stop: "停止",
        live: "ライブ",
        stoppedStatus: "停止中",
        received: "受信:",
        msgPerSec: "件/秒",
        autoScroll: "自動スクロール",
        maxCache: "上限:",
        cacheTooltip: "件数上限 {count} 件 | メモリ上限 {size}",
    },
    group: {
        title: "コンシューマグループ",
        member: "メンバー",
        warn: "具体的なトピックからこのページに切り替えてください"
    },
    inspection: {
        title: "巡回",
        desc: "Kafkaの遅延状況を巡回します。",
        topicsLabel: "トピック",
        topicPlaceholder: "トピックを選択または検索",
        groupLabel: "グループ",
        groupPlaceholder: "コンシューマグループを選択または作成",
        startInspection: "巡回を開始",
        autoFetch: "5分ごとにデータを自動取得",
        lagFormula: "遅延 = 終端オフセット - 提出オフセット。",
        lag: 'ラグ',
        commit: 'コミットされたオフセット',
        end: '終了オフセット',
    },
    settings: {
        title: "設定",
        width: "ウィンドウ幅",
        height: "ウィンドウ高さ",
        lang: "言語",
        theme: "テーマ"
    },
    message: {
        noMemberFound: "メンバーが見つかりません",
        saveSuccess: "保存しました",
        connectSuccess: "接続しました",
        fetchSuccess: "取得しました",
        sendSuccess: "送信しました",
        selectGroupFirst: "まずグループを選択してください",
        selectTopic: "トピックを選択してください",
        selectTopicGroup: "トピックとグループを選択してください",
        connectErr: "接続失敗",
        addOk: "追加しました",
        editOk: "編集しました、設定を更新",
        mustFill: "すべての必須フィールドを入力してください",
        saveErr: "保存失敗",
        pleaseInput: "メッセージ内容を入力してください",
        streamStarted: "サブスクリプション開始"
    },
    about: {
        title: "について",
        projectHomepage: "プロジェクトホームページ",
        kafkaKing: "Kafka-King",
        esClient: "同様のESクライアント",
        esKing: "ES-King",
        newProject: "新プロジェクト",
        allyAgent: "Ally Agent",
        technicalGroup: "技術交流グループ",
        qqGroup: "QQ交流グループ",
        translate: '「翻訳に問題がありますか?」報告するか翻訳に参加する',
    },
    header: {
        desc: "よりユーザーフレンドリーなKafka GUI",
        c_node: "現在のクラスタ",
        netErr: "GitHubに接続できません。ネットワークを確認してください",
        newVersion: "新しいバージョンが見つかりました",
        down: "今すぐダウンロード"
    }
};