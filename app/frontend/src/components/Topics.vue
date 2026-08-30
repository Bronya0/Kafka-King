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
      <h2>{{ t('topic.title') }}</h2>
      <n-button @click="getData" text :render-icon="renderIcon(RefreshOutlined)">{{ t('common.refresh') }}</n-button>
      <n-text>{{ t('common.count') }}：{{ data?data.length:0 }}</n-text>
      <n-button @click="downloadAllDataCsv" :render-icon="renderIcon(DriveFileMoveTwotone)">{{ t('common.csv') }}
      </n-button>

    </n-flex>
    <n-spin :show="loading" description="loading...">
      <n-tabs type="line" animated v-model:value="activeTab">

        <n-tab-pane name="Topic">
          <template #tab>
            <n-icon>
              <LibraryBooksOutlined/>
            </n-icon>
            {{ t('topic.title') }}
          </template>
          <n-flex vertical>
            <!--          搜索框、新增按钮-->
            <n-flex align="center">
              <n-input v-model:value="searchText" @keydown.enter="getData" :placeholder="t('topic.add_name')" clearable
                       style="width: 300px"/>
              <n-button @click="getData" :render-icon="renderIcon(SearchOutlined)"></n-button>
              <n-button @click="showDrawer=true" :render-icon="renderIcon(AddFilled)">{{ t('topic.add') }}</n-button>
              <n-button @click="getData" :render-icon="renderIcon(RefreshOutlined)">{{ t('common.read') }} Topic
              </n-button>
              <!--              <n-dropdown :options="group_data"  @select="getTopicsOffsets"><n-button :render-icon="renderIcon(RefreshOutlined)">刷新 Offsets</n-button></n-dropdown>-->
              <n-select
                  v-model:value="selectedGroup"
                  :options="group_data"
                  :placeholder="t('topic.selectedGroup')"
                  :render-option="renderSelect"
                  filterable
                  clearable
                  style="width: 250px"
              />
              <n-button @click="getTopicsOffsets" :render-icon="renderIcon(RefreshOutlined)">{{ t('common.read') }}
                Offsets
              </n-button>
            </n-flex>
            <n-data-table
                :columns="refColumns(columns)"
                :data="data"
                size="small"
                :bordered="false"
                striped
                :pagination="pagination"
                :row-key="rowKey"
                v-model:checked-row-keys="selectedRowKeys"
            />
          </n-flex>

        </n-tab-pane>

        <n-tab-pane name="Partition">
          <template #tab>
            <n-icon>
              <AddRoadOutlined/>
            </n-icon>
            {{ t('topic.partition') }}
          </template>

          <n-flex vertical>
            <n-flex align="center">
              <n-text>topic:</n-text>
              <n-tag type="success">
                {{ activeDetailTopic }}
              </n-tag>
              <n-button :disabled="!activeDetailTopic" @click="showModal=true" :render-icon="renderIcon(AddFilled)">{{ t('topic.add_partition') }}
              </n-button>
              <n-select
                  v-model:value="selectedGroup"
                  :options="group_data"
                  :placeholder="t('topic.selectedGroup')"
                  :render-option="renderSelect"
                  filterable
                  clearable
                  :disabled="!activeDetailTopic"
                  style="width: 250px"
              />
              <n-button :disabled="!activeDetailTopic" @click="getPartitionOffsets" :render-icon="renderIcon(RefreshOutlined)">{{ t('common.read') }}
                Offsets
              </n-button>
            </n-flex>
            <n-data-table
                :columns="refColumns(partitions_columns)"
                :data="partitions_data"
                :bordered="false"
                :pagination="pagination"
            />
          </n-flex>

        </n-tab-pane>

        <n-tab-pane name="Config">
          <template #tab>
            <n-icon>
              <SettingsRound/>
            </n-icon>
            {{ t('common.config') }}
          </template>

          <n-flex vertical>
            <n-flex align="center">
              <n-text>topic:</n-text>

              <n-tag type="success">
                {{ activeConfigTopic }}
              </n-tag>

              <n-input :disabled="!activeConfigTopic" placeholder="search" v-model:value="configSearchText" clearable style="width: 300px"/>
              <n-button :disabled="!activeConfigTopic" @click="getTopicConfig(activeConfigTopic)" :render-icon="renderIcon(RefreshOutlined)">
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

  <n-drawer v-model:show="showDrawer" :width="500">
    <n-drawer-content :title="t('topic.add')">
      <n-form
          ref="formRef"
          :model="topic_add"
          label-placement="top"
          style="text-align: left;"
          label-width="120"
          require-mark-placement="right-hanging"
      >
        <n-form-item label="Topic" path="topics">
          <n-dynamic-tags
              v-model:value="topic_add.topics"
              :max="100"
          />
        </n-form-item>

        <n-form-item :label="t('topic.partition')" path="partitions">
          <n-input-number
              v-model:value="topic_add.partitions"
              :min="1"
          />
        </n-form-item>

        <n-form-item :label="t('topic.replication_factor')+' (cluster should be at least 2)'" path="replicationFactor">
          <n-input-number
              v-model:value="topic_add.replication_factor"
              :min="1"
          />
        </n-form-item>

        <n-form-item :label="t('topic.viewConfig')" path="config">
          <n-input
              v-model:value="topic_add.configs"
              type="textarea"
              placeholder="Please Input JSON"
              :rows="8"
          />
        </n-form-item>

      </n-form>

      <template #footer>
        <n-space>
          <n-button @click="showDrawer = false">{{ t('common.cancel') }}</n-button>
          <n-button :loading="loading" type="primary" @click="addTopic">{{ t('common.enter') }}</n-button>
        </n-space>
      </template>
    </n-drawer-content>
  </n-drawer>

  <n-modal v-model:show="showModal" preset="dialog" :title="t('topic.add_partition')">
    <n-form
        label-placement="top"
        style="text-align: left;"
    >
      <n-form-item :label="t('topic.add_partition_count')" path="addPartitionNum">
        <n-input-number v-model:value="addPartitionNum" :min="1" :placeholder="t('topic.add_partition_count')"
                        :style="{ maxWidth: '120px' }"/>
      </n-form-item>
      <n-flex>

        <n-button @click="showModal = false">{{ t('common.cancel') }}</n-button>
        <n-button type="primary" @click="addTopicPartition">{{ t('common.enter') }}</n-button>
      </n-flex>
    </n-form>

  </n-modal>

  <n-modal v-model:show="showDeleteRecords" preset="dialog" :title="t('topic.deleteRecords')">
    <n-form label-placement="top" style="text-align: left;">
      <n-form-item label="Topic">
        <n-tag type="info">{{ deleteRecordsForm.topic }}</n-tag>
      </n-form-item>
      <n-form-item :label="t('topic.deleteRecordsScope')">
        <n-switch v-model:value="deleteRecordsForm.all" :round="false">
          <template #checked>{{ t('topic.deleteRecordsAll') }}</template>
          <template #unchecked>{{ t('topic.deleteRecordsBefore') }}</template>
        </n-switch>
      </n-form-item>
      <n-form-item v-if="!deleteRecordsForm.all" :label="t('topic.deleteRecordsOffset')">
        <n-input-number v-model:value="deleteRecordsForm.offset" :min="0" style="width: 260px"/>
      </n-form-item>
      <n-text type="error">{{ t('topic.deleteRecordsWarning') }}</n-text>
    </n-form>
    <template #action>
      <n-button @click="showDeleteRecords = false">{{ t('common.cancel') }}</n-button>
      <n-button type="error" :loading="deleteRecordsLoading" @click="doDeleteRecords">{{ t('common.enter') }}</n-button>
    </template>
  </n-modal>

  <n-modal v-model:show="showReassign" preset="dialog" :title="t('topic.reassign')">
    <n-form label-placement="top" style="text-align: left;">
      <n-form-item label="Topic">
        <n-tag type="info">{{ reassignForm.topic }}</n-tag>
      </n-form-item>
      <n-form-item :label="t('topic.reassignJson')">
        <n-input v-model:value="reassignForm.json" type="textarea" :rows="10" style="font-family: monospace"/>
      </n-form-item>
      <n-text depth="3">{{ t('topic.reassignTip') }}</n-text>
    </n-form>
    <template #action>
      <n-button @click="showReassign = false">{{ t('common.cancel') }}</n-button>
      <n-button type="primary" :loading="reassignLoading" @click="doReassign">{{ t('common.enter') }}</n-button>
    </template>
  </n-modal>

</template>
<script setup>
import {h, onMounted, ref} from "vue";
import emitter, { setConnectName, getConnectName } from "../utils/eventBus";
import {NButton, NDataTable, NDropdown, NIcon, NInput, NInputNumber, NModal, NTag, NText, useDialog, useMessage} from 'naive-ui'
import {
  AddFilled,
  AddRoadOutlined,
  DriveFileMoveTwotone,
  LibraryBooksOutlined,
  MoreVertFilled,
  RefreshOutlined,
  SearchOutlined,
  SettingsRound,
} from '@vicons/material'
import {
  createCsvContent,
  download_file,
  getCurrentDateTime,
  isValidJson, refColumns,
  renderIcon,
  renderSelect
} from "../utils/common";
import {
  AlterPartitionReassignments,
  AlterTopicConfig,
  CreatePartitions,
  CreateTopics,
  DeleteRecords,
  DeleteTopic,
  GetGroups,
  GetTopicConfig,
  GetTopicOffsets,
  GetTopics
} from "../../wailsjs/go/service/Service";
import ShowOrEdit from "../common/ShowOrEdit.vue";
import {useI18n} from "vue-i18n";

const {t} = useI18n()

const config_data = ref([])
const partitions_data = ref([])
const group_data = ref([])
const offsets = ref({
  start_map: {},
  end_map: {},
  commit_map: {},
})
const activeTab = ref('Topic');
const selectedGroup = ref();
const loading = ref(false)
const data = ref([])
let currentConnectName = ''
const topic_add = ref({
  topics: [],
  partitions: 1,
  replication_factor: 1,
  configs: ""
})
const rowKey = (row) => row['topic']
const selectedRowKeys = ref([]);

const message = useMessage()
const dialog = useDialog()

const searchText = ref("");
const configSearchText = ref("");
const activeDetailTopic = ref("");
const activeConfigTopic = ref("");
const showDrawer = ref(false)
const showModal = ref(false)
const addPartitionNum = ref(1)

const selectNode = async (node) => {
  currentConnectName = node?.name || ''
  setConnectName(currentConnectName)
  config_data.value = []
  partitions_data.value = []
  group_data.value = []
  selectedRowKeys.value = []
  data.value = []
  offsets.value = {
    start_map: {},
    end_map: {},
    commit_map: {},
  }
  topic_add.value = {
    topics: [],
    partitions: 1,
    replication_factor: 1,
    configs: ""
  }

  selectedGroup.value = null
  activeDetailTopic.value = ''
  activeConfigTopic.value = ''
  loading.value = false
  showDrawer.value = false
  showModal.value = false
  addPartitionNum.value = 1
  searchText.value = ""
  configSearchText.value = ""

  await getData()
  await getGroups()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  getData()
  getGroups()
})

// 读取topic及分区信息
const getData = async () => {
  loading.value = true
  try {
    const res = await GetTopics(true)
    if (res.err !== "") {
      message.error(res.err, {duration:  5000})
    } else {
      // 排序
      if (res.results) {
        res.results.sort((a, b) => a['topic'] > b['topic'] ? 1 : -1)
        if (searchText.value !== "") {
          // 模糊搜索
          data.value = res.results.filter(item => item['topic'].includes(searchText.value))
        } else {
          data.value = res.results
        }
      } else {
        data.value = []
      }
    }
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }

  loading.value = false

}

const pageKey = 'kafkaKing:topics:pageKey'
const pagination = ref({
  page: 1,
  pageSize: parseInt(localStorage.getItem(pageKey)) || 10,
  showSizePicker: true,
  pageSizes: [5, 10, 15, 20, 25, 30, 40],
  onChange: (page) => {
    pagination.value.page = page
  },
  onUpdatePageSize: (pageSize) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
    localStorage.setItem(pageKey, pageSize.toString())
  },
})

const downloadAllDataCsv = async () => {
  let datas = {
    "Config": [config_data, config_columns],
    "Topic": [data, columns],
    "Partition": [partitions_data, partitions_columns]
  }
  const csvContent = createCsvContent(
      datas[activeTab.value][0].value,
      datas[activeTab.value][1],
  )

  download_file(csvContent, `${activeTab.value}-${getCurrentDateTime()}.csv`, 'text/csv;charset=utf-8;')
}

const columns = [
  {type: "selection",},
  // {title: 'ID', key: 'ID',  width: 20,},
  {
    title: 'topic', key: 'topic',  width: 80,
    render: (row) => h(NText, {
      type: 'info',
      style: {cursor: 'pointer'},
      onClick: async () => {
        await getTopicConfig(row["topic"])
        activeConfigTopic.value = row["topic"]
      }
    }, {default: () => row['topic']}),
  },
  {
    title: t('topic.partition'), key: 'partition_count',  width: 30,
    render: (row) => h(NText, {
      type: 'info',
      style: {cursor: 'pointer'},
      onClick: async () => {
        await getTopicDetail(row["topic"])
        activeDetailTopic.value = row["topic"]
      }
    }, {default: () => row['partition_count']}),
  },
  {title: t('topic.replication_factor'), key: 'replication_factor',  width: 30},
  {
    title: t('topic.err'),
    key: 'Err',
    width: 40,
    render: (row) => h(NTag, {type: row['Err'] === "" ? "success" : 'error'}, {default: () => row['Err'] === "" ? "health" : row['Err']}),
  },
  {
    title: 'StartOffset',
    key: 'StartOffset',

    width: 50,


  },
  {
    title: 'CommittedOffset',
    key: 'CommittedOffset',

    width: 60,


  },
  {
    title: 'EndOffset',
    key: 'EndOffset',

    width: 50,


  },
  {
    title: t('topic.lag'),
    key: 'lag',
    width: 50,


    render: (row) => {
      if (row.EndOffset != null && row.CommittedOffset != null) {
        return row.EndOffset - row.CommittedOffset
      }
    },
    sorter: (row1, row2) => {
      const lag1 = row1.EndOffset != null && row1.CommittedOffset != null
          ? row1.EndOffset - row1.CommittedOffset
          : 0;
      const lag2 = row2.EndOffset != null && row2.CommittedOffset != null
          ? row2.EndOffset - row2.CommittedOffset
          : 0;
      return lag1 - lag2;
    }
  },
  {
    title: t('common.action'),
    key: 'actions',
    width: 80,  // 调整宽度以适应两个按钮

    render: (row) => {
      const options = [
        {label: t('topic.viewProduce'), key: 'viewProduce'},
        {label: t('topic.viewConsumer'), key: 'viewConsumer'},
        {label: t('topic.viewOffset'), key: 'viewOffset'},
        {label: t('topic.viewConfig'), key: 'viewConfig'},
        {label: t('topic.viewPartition'), key: 'viewPartition'},
        {label: t('topic.deleteRecords'), key: 'deleteRecords'},
        {label: t('topic.reassign'), key: 'reassign'},
        {label: t('topic.deleteTopic'), key: 'deleteTopic'},
      ]
      return h(
          NDropdown,
          {
            trigger: 'click',
            options,
            onSelect: (key) => handleMenuSelect(key, row)
          },
          {
            default: () => h(
                NButton,
                {
                  strong: true,
                  secondary: true,
                },
                {default: () => t('common.action'), icon: () => h(NIcon, null, {default: () => h(MoreVertFilled)})}
            )
          }
      )
    }
  },
]


const handleMenuSelect = async (key, row) => {
  const func = {
    "viewProduce": viewProduce,
    "viewConsumer": viewConsumer,
    "viewOffset": viewOffset,
    "viewConfig": viewConfig,
    "viewPartition": viewPartition,
    "deleteRecords": openDeleteRecords,
    "reassign": openReassign,
    "deleteTopic": deleteTopic,
  }
  loading.value = true
  try {
    await func[key](row)
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }
  loading.value = false
}


const partitions_columns = [
  {title: 'ID', key: 'partition',  width: 10},
  {
    title: 'Health',
    key: 'err',
    width: 20,
    render: (row) => h(NTag, {type: row['err'] === "" ? "success" : 'error'}, {default: () => row['err'] === "" ? "health" : row['err']}),
  },
  {
    title: 'StartOffset',
    key: 'StartOffset',
    width: 15,
  },
  {
    title: 'CommittedOffset',
    key: 'CommittedOffset',
    width: 16,
  },
  {
    title: 'EndOffset',
    key: 'EndOffset',
    width: 15,
  },
  {
    title: 'Lag',
    key: '积压',
    width: 15,
    render: (row) => {
      if (row.EndOffset != null && row.CommittedOffset != null) {
        return row.EndOffset - row.CommittedOffset
      }
    }
  },
  {title: 'LeaderID', key: 'leader',  width: 15},
  {title: 'LeaderEpoch', key: 'LeaderEpoch',  width: 15},
  {title: 'Replicas', key: 'replicas',  width: 15},
  {title: 'ISR', key: 'isr',  width: 15},
  {title: 'ErrorReplicas', key: 'OfflineReplicas',  width: 15},
]

const config_columns = [
  {title: 'Name', key: 'Name',  width: 100},
  {
    title: t('node.value'), key: 'Value',  width: 140,
    render: (row) => {
      return h(ShowOrEdit, {
        value: row['Value'],
        onUpdateValue(v) {
          alterTopicConfig(activeConfigTopic.value, row['Name'], v)
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


const getTopicConfig = async (topic) => {
  loading.value = true
  try {
    const res = await GetTopicConfig(topic)
    if (res.err !== "") {
      message.error(res.err, {duration:  5000})
    } else {
      // 排序
      if (res.results) {
        res.results.sort((a, b) => a["Name"] > b["Name"] ? 1 : -1)
        if (configSearchText.value){
          res.results = res.results.filter(item => item['Name'].includes(configSearchText.value))
        }
        config_data.value = res.results
      } else {
        config_data.value = []
      }
      activeTab.value = "Config"
    }
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }
  loading.value = false

}

const getTopicDetail = async (topic) => {
  loading.value = true
  try {
    let partitions = data.value.find(item => item['topic'] === topic)['partitions']
    partitions.sort((a, b) => a['partition'] > b['partition'] ? 1 : -1)
    // 给每个item添加topic属性，后面匹配会用到
    partitions.forEach(item => item['topic'] = topic)
    partitions_data.value = partitions
    // 获取offsets
    if (selectedRowKeys.value.length > 0) {
      await getTopicsOffsets()
    } else {
      mergeOffsets()
    }
    activeTab.value = "Partition"
    console.log(activeTab.value)
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }
  loading.value = false

}

// 页面跳转，第二个参数是菜单key
const viewProduce = async (row) => {
  const cn = currentConnectName || getConnectName()
  console.log('[Topics] write producer topic:', row.topic, 'connect:', cn)
  if (cn) {
    localStorage.setItem('kafkaKing:producer:topic:' + cn, row.topic)
  }
  emitter.emit('menu_select', "producer")
}

// 页面跳转，第二个参数是菜单key
const viewConsumer = async (row) => {
  const cn = currentConnectName || getConnectName()
  console.log('[Topics] write consumer topic:', row.topic, 'connect:', cn)
  if (cn) {
    localStorage.setItem('kafkaKing:consumer:topic:' + cn, row.topic)
  }
  emitter.emit('menu_select', "consumer")
}

//  读取某topic的offset
const viewOffset = async (row) => {
  if (!selectedGroup.value) {
    message.warning(t('message.selectGroupFirst'))
    return
  }
  await getOffsets([row.topic], selectedGroup.value)
}

// 查看配置
const viewConfig = async (row) => {
  await getTopicConfig(row["topic"])
  activeConfigTopic.value = row["topic"]
}

// 查看分区
const viewPartition = async (row) => {
  await getTopicDetail(row["topic"])
  activeDetailTopic.value = row["topic"]
}
// 获取当页数据
const getPage = (data_lst) => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize;
  const end = start + pagination.value.pageSize;
  return data_lst.slice(start, end)
}

const getTopicsOffsets = async () => {
  if (!selectedGroup.value) {
    message.warning(t('message.selectGroupFirst'))
    return
  }
  const page_data = getPage(data.value)
  const topics = page_data.map(item => item['topic'])
  await getOffsets(topics, selectedGroup.value)
}

const getPartitionOffsets = async () => {
  if (activeDetailTopic.value === "") {
    message.warning(t('group.warn'))
    return
  }
  if (!selectedGroup.value) {
    message.warning(t('message.selectGroupFirst'))
    return
  }

  await getOffsets([activeDetailTopic.value], selectedGroup.value)
}

const getOffsets = async (topics, key) => {
  try {
    loading.value = true
    const res = await GetTopicOffsets(topics, key)
    if (res.err !== "") {
      message.error(res.err, {duration:  5000})
    } else {
      offsets.value.start_map = {...res.result.start_map}
      offsets.value.end_map = {...res.result.end_map}
      offsets.value.commit_map = {...res.result.commit_map}
      mergeOffsets()
    }
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }
  loading.value = false

}

// 刷新topic和分区的offset
const mergeOffsets = () => {
  // 刷新topic 列表data，把offsets塞进去
  for (const k in data.value) {
    const v = data.value[k]
    const topic = v['topic']
    if (topic in offsets.value.start_map) {
      v['StartOffset'] = addOffsets(offsets.value.start_map[topic])
    }
    if (topic in offsets.value.end_map) {
      v['EndOffset'] = addOffsets(offsets.value.end_map[topic])
    }
    if (topic in offsets.value.commit_map) {
      v['CommittedOffset'] = addOffsets(offsets.value.commit_map[topic])
    }
  }

  for (const k in partitions_data.value) {
    const v = partitions_data.value[k]
    const topic = v['topic']
    const partitions_num = v['partition']
    if (topic in offsets.value.start_map) {
      v['StartOffset'] = offsets.value.start_map[topic][partitions_num]['At']
    }
    if (topic in offsets.value.end_map) {
      v['EndOffset'] = offsets.value.end_map[topic][partitions_num]['At']
    }
    if (topic in offsets.value.commit_map) {
      v['CommittedOffset'] = offsets.value.commit_map[topic][partitions_num]['At']
    }

  }

}

const addOffsets = (item) => {

  let count = 0;
  for (const k in item) {
    const at = item[k]['At']
    if (at > 0) {
      count += at
    }
  }
  return count
}

const getGroups = async () => {
  loading.value = true
  try {
    const res = await GetGroups()
    if (res.err !== "") {
      message.error(res.err, {duration:  5000})
    } else {
      if (res.results) {
        let groups = []
        for (const k in res.results) {
          const data = res.results[k]
          groups.push({
            label: data['Group'],
            value: data['Group'],
            State: data['State'],
            ProtocolType: data['ProtocolType'],
            Coordinator: data['Coordinator'],
          })
        }
        groups.sort((a, b) => a['label'] > b['label'] ? 1 : -1)
        group_data.value = groups
      }
    }
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }
  loading.value = false

}

const deleteTopic = async (row) => {
  dialog.info({
    title: 'Warning',
    content: `${t('common.deleteOk')}  Topic: ${row.topic}`,
    positiveText: t('common.enter'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      await deleteTopicFunc(row.topic)
    }
  })
}
const deleteTopicFunc = async (topic) => {
  loading.value = true
  try {
    const res = await DeleteTopic([topic])
    if (res.err !== "") {
      message.error(res.err, {duration:  5000})
    } else {
      message.success(t('common.deleteFinish'))
      await getData()
      emitter.emit('refreshTopic')
    }
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }
  loading.value = false

}

const addTopic = async () => {
  loading.value = true
  try {
    let configs = {}
    if (isValidJson(topic_add.value.configs)) {
      configs = JSON.parse(topic_add.value.configs)
    }
    const res = await CreateTopics(topic_add.value.topics, topic_add.value.partitions, topic_add.value.replication_factor, configs)
    if (res.err !== "") {
      message.error(res.err, {duration:5000})
    } else {
      message.success(t('message.addOk'))
      showDrawer.value = false
      topic_add.value.topics = []
      await getData()
      emitter.emit('refreshTopic')
    }
  } catch (e) {
    message.error(e.message, {duration:5000})
  }
  loading.value = false

}
const addTopicPartition = async () => {
  loading.value = true
  try {
    const res = await CreatePartitions([activeDetailTopic.value], addPartitionNum.value)
    if (res.err !== "") {
      message.error(res.err, {duration:5000})
    } else {
      message.success(t('message.addOk'))
      await getData()
    }
  } catch (e) {
    message.error(e.message, {duration:5000})
  }
  loading.value = false
  showModal.value = false
  await getTopicDetail(activeDetailTopic.value)

}

const alterTopicConfig = async (topic, name, value) => {
  loading.value = true
  try {
    const res = await AlterTopicConfig(topic, name, value)
    if (res.err !== "") {
      message.error(res.err, {duration:5000})
    } else {
      message.success(t('message.editOk'))
      await getTopicConfig(activeConfigTopic.value)
    }
  } catch (e) {
    message.error(e.message, {duration:5000})
  }
  loading.value = false

}

// ---- 清理消息（DeleteRecords）----
const showDeleteRecords = ref(false)
const deleteRecordsForm = ref({topic: '', offset: 0, all: true})
const deleteRecordsLoading = ref(false)

const openDeleteRecords = (row) => {
  deleteRecordsForm.value = {topic: row.topic, offset: 0, all: true}
  showDeleteRecords.value = true
}

const doDeleteRecords = async () => {
  const f = deleteRecordsForm.value
  deleteRecordsLoading.value = true
  try {
    const res = await DeleteRecords(f.topic, [], f.all ? -1 : Number(f.offset || 0))
    if (res.err !== "") {
      message.error(res.err, {duration: 8000})
    } else {
      message.success(t('topic.deleteRecordsDone'))
      showDeleteRecords.value = false
      await getData()
    }
  } catch (e) {
    message.error(e.message, {duration: 5000})
  } finally {
    deleteRecordsLoading.value = false
  }
}

// ---- 副本重分配 ----
const showReassign = ref(false)
const reassignForm = ref({topic: '', json: '{}'})
const reassignLoading = ref(false)

const openReassign = (row) => {
  // 预填当前分区到副本的映射，方便修改
  let prefilled = {}
  try {
    const detail = data.value.find(item => item['topic'] === row.topic)
    if (detail && detail.partitions) {
      for (const p of detail.partitions) {
        prefilled[String(p.partition)] = p.replicas
      }
    }
  } catch (_) {}
  reassignForm.value = {
    topic: row.topic,
    json: JSON.stringify(prefilled, null, 2),
  }
  showReassign.value = true
}

const doReassign = async () => {
  const f = reassignForm.value
  let assignments
  try {
    assignments = JSON.parse(f.json)
  } catch (e) {
    message.error(t('topic.reassignInvalidJson'), {duration: 5000})
    return
  }
  reassignLoading.value = true
  try {
    const res = await AlterPartitionReassignments(f.topic, assignments)
    if (res.err !== "") {
      message.error(res.err, {duration: 8000})
    } else {
      message.success(t('topic.reassignDone'))
      showReassign.value = false
    }
  } catch (e) {
    message.error(e.message, {duration: 5000})
  } finally {
    reassignLoading.value = false
  }
}
</script>


<style scoped>

</style>