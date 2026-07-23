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
        enter: "Подтвердить",
        cancel: "Отмена",
        name: "Имя",
        save: "Сохранить",
        check: "Пожалуйста, выберите",
        add: "Создать",
        edit: "Редактировать",
        delete: "Удалить",
        deleteFinish: "Успешно удалено",
        deleteOk: "Вы действительно хотите удалить?",
        count: "Количество",
        refresh: "Обновить",
        read: "Читать",
        config: "Настройки",
        csv: "Экспортировать в CSV",
        connecting: "Подключение...",
        action: "Действие",
        compress: 'кампрэсія',
        decompress: 'Распакуйце',
    },
    aside: {
        cluster: "Кластер",
        node: "Узел",
        topic: "Тема",
        producer: "Производитель",
        consumer: "Потребитель",
        group: "Группа потребителей",
        monitor: "Мониторинг",
        settings: "Настройки"
    },
    conn: {
        title: "Кластер",
        add: "Добавить кластер",
        edit: "Редактировать соединение",
        test: "Тестировать соединение",
        add_link: "Добавить соединение",
        please_add_name: "Пожалуйста, введите имя",
        please_add_link: "Пожалуйста, введите адрес соединения",
        input_name: "Пожалуйста, введите имя",
        bootstrap_servers: "Адрес соединения",
        tip: "Примечание: Убедитесь, что локальная среда может получить доступ к адресу advertised.listeners Kafka (особенно для разрешения доменов, даже если вы вводите IP, вам нужно настроить hosts локально)",
        tls: "Использовать TLS",
        skipTLSVerify: "Пропустить проверку TLS",
        tls_cert_file: "Введите путь к PEM-сертификату",
        tls_key_file: "Введите путь к приватному ключу",
        tls_ca_file: "Введите путь к CA-сертификату",
        use_sasl: "Использовать SASL",
        sasl_mechanism: "Механизм SASL",
        sasl_user: "Имя пользователя SASL",
        sasl_pwd: "Пароль SASL",
        kerberos_user_keytab: "Путь к файлу keytab Kerberos",
        kerberos_krb5_conf: "Путь к файлу krb5.conf Kerberos",
        Kerberos_user: "Имя пользователя Kerberos",
        Kerberos_realm: "Домен Kerberos",
        kerberos_service_name: "Имя сервиса Kerberos"
    },
    node: {
        title: "Узел",
        source: "Источник",
        value: "Значение (двойной щелчок для редактирования)",
        sensitive: "Чувствительно ли это?",
        ok_message: "Редактирование успешно, обновление конфигурации"
    },
    topic: {
        title: "Тема",
        add: "Создать тему",
        add_name: "Введите имя темы",
        selectedGroup: "Выберите группу и прочитайте смещения",
        partition: "Раздел",
        add_partition: "Добавить раздел",
        add_partition_count: "Количество добавляемых дополнительных разделов",
        replication_factor: "Коэффициент репликации",
        err: "Ошибка темы",
        lag: "Опоздание",
        viewProduce: "Производить сообщения",
        viewConsumer: "Просмотреть/потреблять сообщения",
        viewOffset: "Прочитать смещение",
        viewConfig: "Настройки темы",
        viewPartition: "Просмотр разделов",
        deleteTopic: "Удалить тему"
    },
    producer: {
        title: "Производитель",
        desc: "Клиент-производитель, который отправляет сообщения в указанную тему.",
        selectTopic: "Выбрать тему",
        topicPlaceholder: "Обязательно: Выберите или найдите Kafka тему",
        optionalMessageKey: "Необязательно: Введите ключ сообщения",
        keyPlaceholder: "Необязательно: Введите ключ сообщения",
        specifyPartition: "Необязательно: Укажите номер раздела",
        messageContentPlaceholder: "Обязательно: Содержание сообщения, строковый формат, поддерживается JSON",
        headersTitle: "Заголовки сообщения:",
        addHeader: "Добавить заголовок",
        removeHeader: "Удалить",
        headerKeyPlaceholder: "Ключ заголовка",
        headerValuePlaceholder: "Значение заголовка",
        sendTimes: "Количество отправок",
        sendTimesPlaceholder: "Количество отправок",
        sendMessage: "Отправить сообщение"
    },
    consumer: {
        title: "Потребитель",
        desc: "Простой клиент-потребитель для просмотра сообщений из темы.",
        requiredTopic: "Обязательно: Тема",
        topicPlaceholder: "Выберите или найдите Kafka тему",
        requiredMessagesCount: "Обязательно: Количество сообщений для потребления",
        messagesCountPlaceholder: "Количество сообщений для потребления",
        pollTimeoutDescription: "Время ожидания опроса: по умолчанию 10 секунд. Если есть исключения или нет сообщений для потребления, произойдет тайм-аут",
        pollTimeoutPlaceholder: "Время ожидания опроса",
        optionalGroup: "Необязательно: Группа (При выборе, смещения будут автоматически отправлены при потреблении. Поддерживает создание новых групп)",
        groupPlaceholder: "Выберите или создайте группу потребителей",
        commitOffsetTooltip: "Закоммитить смещение после потребления",
        firstConsumeTip: "Первое потребление может занять некоторое время для балансировки смещений",
        consumeMessage: "Потребовать сообщения",
        subscribe: "Подписаться",
        stop: "Стоп",
        live: "В эфире",
        stoppedStatus: "Остановлен",
        received: "Получено:",
        msgPerSec: "сообщ/с",
        autoScroll: "Автопрокрутка",
        maxCache: "Макс:",
        cacheTooltip: "Макс. количество: {count} | Макс. память: {size}",
    },
    group: {
        title: "Группа потребителей",
        member: "Участники",
        warn: "Пожалуйста, переключитесь с конкретной темы на эту страницу"
    },
    inspection: {
        title: "Мониторинг",
        desc: "Проверка состояния задержек в Kafka.",
        topicsLabel: "Темы",
        topicPlaceholder: "Выберите или найдите Kafka тему",
        groupLabel: "Группа",
        groupPlaceholder: "Выберите или создайте группу потребителей",
        startInspection: "Начать мониторинг",
        autoFetch: "Автоматическое получение данных каждые 5 минут",
        lagFormula: "Задержка = Конечное смещение - Закоммиченное смещение.",
        lag: 'Задержка',
        commit: 'Здзейснены зрух',
        end: 'Канцавое зрушэнне',
    },
    settings: {
        title: "Настройки",
        width: "Ширина окна",
        height: "Высота окна",
        lang: "Язык",
        theme: "Тема"
    },
    message: {
        noMemberFound: "Участников не найдено",
        saveSuccess: "Успешно сохранено",
        connectSuccess: "Успешно подключено",
        fetchSuccess: "Успешно получено",
        sendSuccess: "Успешно отправлено",
        selectGroupFirst: "Пожалуйста, сначала выберите группу",
        selectTopic: "Пожалуйста, выберите тему",
        selectTopicGroup: "Пожалуйста, выберите тему и группу",
        connectErr: "Ошибка подключения",
        addOk: "Успешно добавлено",
        editOk: "Успешно отредактировано, обновление конфигурации",
        mustFill: "Пожалуйста, заполните все обязательные поля",
        saveErr: "Ошибка сохранения",
        pleaseInput: "Пожалуйста, введите содержание сообщения",
        streamStarted: "Подписка запущена"
    },
    about: {
        title: "О программе",
        projectHomepage: "Домашняя страница проекта",
        kafkaKing: "Kafka-King",
        esClient: "Сопутствующий ES клиент",
        esKing: "ES-King",
        newProject: "Новый проект",
        allyAgent: "Ally Agent",
        technicalGroup: "Группа технического обмена",
        qqGroup: "QQ группа обмена",
        translate: 'Ці ёсць праблемы з перакладам? Паведаміць або прыняць удзел у перакладзе',
    },
    header: {
        desc: "Более удобный интерфейс для работы с Kafka",
        c_node: "Текущий кластер",
        netErr: "Не удается подключиться к GitHub, проверьте сетевое соединение",
        newVersion: "Доступна новая версия",
        down: "Скачать сейчас"
    }
}
