<!--
  - Copyright 2025 Bronya0 <tangssst@163.com>.
  - Author Github: https://github.com/Bronya0
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     https://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2>{{ t('consumer.title') }}</h2>
      <p>{{ t('consumer.desc') }}</p>
      <n-button :render-icon="renderIcon(DriveFileMoveTwotone)" @click="downloadAllDataCsv">{{ t('common.csv') }}
      </n-button>
      <n-button :render-icon="renderIcon(DriveFileMoveTwotone)" @click="downloadAllDataJson">{{ t('common.json') }}
      </n-button>
      <n-button :render-icon="renderIcon(ReplayOutlined)" @click="openReplay">{{ t('consumer.replay') }}</n-button>
    </n-flex>
    <!-- 查询条件区域 -->
    <n-form ref="formRef" :model="select" :rules="{
      selectedTopic: { required: true, trigger: 'blur' },
      selectedGroup: { required: true, trigger: 'blur' },
      maxMessages: { required: true, type: 'number', trigger: 'blur' },
    }" inline label-placement="top" label-width="auto" style="text-align: left;">

      <!-- 常用选项 -->
      <n-form-item label="Topic" path="selectedTopic">
        <n-select v-model:value="select.selectedTopic" :options="topic_data" :placeholder="t('consumer.requiredTopic')"
          :render-option="renderSelect" clearable filterable />
      </n-form-item>

      <n-form-item label="Number" path="maxMessages" style="width: 100px">
        <n-tooltip>
          <template #trigger>
            <n-input-number v-model:value="select.maxMessages" :min="1" />
          </template>
          {{ t('consumer.messagesCountPlaceholder') }}
        </n-tooltip>
      </n-form-item>

      <n-form-item label="Group" path="selectedGroup">
        <n-tooltip>
          <template #trigger>
            <n-select v-model:value="select.selectedGroup" :options="group_data" :render-option="renderSelect" clearable
              filterable style="max-width: 200px" tag />
          </template>
          support create
        </n-tooltip>
      </n-form-item>

      <n-form-item>
        <n-button :loading="loading" :render-icon="renderIcon(MessageOutlined)" tertiary type="primary"
          @click="consume">
          {{ t('consumer.consumeMessage') }}
        </n-button>
      </n-form-item>

      <n-form-item>
        <n-button :loading="streamStarting" :render-icon="renderIcon(PlayArrowOutlined)"
          tertiary type="success" @click="startStream">
          {{ t('consumer.subscribe') }}
        </n-button>
      </n-form-item>

      <n-form-item>
        <n-button v-if="activeStreams.length > 0" :loading="streamStopping" :render-icon="renderIcon(StopOutlined)"
          tertiary type="error" @click="stopAllStreams">
          {{ t('consumer.stopAll') }}
        </n-button>
      </n-form-item>

      <n-form-item>
        <n-input v-model:value="searchText" clearable :placeholder="t('consumer.localSearch')" style="max-width: 150px"
          @input="searchData" />
      </n-form-item>

      <n-form-item>
        <n-tooltip>
          <template #trigger>
            <n-switch v-model:value="filterRegex" size="small" @update:value="searchData">
              <template #checked>{{ t('consumer.regex') }}</template>
              <template #unchecked>{{ t('consumer.keyword') }}</template>
            </n-switch>
          </template>
          {{ t('consumer.filterModeTip') }}
        </n-tooltip>
      </n-form-item>

      <!-- 高级选项折叠按钮 -->
      <n-form-item>
        <n-button text @click="advancedOptionsCollapsed = !advancedOptionsCollapsed">
          <template #icon>
            <n-icon>
              <ExpandMoreOutlined v-if="advancedOptionsCollapsed" />
              <ExpandLessOutlined v-else />
            </n-icon>
          </template>
          {{ advancedOptionsCollapsed ? t('consumer.showAdvanced') : t('consumer.hideAdvanced') }}
        </n-button>
      </n-form-item>
    </n-form>

    <!-- 高级选项区域 -->
    <n-form v-show="!advancedOptionsCollapsed" :model="select" inline label-placement="top" label-width="auto"
      style="text-align: left; margin-top: 10px;">
      <n-form-item label="Pull Timeout">
        <n-tooltip>
          <template #trigger>
            <n-input-number v-model:value="select.timeout" :min="1" style="max-width: 100px" />
          </template>
          {{ t('consumer.pollTimeoutPlaceholder') }}
        </n-tooltip>
      </n-form-item>

      <n-form-item :label="t('common.decompress')" path="decompress">
        <n-select v-model:value="select.decompress" :options="[
          { label: 'gzip', value: 'gzip' },
          { label: 'lz4', value: 'lz4' },
          { label: 'zstd', value: 'zstd' },
          { label: 'snappy', value: 'snappy' },
        ]" clearable filterable style="width: 100px" />
      </n-form-item>

      <n-form-item label="Decode" path="decode">
        <n-select v-model:value="select.decode" :options="[
          { label: 'utf8', value: 'utf8' },
          { label: 'Base64', value: 'base64' },
          { label: 'Avro (Schema Registry)', value: 'avro' },
          { label: 'JSON (Schema Registry)', value: 'sr_json' },
          { label: 'Protobuf (Schema Registry)', value: 'sr_pb' },
        ]" clearable filterable style="width: 170px" />
      </n-form-item>

      <n-form-item :label="t('consumer.startOffset')" path="startOffset">
        <n-tooltip>
          <template #trigger>
            <n-input-number v-model:value="select.startOffset" :min="0" style="max-width: 140px" clearable />
          </template>
          {{ t('consumer.startOffsetTip') }}
        </n-tooltip>
      </n-form-item>

      <n-form-item :label="t('consumer.isolationLevel')" path="isolationLevel">
        <n-select v-model:value="select.isolationLevel" :options="[
          { label: t('consumer.isolationLevelReadUncommitted'), value: 'read_uncommitted' },
          { label: t('consumer.isolationLevelReadCommitted'), value: 'read_committed' },
        ]" style="width: 100px" />
      </n-form-item>

      <n-form-item label="Commit Offset" path="isCommit">
        <n-tooltip>
          <template #trigger>
            <n-switch v-model:value="select.isCommit" :checked-value=true :round="false" :unchecked-value=false>
              <template #unchecked>false</template>
              <template #checked>true</template>
            </n-switch>
          </template>
          {{ t('consumer.commitOffsetTooltip') }}
        </n-tooltip>
      </n-form-item>

      <n-form-item :label="t('consumer.isLatest')" path="isLatest">
        <n-tooltip>
          <template #trigger>
            <n-switch v-model:value="select.isLatest" :checked-value=true :round="false" :unchecked-value=false>
              <template #unchecked>最早</template>
              <template #checked>最新</template>
            </n-switch>
          </template>
          {{ t('consumer.onlyTip') }}
        </n-tooltip>
      </n-form-item>

      <n-form-item :label="t('consumer.startTimestamp')" path="startTimestamp">
        <n-tooltip>
          <template #trigger>
            <n-date-picker v-model:value="select.startTimestamp" clearable style="max-width: 188px" type="datetime"
              value-format="timestamp" />
          </template>
          {{ t('consumer.onlyTip') }}
        </n-tooltip>
      </n-form-item>
    </n-form>

    <!-- 活跃流列表 -->
    <n-flex v-if="activeStreams.length > 0" align="center" :size="8" style="flex-wrap: wrap;">
      <n-tag v-for="s in activeStreams" :key="s.id" :type="s.running ? 'success' : 'default'" size="small" round
        closable @close="stopStream(s.id)">
        <template #icon>
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;"
            :style="{ background: s.running ? '#18a058' : '#ccc' }" />
        </template>
        {{ s.topic }} @ {{ s.group }}
      </n-tag>
    </n-flex>

    <!-- 流式订阅状态栏 -->
    <n-flex v-if="streamRunning || streamMsgCount > 0" align="center" :size="16" style="padding: 4px 0;">
      <n-tag :type="streamRunning ? 'success' : 'default'" size="small" round>
        <template #icon>
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;"
            :style="{ background: streamRunning ? '#18a058' : '#ccc' }" />
        </template>
        {{ streamRunning ? t('consumer.live') : t('consumer.stoppedStatus') }}
      </n-tag>
      <n-text depth="3">
        {{ t('consumer.received') }}
        <n-text depth="3" style="font-weight: bold">{{ totalReceived.toLocaleString() }}</n-text>
        <n-tooltip trigger="hover" style="font-size:12px">
          <template #trigger>
            <n-text depth="3" style="font-size:12px">({{ t('consumer.maxCache') }} {{ streamMsgCount.toLocaleString() }})</n-text>
          </template>
          {{ t('consumer.cacheTooltip', { count: maxStreamMessages.toLocaleString(), size: formatSize(MAX_MESSAGES_SIZE) }) }}
        </n-tooltip>
      </n-text>
      <n-text v-if="streamRunning && streamRate > 0" depth="3">~{{ streamRate }} {{ t('consumer.msgPerSec') }}</n-text>
      <n-switch v-model:value="autoScroll" size="small">
        <template #checked>{{ t('consumer.autoScroll') }}</template>
        <template #unchecked>{{ t('consumer.autoScroll') }}</template>
      </n-switch>
    </n-flex>
    <!-- 消息列表 -->
    <n-data-table :bordered="true" :columns="refColumns(columns)" :data="filter_messages" :pagination="pagination"
      striped />
  </n-flex>

  <!-- 回放对话框 -->
  <n-modal v-model:show="showReplay" preset="dialog" :title="t('consumer.replay')">
    <n-flex vertical>
      <n-text>{{ t('consumer.replayTip', { count: filter_messages.length }) }}</n-text>
      <n-select v-model:value="replayTarget" :options="topic_data" filterable :placeholder="t('consumer.replayTarget')" />
    </n-flex>
    <template #action>
      <n-button @click="showReplay = false">{{ t('common.cancel') }}</n-button>
      <n-button type="primary" :loading="replaying" @click="doReplay">{{ t('common.enter') }}</n-button>
    </template>
  </n-modal>
</template>
<script setup>
import { onMounted, onUnmounted, ref, shallowRef, h, nextTick, watch, onActivated } from 'vue'
import emitter, { setConnectName, getConnectName } from "../utils/eventBus";
import { createCsvContent, download_file, refColumns, renderIcon, renderSelect } from "../utils/common";
import {
  DriveFileMoveTwotone, MessageOutlined, ContentCopyOutlined, ExpandMoreOutlined, ExpandLessOutlined,
  PlayArrowOutlined, StopOutlined, ReplayOutlined,
} from "@vicons/material";
import { NButton, NDataTable, NFlex, NInput, NTooltip, NIcon, NTag, NText, NSwitch, useMessage } from 'naive-ui'
import {
  Consumer, GetGroups, GetStreamState, GetTopics, ReproduceMessages,
  StartStreamConsumer, StopStreamConsumer,
} from "../../wailsjs/go/service/Service";
import { EventsOn, EventsOff } from "../../wailsjs/runtime";
import { useI18n } from "vue-i18n";

const { t } = useI18n()
const formRef = ref(null)

const message = useMessage()
const topic_data = ref([]);
const group_data = ref([]);
let messages = []
const filter_messages = shallowRef([])
const searchText = ref(null)
const filterRegex = ref(false)

// 新增状态变量，用于跟踪是否是首次消费
const isFirstConsume = ref(true)

// 控制高级选项折叠状态
const advancedOptionsCollapsed = ref(true)

// 表单数据
const select = ref({
  selectedTopic: null,
  selectedGroup: "__kafka_king_auto_generate__",
  maxMessages: 100,
  timeout: 5,
  isCommit: false,
  isLatest: false,
  decompress: null,
  decode: "utf8", // 默认按 utf8 解码
  startTimestamp: null,
  startOffset: null, // 指定起始 offset（对每个分区生效）
  isolationLevel: "read_uncommitted", // 默认为read_uncommitted
})

const loading = ref(false)

const activeStreams = ref([]) // [{id, topic, group, running}]
const streamStarting = ref(false)
const streamStopping = ref(false)
const streamRunning = ref(false)
const streamMsgCount = ref(0)
const totalReceived = ref(0)
const streamRate = ref(0)
const autoScroll = ref(true)
const maxStreamMessages = ref(10000)
let streamMsgTimestamps = []
let streamEventsRegistered = false
let renderScheduled = false
let currentConnectName = ''

// 回放
const showReplay = ref(false)
const replayTarget = ref(null)
const replaying = ref(false)

// 内存保护：最大缓存 200MB，基于估算的消息大小
const MAX_MESSAGES_SIZE = 200 * 1024 * 1024
let totalMessagesSize = 0

const estimateMsgSize = (msg) => {
  let size = 0
  if (msg.Value) size += msg.Value.length * 2 // UTF-16 实际内存
  if (msg.Key) size += msg.Key.length * 2
  return size + 400 // 消息对象固定开销
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.min(units.length - 1, Math.floor(Math.log(bytes) / Math.log(1024)))
  return (bytes / Math.pow(1024, i)).toFixed(0) + ' ' + units[i]
}

const scheduleRender = () => {
  renderScheduled = true
  requestAnimationFrame(() => {
    renderScheduled = false
    searchData()
    if (autoScroll.value) {
      nextTick(() => {
        const tableBody = document.querySelector('.n-data-table .n-scrollbar-content')
        if (tableBody) {
          tableBody.parentElement.scrollTop = tableBody.parentElement.scrollHeight
        }
      })
    }
  })
}

const refreshStreams = async () => {
  try {
    const res = await GetStreamState()
    if (res.err === "") {
      activeStreams.value = res.result?.streams || []
      streamRunning.value = activeStreams.value.some(s => s.running)
    }
  } catch (e) {
    console.error(e)
  }
}

const refreshTopic = async () => {
  await getData()
}

const selectNode = async (node) => {
  if (activeStreams.value.length > 0) {
    await StopStreamConsumer("")
  }
  currentConnectName = node?.name || ''
  setConnectName(currentConnectName)
  topic_data.value = []
  group_data.value = []
  messages = []
  filter_messages.value = []
  totalMessagesSize = 0
  totalReceived.value = 0
  streamMsgCount.value = 0
  activeStreams.value = []
  streamRunning.value = false
  select.value.selectedTopic = null
  select.value.selectedGroup = null
  loading.value = false
  await getData()
}

// 消费参数变更时持久化到 localStorage
const CACHE_PARAMS_KEY = 'kafkaKing:consumer:params:'
watch(() => select.value, (val) => {
  if (currentConnectName && val.selectedGroup) {
    const cache = {
      selectedGroup: val.selectedGroup,
      maxMessages: val.maxMessages,
      timeout: val.timeout,
    }
    localStorage.setItem(CACHE_PARAMS_KEY + currentConnectName, JSON.stringify(cache))
  }
  if (currentConnectName && val.selectedTopic) {
    localStorage.setItem('kafkaKing:consumer:topic:' + currentConnectName, val.selectedTopic)
  }
}, { deep: true })

onMounted(async () => {
  emitter.on('selectNode', selectNode)
  emitter.on('refreshTopic', refreshTopic)
  getData()
  await registerStreamEvents()
  await refreshStreams()
})

// keep-alive 缓存激活时从 localStorage 恢复 topic
onActivated(() => {
  const connectName = currentConnectName || getConnectName()
  if (connectName) {
    const cached = localStorage.getItem('kafkaKing:consumer:topic:' + connectName)
    if (cached) {
      select.value.selectedTopic = cached
    }
  }
})

onUnmounted(() => {
  if (activeStreams.value.length > 0) {
    StopStreamConsumer("")
  }
  EventsOff("consumer-msg")
  EventsOff("consumer-err")
  EventsOff("consumer-start")
  EventsOff("consumer-end")
})


const getData = async () => {
  try {
    const res = await GetTopics()
    if (res.err !== "") {
      message.error(res.err, { duration: 5000 })
    } else {
      let topic_data_lst = []
      if (res.results) {
        res.results.sort((a, b) => a['topic'] > b['topic'] ? 1 : -1)
        for (const k in res.results) {
          topic_data_lst.push({
            "label": res.results[k]['topic'],
            "value": res.results[k]['topic']
          })
        }
      }
      topic_data.value = topic_data_lst
      // 从缓存恢复上次选的 topic
      if (currentConnectName && !select.value.selectedTopic) {
        const cached = localStorage.getItem('kafkaKing:consumer:topic:' + currentConnectName)
        if (cached) {
          select.value.selectedTopic = cached
        }
      }
    }
    const res2 = await GetGroups()
    if (res2.err !== "") {
      message.error(res2.err, { duration: 5000 })
    } else {
      let groups = [{
        label: '(auto generate)',
        value: '__kafka_king_auto_generate__',
      }]
      for (const k in res2.results) {
        const g_data = res2.results[k]
        groups.push({
          label: g_data['Group'],
          value: g_data['Group'],
          State: g_data['State'],
          ProtocolType: g_data['ProtocolType'],
          Coordinator: g_data['Coordinator'],
        })
      }
      groups.sort((a, b) => a['label'] > b['label'] ? 1 : -1)
      group_data.value = groups

      // 恢复上次的消费参数（消费组、数量、超时）
      if (currentConnectName) {
        const cached = localStorage.getItem(CACHE_PARAMS_KEY + currentConnectName)
        if (cached) {
          try {
            const params = JSON.parse(cached)
            if (params.selectedGroup && groups.some(g => g.value === params.selectedGroup)) {
              select.value.selectedGroup = params.selectedGroup
            }
            if (typeof params.maxMessages === 'number') {
              select.value.maxMessages = params.maxMessages
            }
            if (typeof params.timeout === 'number') {
              select.value.timeout = params.timeout
            }
          } catch (_) {}
        }
      }
    }
  } catch (e) {
    message.error(e.message, { duration: 5000 })
  }
}

// 分页配置
const pageKey = 'kafkaKing:consumer:pageKey'
const pagination = ref({
  page: 1,
  pageSize: parseInt(localStorage.getItem(pageKey)) || 10,
  showSizePicker: true,
  pageSizes: [5, 10, 15, 20, 25, 30, 40, 50, 100],
  onChange: (page) => {
    pagination.value.page = page
  },
  onUpdatePageSize: (pageSize) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
    localStorage.setItem(pageKey, pageSize.toString())
  },
})


// 表格列定义
const columns = [
  {
    title: 'Offset',
    key: 'Offset',
    width: 20,
    sorter: 'default'
  },
  {
    title: 'Key',
    key: 'Key',
    width: 15,
    sorter: 'default'
  },
  {
    title: 'Value',
    key: 'Value',
    width: 40,
    render(row) {
      return [
        h(NTooltip, {}, {
          trigger: () => h(NButton, {
            size: 'small',
            text: true,
            onClick: () => {
              navigator.clipboard.writeText(row.Value)
              message.success('复制成功')
            }
          }, { default: () => h(NIcon, { size: 14 }, { default: () => h(ContentCopyOutlined) }) }),
          default: () => '复制Value'
        }),
        h('span', { style: { 'margin-left': '8px', 'word-break': 'break-all' } }, row.Value)
      ]
    },
    sorter: 'default'
  },
  {
    title: 'Timestamp',
    key: 'Timestamp',
    width: 20,
    sorter: (rowA, rowB) => {
      const dateA = new Date(rowA['Timestamp']);
      const dateB = new Date(rowB['Timestamp']);
      return dateA - dateB;
    }
  },
  {
    title: 'Topic',
    key: 'Topic',
    width: 20,
    sorter: 'default'
  },
  {
    title: 'Partition',
    key: 'Partition',
    width: 10,
    sorter: 'default'
  },
  {
    title: 'Headers',
    key: 'Headers',
    width: 20,
    sorter: 'default'
  },
  {
    title: 'ProducerID',
    key: 'ProducerID',
    width: 10,
    sorter: 'default'
  }
]


// 获取消息
const consume = async () => {
  if (!select.value.selectedTopic) {
    message.error(t('message.selectTopic'), { duration: 5000 })
    return
  }
  if (!select.value.selectedGroup) {
    message.error("Group is needed", { duration: 5000 })
    return
  }
  loading.value = true
  try {
    // 如果是首次消费，显示提示
    if (isFirstConsume.value) {
      message.info(t('consumer.firstConsumeTip'))
      isFirstConsume.value = false
    }

    const result = await Consumer(select.value.selectedTopic, select.value.selectedGroup,
      select.value.maxMessages, select.value.timeout, select.value.decompress,
      select.value.isolationLevel,
      select.value.isCommit, select.value.isLatest, select.value.startTimestamp,
      select.value.startOffset || 0, select.value.decode)

    if (result.err !== "") {
      message.error(result.err, { duration: 5000 })
    } else {
      messages = result.results
      // 手动消费后重新计算缓存大小
      totalMessagesSize = 0
      for (const msg of messages) {
        totalMessagesSize += estimateMsgSize(msg)
      }
      searchData()
      message.success(t('message.fetchSuccess'))
    }
  } catch (e) {
    message.error(e.message, { duration: 5000 })
  } finally {
    loading.value = false
  }
}

function newStreamID() {
  return (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`)
}

function registerStreamEvents() {
  if (streamEventsRegistered) return
  streamEventsRegistered = true

  EventsOn("consumer-msg", (payload) => {
    if (!payload || !payload.rows || payload.rows.length === 0) return
    const rows = payload.rows.map(r => ({ ...r, Stream: String(payload.id || '').slice(0, 6) }))
    messages.push(...rows)
    totalReceived.value += rows.length

    // 累计新消息的估算内存大小
    for (const msg of rows) {
      totalMessagesSize += estimateMsgSize(msg)
    }

    const now = Date.now()
    streamMsgTimestamps.push({ time: now, count: rows.length })
    streamMsgTimestamps = streamMsgTimestamps.filter(e => e.time > now - 5000)
    const totalInWindow = streamMsgTimestamps.reduce((sum, e) => sum + e.count, 0)
    streamRate.value = Math.round(totalInWindow / 5)
    streamMsgCount.value = messages.length

    // 数量上限（控制表格行数）
    if (messages.length > maxStreamMessages.value) {
      const excess = messages.length - maxStreamMessages.value
      for (let i = 0; i < excess; i++) {
        totalMessagesSize -= estimateMsgSize(messages[i])
      }
      messages.splice(0, excess)
      streamMsgCount.value = messages.length
    }

    // 内存大小上限（防止大消息撑爆）
    if (totalMessagesSize > MAX_MESSAGES_SIZE) {
      let removeCount = 0
      while (removeCount < messages.length && totalMessagesSize > MAX_MESSAGES_SIZE) {
        totalMessagesSize -= estimateMsgSize(messages[removeCount])
        removeCount++
      }
      if (removeCount > 0) {
        messages.splice(0, removeCount)
        streamMsgCount.value = messages.length
      }
    }

    scheduleRender()
  })

  EventsOn("consumer-err", (payload) => {
    const errText = typeof payload === 'string' ? payload : payload?.err
    message.warning(String(errText ?? ''), { duration: 5000 })
  })

  EventsOn("consumer-start", (payload) => {
    streamStarting.value = false
    if (payload && payload.id) {
      const exists = activeStreams.value.some(s => s.id === payload.id)
      if (!exists) {
        activeStreams.value.push({
          id: payload.id,
          topic: payload.topic || '',
          group: payload.group || '',
          running: true,
        })
      } else {
        activeStreams.value.find(s => s.id === payload.id).running = true
      }
    }
    streamRunning.value = true
    message.success(t('message.streamStarted'))
  })

  EventsOn("consumer-end", (payload) => {
    const id = payload?.id ?? payload
    activeStreams.value = activeStreams.value.filter(s => s.id !== id)
    streamRunning.value = activeStreams.value.some(s => s.running)
    if (activeStreams.value.length === 0) {
      streamStopping.value = false
      streamRate.value = 0
      streamMsgTimestamps = []
    }
  })
}

async function startStream() {
  if (!select.value.selectedTopic) {
    message.error(t('message.selectTopic'), { duration: 5000 })
    return
  }
  if (!select.value.selectedGroup) {
    message.error("Group is needed", { duration: 5000 })
    return
  }
  streamStarting.value = true

  try {
    const result = await StartStreamConsumer(
      newStreamID(),
      select.value.selectedTopic, select.value.selectedGroup,
      select.value.maxMessages, select.value.timeout, select.value.decompress,
      select.value.isolationLevel,
      select.value.isCommit, select.value.isLatest,
      select.value.startTimestamp || 0, select.value.startOffset || 0, select.value.decode)

    if (result.err !== "") {
      message.error(result.err, { duration: 5000 })
      streamStarting.value = false
    } else {
      await refreshStreams()
    }
  } catch (e) {
    message.error(e.message, { duration: 5000 })
    streamStarting.value = false
  }
}

async function stopStream(id) {
  try {
    await StopStreamConsumer(id)
  } catch (e) {
    message.error(e.message, { duration: 5000 })
  }
  await refreshStreams()
}

async function stopAllStreams() {
  streamStopping.value = true
  try {
    await StopStreamConsumer("")
  } catch (e) {
    message.error(e.message, { duration: 5000 })
    streamStopping.value = false
  }
  await refreshStreams()
}

// 回放：把当前表格中的消息原样发到目标 topic
const openReplay = () => {
  if (filter_messages.value.length === 0) {
    message.warning(t('consumer.replayEmpty'), { duration: 5000 })
    return
  }
  replayTarget.value = select.value.selectedTopic
  showReplay.value = true
}

const doReplay = async () => {
  if (!replayTarget.value) {
    message.error(t('message.selectTopic'), { duration: 5000 })
    return
  }
  replaying.value = true
  try {
    const res = await ReproduceMessages(replayTarget.value, filter_messages.value)
    if (res.err !== "") {
      message.error(res.err, { duration: 5000 })
    } else {
      message.success(t('consumer.replayDone', { count: res.result?.count ?? 0 }))
      showReplay.value = false
    }
  } catch (e) {
    message.error(e.message, { duration: 5000 })
  } finally {
    replaying.value = false
  }
}

const downloadAllDataCsv = async () => {
  const csvContent = createCsvContent(
    filter_messages.value, columns
  )
  download_file(csvContent, 'messages.csv', 'text/csv;charset=utf-8;')
}

const downloadAllDataJson = () => {
  const content = JSON.stringify(filter_messages.value, null, 2)
  download_file(content, 'messages.json', 'application/json;charset=utf-8;')
}

// 流式显示窗口大小：自动滚底时只取最新 N 条，避免全量复制
const STREAM_WINDOW = 10000

const searchData = () => {
  if (searchText.value) {
    let pred
    if (filterRegex.value) {
      try {
        const re = new RegExp(searchText.value)
        pred = m => re.test(m.Value) || re.test(m.Key)
      } catch (_) {
        pred = () => true // 非法正则时不过滤
      }
    } else {
      const q = searchText.value
      pred = m => (m.Value || '').includes(q) || (m.Key || '').includes(q)
    }
    filter_messages.value = messages.filter(pred).slice().reverse()
  } else {
    // 自动滚底时只窗口化最新消息，大幅减少数组复制和 table 渲染
    if (streamRunning.value && autoScroll.value && messages.length > STREAM_WINDOW) {
      const windowed = messages.slice(messages.length - STREAM_WINDOW)
      windowed.reverse()
      filter_messages.value = windowed
    } else {
      filter_messages.value = messages.slice().reverse()
    }
  }
}

</script>
