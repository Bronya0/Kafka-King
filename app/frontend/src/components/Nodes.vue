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
      <h2>{{ t('node.title') }}</h2>
      <n-button @click="getData" text :render-icon="renderIcon(RefreshOutlined)">{{ t('common.refresh') }}</n-button>
      <n-text>{{ t('common.count') }}：{{ data?data.length:0 }}</n-text>
      <n-button @click="downloadAllDataCsv" :render-icon="renderIcon(DriveFileMoveTwotone)">{{ t('common.csv') }}
      </n-button>
    </n-flex>
    <n-spin :show="loading" description="loading...">
      <n-tabs type="line" animated v-model:value="activeTab">
        <n-tab-pane name="Broker">
          <template #tab>
            {{ t('node.title') }}
          </template>
          <n-data-table
              :columns="refColumns(columns)"
              :data="data"
              size="small"
              :bordered="false"
              striped
              :pagination="pagination"
          />
        </n-tab-pane>
        <n-tab-pane name="LogDirs">
          <template #tab>
            {{ t('node.logdirs') }}
          </template>
          <n-flex vertical>
            <n-flex align="center">
              <n-button @click="getLogDirs" :render-icon="renderIcon(RefreshOutlined)">{{ t('common.refresh') }}
              </n-button>
            </n-flex>
            <n-text depth="3">{{ t('node.logdirsTip') }}</n-text>
            <n-data-table
                :columns="refColumns(logdir_columns)"
                :data="logdir_data"
                size="small"
                :bordered="false"
                striped
                :pagination="pagination"
            />
            <n-text depth="3">{{ t('node.logdirsPartitions') }}</n-text>
            <n-data-table
                :columns="refColumns(logdir_partition_columns)"
                :data="logdir_partitions"
                size="small"
                :bordered="false"
                striped
                :pagination="pagination"
            />
          </n-flex>
        </n-tab-pane>
        <n-tab-pane name="Quotas">
          <template #tab>
            {{ t('node.quotas') }}
          </template>
          <n-flex vertical>
            <n-flex align="center">
              <n-button @click="getQuotas" :render-icon="renderIcon(RefreshOutlined)">{{ t('common.refresh') }}
              </n-button>
              <n-button type="primary" secondary @click="showQuotaModal = true"
                        :render-icon="renderIcon(AddFilled)">{{ t('node.addQuota') }}
              </n-button>
            </n-flex>
            <n-data-table
                :columns="refColumns(quota_columns)"
                :data="quota_data"
                size="small"
                :bordered="false"
                striped
                :pagination="pagination"
            />
          </n-flex>
        </n-tab-pane>
        <n-tab-pane name="Config">
          <template #tab>
            {{ t('common.config') }}
          </template>
          <n-flex vertical>

            <n-flex align="center">
              <n-input :disabled='activeConfigNode===""' placeholder="search" v-model:value="configSearchText" clearable style="width: 300px"/>
              <n-button :disabled='activeConfigNode===""' @click="getBrokerConfig(activeConfigNode)" :render-icon="renderIcon(RefreshOutlined)">
                {{ t('common.refresh') }}
              </n-button>
            </n-flex>
            <n-data-table
                :columns="refColumns(config_columns)"
                :data="config_data"
                :bordered="false"
                :pagination="pagination"

            />
          </n-flex>

        </n-tab-pane>
      </n-tabs>

    </n-spin>
  </n-flex>

  <n-modal v-model:show="showQuotaModal" preset="dialog" :title="t('node.addQuota')">
    <n-form label-placement="top" style="text-align: left;">
      <n-form-item :label="t('node.quotaEntityType')">
        <n-select v-model:value="quotaForm.entityType" :options="quotaEntityOptions" style="width: 200px"/>
      </n-form-item>
      <n-form-item :label="t('node.quotaEntityName')">
        <n-input v-model:value="quotaForm.entityName" :placeholder="t('node.quotaEntityNameTip')" style="width: 260px"/>
      </n-form-item>
      <n-form-item :label="t('node.quotaKey')">
        <n-select v-model:value="quotaForm.key" :options="quotaKeyOptions" tag filterable style="width: 260px"/>
      </n-form-item>
      <n-form-item :label="t('node.quotaValue')">
        <n-input-number v-model:value="quotaForm.value" :min="0" style="width: 260px"/>
      </n-form-item>
    </n-form>
    <template #action>
      <n-button @click="showQuotaModal = false">{{ t('common.cancel') }}</n-button>
      <n-button type="primary" :loading="quotaLoading" @click="addQuota">{{ t('common.enter') }}</n-button>
    </template>
  </n-modal>

</template>
<script setup>
import {h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NDataTable, NIcon, NInput, NInputNumber, NModal, NSelect, NTag, NText, useMessage} from 'naive-ui'
import {createCsvContent, download_file, getCurrentDateTime, refColumns, renderIcon} from "../utils/common";
import {AddFilled, DeleteOutlineTwotone, DriveFileMoveTwotone, RefreshOutlined, SettingsTwotone} from "@vicons/material";
import {
  AlterNodeConfig,
  AlterQuota,
  GetBrokerConfig,
  GetBrokers,
  GetLogDirs,
  GetQuotas,
} from "../../wailsjs/go/service/Service";
import ShowOrEdit from "../common/ShowOrEdit.vue";
import {useI18n} from "vue-i18n";

const message = useMessage()
const {t} = useI18n()

const config_data = ref([])
const data = ref([])
const configSearchText = ref("")
// 当前活动的 TabPane 名称
const activeTab = ref('Broker');
const activeConfigNode = ref('');
const loading = ref(false)

const selectNode = async (node) => {
  config_data.value = []
  data.value = []
  logdir_data.value = []
  logdir_partitions.value = []
  quota_data.value = []
  activeConfigNode.value = ''
  configSearchText.value = ''
  loading.value = false

  await getData()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  getData()
})


const getData = async () => {
  loading.value = true
  try {
    const res = await GetBrokers()
    if (res.err !== "") {
      message.error(res.err, {duration:  5000})
    } else {
      const result = res.result
      data.value = result.brokers
    }
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }

  loading.value = false

}

const pagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [5, 10, 20, 30, 40],
  onChange: (page) => {
    pagination.value.page = page
  },
  onUpdatePageSize: (pageSize) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
  },
})

const downloadAllDataCsv = async () => {
  const csvContent = createCsvContent(
      activeTab.value === "Broker" ? data.value : config_data.value,
      activeTab.value === "Broker" ? columns : config_columns
  )
  download_file(csvContent, `${getCurrentDateTime()}.csv`, 'text/csv;charset=utf-8;')
}


const columns = [
  {title: 'node_id', key: 'node_id',  width: 20},
  {
    title: 'host', key: 'host',  width: 50,
    render: (row) => h('span', {}, [
      h(NTag, {type: "info"}, {default: () => row['host']}),
      row['is_controller'] ? h(NTag, {type: 'warning', style: {marginLeft: '6px'}}, {default: () => t('node.controller')}) : null,
    ]),
  },
  {
    title: 'port', key: 'port',  width: 20,
    render: (row) => h(NTag, {type: "success"}, {default: () => row['port']}),
  },
  {title: 'rack', key: 'rack',  width: 20},
  {
    title: 'config', key: 'config', width: 30,
    render: (row) => h(
        NButton,
        {
          strong: true,
          secondary: true,
          onClick: async () => {
            await getBrokerConfig(row["node_id"])
            activeConfigNode.value = row["node_id"]
          }
        },
        {default: () => t('common.config'), icon: () => h(NIcon, null, {default: () => h(SettingsTwotone)})}
    )
  },
]

const config_columns = [
  {
    title: 'Name', key: 'Name',  width: 80,
  },
  {
    title: t('node.value'), key: 'Value',  width: 140,
    render: (row) => {
      return h(ShowOrEdit, {
        value: row['Value'],
        onUpdateValue(v) {
          alterNodeConfig(activeConfigNode.value, row['Name'], v)
        }
      })
    }
  },
  {title: t('node.source'), key: 'Source',  width: 50, },
  {
    title: t('node.sensitive'),
    key: 'Sensitive',
    width: 20,

    sorter: (row1, row2) => Number(row1['Sensitive']) - Number(row2['Sensitive']),
    render: (row) => h(NTag, {type: row['Sensitive'] === true ? "error" : "info"}, {default: () => row['Sensitive'] === true ? "yes" : "no"}),
  },

]

const getBrokerConfig = async (node_id) => {
  loading.value = true
  try {
    const res = await GetBrokerConfig(node_id)
    if (res.err !== "") {
      message.error(res.err, {duration:  5000})
    } else {
      // 排序
      res.results.sort((a, b) => a["Name"] > b["Name"] ? 1 : -1)
      if (configSearchText.value){
        res.results = res.results.filter(item => item['Name'].includes(configSearchText.value))
      }
      config_data.value = res.results
      activeTab.value = "Config"
    }
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }
  loading.value = false

}


// ---- LogDirs ----
const logdir_data = ref([])
const logdir_partitions = ref([])

const formatBytes = (b) => {
  if (b === null || b === undefined) return 'N/A'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  let v = Number(b)
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024
    i++
  }
  return v.toFixed(i === 0 ? 0 : 1) + ' ' + units[i]
}

const logdir_columns = [
  {title: 'Broker', key: 'broker', width: 15},
  {title: 'Dir', key: 'dir', width: 80},
  {
    title: t('node.size'), key: 'size', width: 25,
    render: (row) => row['err'] ? h(NTag, {type: 'error'}, {default: () => row['err']}) : formatBytes(row['size']),
  },
]

const logdir_partition_columns = [
  {title: 'Broker', key: 'broker', width: 12},
  {title: 'Topic', key: 'topic', width: 40},
  {title: 'Partition', key: 'partition', width: 12},
  {
    title: t('node.size'), key: 'size', width: 18,
    render: (row) => formatBytes(row['size']),
  },
  {
    title: t('topic.lag'), key: 'offset_lag', width: 15,
    render: (row) => row['offset_lag'] ?? 'N/A',
  },
]

const getLogDirs = async () => {
  loading.value = true
  try {
    const res = await GetLogDirs()
    if (res.err !== "") {
      message.error(res.err, {duration: 5000})
    } else {
      logdir_data.value = res.result?.dirs || []
      logdir_partitions.value = (res.result?.partitions || []).slice(0, 200)
      activeTab.value = 'LogDirs'
    }
  } catch (e) {
    message.error(e.message, {duration: 5000})
  }
  loading.value = false
}

// ---- Quotas ----
const quota_data = ref([])
const showQuotaModal = ref(false)
const quotaLoading = ref(false)
const quotaForm = ref({
  entityType: 'user',
  entityName: '',
  key: 'producer_byte_rate',
  value: 10240,
})
const quotaEntityOptions = [
  {label: 'user', value: 'user'},
  {label: 'client-id', value: 'client-id'},
  {label: 'ip', value: 'ip'},
]
const quotaKeyOptions = [
  {label: 'producer_byte_rate', value: 'producer_byte_rate'},
  {label: 'consumer_byte_rate', value: 'consumer_byte_rate'},
  {label: 'request_percentage', value: 'request_percentage'},
  {label: 'controller_mutation_rate', value: 'controller_mutation_rate'},
]

const quota_columns = [
  {title: 'Entity', key: 'entity', width: 60},
  {
    title: 'Values', key: 'values', width: 60,
    render: (row) => {
      const vs = row['values'] || {}
      return h('span', {}, Object.entries(vs).map(([k, v]) => `${k}=${v}`).join(', '))
    },
  },
  {
    title: t('common.action'), key: 'actions', width: 30,
    render: (row) => h(NButton, {
      strong: true, secondary: true, type: 'error',
      onClick: () => deleteQuota(row),
    }, {default: () => t('common.delete'), icon: () => h(NIcon, null, {default: () => h(DeleteOutlineTwotone)})}),
  },
]

const getQuotas = async () => {
  loading.value = true
  try {
    const res = await GetQuotas()
    if (res.err !== "") {
      message.error(res.err, {duration: 5000})
    } else {
      quota_data.value = res.results || []
      activeTab.value = 'Quotas'
    }
  } catch (e) {
    message.error(e.message, {duration: 5000})
  }
  loading.value = false
}

const addQuota = async () => {
  quotaLoading.value = true
  try {
    const res = await AlterQuota(
        quotaForm.value.entityType,
        quotaForm.value.entityName || '',
        [{key: quotaForm.value.key, value: Number(quotaForm.value.value)}],
    )
    if (res.err !== "") {
      message.error(res.err, {duration: 8000})
    } else {
      message.success(t('message.addOk'))
      showQuotaModal.value = false
      await getQuotas()
    }
  } catch (e) {
    message.error(e.message, {duration: 5000})
  } finally {
    quotaLoading.value = false
  }
}

const deleteQuota = async (row) => {
  const vs = row['values'] || {}
  const ops = Object.keys(vs).map(k => ({key: k, remove: true}))
  if (ops.length === 0) return
  // 从 entity 字符串 "user=alice" 解析回类型与名字
  const comps = String(row['entity']).replace(/[{}]/g, '').split(',').map(x => x.trim()).filter(Boolean)
  let entityType = 'user'
  let entityName = ''
  if (comps.length > 0) {
    const [etype, ename] = comps[0].split('=')
    entityType = etype
    entityName = ename === '<default>' ? '' : ename
  }
  loading.value = true
  try {
    const res = await AlterQuota(entityType, entityName, ops)
    if (res.err !== "") {
      message.error(res.err, {duration: 8000})
    } else {
      message.success(t('common.deleteFinish'))
      await getQuotas()
    }
  } catch (e) {
    message.error(e.message, {duration: 5000})
  } finally {
    loading.value = false
  }
}

const alterNodeConfig = async (node_id, name, value) => {
  loading.value = true
  try {
    const res = await AlterNodeConfig(node_id, name, value)
    if (res.err !== "") {
      message.error(res.err, {duration:  5000})
    } else {
      message.success(t('node.ok_message'))
      await getBrokerConfig(activeConfigNode.value)
    }
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }
  loading.value = false

}

</script>


<style scoped>

</style>