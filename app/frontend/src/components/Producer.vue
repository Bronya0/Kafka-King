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
      <h2>{{ t('producer.title') }}</h2>
      <p>{{ t('producer.desc') }}</p>
    </n-flex>

    <n-flex align="center">
      {{ t('producer.selectTopic') }}：
      <n-select
          v-model:value="selectedTopic"
          :options="data"
          :placeholder="t('producer.topicPlaceholder')"
          :render-option="renderSelect"
          filterable
          clearable
          style="width: 300px"
      />
      {{ t('producer.optionalMessageKey') }}：
      <n-input v-model:value="messageKey" :placeholder="t('producer.keyPlaceholder')" style="width: 300px"/>
      {{ t('producer.specifyPartition') }}：
      <n-input-number v-model:value="partition" style="width: 120px"/>
    </n-flex>

    <n-input
        v-model:value="messageContent"
        type="textarea"
        :placeholder="t('producer.messageContentPlaceholder')"
        :rows="12"
        style="text-align: left;"
    />

    <!-- Dynamic addition of headers -->
    <n-flex vertical>
      <n-flex align="center">
        <span>{{ t('producer.headersTitle') }}</span>
        <n-button size="small" @click="addHeader">
          {{ t('producer.addHeader') }}
        </n-button>
      </n-flex>

      <n-flex v-for="(header, index) in headers" :key="index" :wrap="false">
        <n-input v-model:value="header.key" :placeholder="t('producer.headerKeyPlaceholder')" style="width: 200px"/>
        <n-input v-model:value="header.value" :placeholder="t('producer.headerValuePlaceholder')" style="width: 200px"/>
        <n-button size="small" type="error" @click="removeHeader(index)">
          {{ t('producer.removeHeader') }}
        </n-button>
      </n-flex>
    </n-flex>

    <n-flex align="center">
      {{ t('producer.sendTimes') }}
      <n-input-number
          v-model:value="nums"
          :min="1"
          :placeholder="t('producer.sendTimesPlaceholder')"
          style="width: 160px"
      />
      {{t('common.compress')}}
        <n-select
            v-model:value="compress"
            :options="[
              {label: 'gzip', value: 'gzip'},
              {label: 'lz4', value: 'lz4'},
              {label: 'zstd', value: 'zstd'},
              {label: 'snappy', value: 'snappy'},
            ]"
            filterable
            clearable
            style="width: 100px"
        />

    </n-flex>
    <n-flex align="center">
      <n-button tertiary type="primary" @click="produce" :loading="loading" :render-icon="renderIcon(SendTwotone)">
        {{ t('producer.sendMessage') }}
      </n-button>
    </n-flex>

  </n-flex>
</template>
<script setup>

import {onMounted, ref, watch, onActivated} from 'vue'
import emitter, { setConnectName, getConnectName } from "../utils/eventBus";
import {NButton, useMessage} from "naive-ui";
import {renderIcon, renderSelect} from "../utils/common";
import {SendTwotone} from "@vicons/material";
import {GetTopics, Produce} from "../../wailsjs/go/service/Service";
import {useI18n} from "vue-i18n";

const {t} = useI18n()

const message = useMessage()
const data = ref([]);
// 表单数据
const selectedTopic = ref()
const messageKey = ref()
const messageContent = ref('')
const headers = ref([])
const nums = ref(1)
const partition = ref(null) // null 表示自动分配分区
const loading = ref(false)
const compress = ref()
let currentConnectName = ''

const refreshTopic = async () => {
  await getData()
}

const selectNode = async (node) => {
  currentConnectName = node?.name || ''
  setConnectName(currentConnectName)
  data.value = []
  selectedTopic.value = null
  loading.value = false

  await getData()
}

onMounted(() => {
  console.log('[Producer] onMounted')
  emitter.on('selectNode', selectNode)
  emitter.on('refreshTopic', refreshTopic)

  getData()
})

// topic 变更时缓存到 localStorage
watch(selectedTopic, (topic) => {
  if (currentConnectName && topic) {
    localStorage.setItem('kafkaKing:producer:topic:' + currentConnectName, topic)
  }
})

// keep-alive 缓存激活时从 localStorage 恢复 topic
onActivated(() => {
  const connectName = currentConnectName || getConnectName()
  console.log('[Producer] onActivated, connectName:', connectName, 'selected:', selectedTopic.value)
  if (connectName) {
    const cached = localStorage.getItem('kafkaKing:producer:topic:' + connectName)
    console.log('[Producer] cached topic:', cached)
    if (cached) {
      console.log('[Producer] restoring topic:', cached)
      selectedTopic.value = cached
    }
  }
})

// 读取topic及分区信息
const getData = async () => {
  try {
    const res = await GetTopics()
    if (res.err !== "") {
      message.error(res.err, {duration:  5000})
    } else {
      // 排序
      let data_lst = []
      if (res.results) {
        res.results.sort((a, b) => a['topic'] > b['topic'] ? 1 : -1)
        for (const k in res.results) {
          data_lst.push({
            "label": res.results[k]['topic'],
            "value": res.results[k]['topic']
          })
        }
      }
      data.value = data_lst
      // 从缓存恢复上次选的 topic
      if (currentConnectName && !selectedTopic.value) {
        const cached = localStorage.getItem('kafkaKing:producer:topic:' + currentConnectName)
        if (cached) {
          selectedTopic.value = cached
        }
      }
    }
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }

}


// 添加header
const addHeader = () => {
  headers.value.push({
    key: '',
    value: ''
  })
}

// 删除header
const removeHeader = (index) => {
  headers.value.splice(index, 1)
}

// 发送消息
const produce = async () => {
  if (!selectedTopic.value) {
    message.error(t('message.selectTopic'), {duration:  5000})
    return
  }

  if (!messageContent.value) {
    message.error(t('message.pleaseInput'), {duration:  5000})
    return
  }
  loading.value = true
  try {
    const res = await Produce(selectedTopic.value, messageKey.value, messageContent.value,
        partition.value === null ? -1 : partition.value, nums.value, headers.value, compress.value)
    if (res.err !== "") {
      message.error(res.err, {duration:  5000})
    } else {
      message.success(t('message.sendSuccess'))
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}


</script>
