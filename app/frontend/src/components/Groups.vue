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
      <h2>{{ t('group.title') }}</h2>
      <n-button @click="getData" text :render-icon="renderIcon(RefreshOutlined)">{{ t('common.refresh') }}</n-button>
      <n-text>{{ t('common.count') }}：{{ group_data ? group_data.length : 0 }}</n-text>
      <n-button @click="downloadAllDataCsv" :render-icon="renderIcon(DriveFileMoveTwotone)">{{ t('common.csv') }}
      </n-button>
    </n-flex>
    <n-input v-model:value="searchText" clearable placeholder="search" style="max-width: 20%"
             @keyup.enter="searchData"/>

    <n-spin :show="loading" :description="t('common.connecting')">
      <n-data-table
          :columns="refColumns(columns)"
          :data="filter_data"
          size="small"
          :bordered="false"
          striped
          :pagination="pagination"
      />
    </n-spin>
  </n-flex>

  <n-modal v-model:show="showReset" preset="dialog" :title="t('group.resetTitle')">
    <n-form label-placement="top" style="text-align: left;">
      <n-form-item label="Group">
        <n-tag type="info">{{ resetForm.group }}</n-tag>
      </n-form-item>
      <n-form-item :label="t('group.resetStrategy')">
        <n-select v-model:value="resetForm.strategy" :options="resetStrategyOptions" style="width: 260px"/>
      </n-form-item>
      <n-form-item v-if="resetForm.strategy === 'timestamp'" :label="t('consumer.startTimestamp')">
        <n-date-picker v-model:value="resetForm.timestamp" type="datetime" style="width: 260px"
                       value-format="timestamp"/>
      </n-form-item>
      <n-form-item v-if="resetForm.strategy === 'absolute'" :label="t('group.resetOffsetValue')">
        <n-input-number v-model:value="resetForm.offset" :min="0" style="width: 260px"/>
      </n-form-item>
      <n-form-item :label="t('group.resetTopics')">
        <n-dynamic-tags v-model:value="resetForm.topics"/>
      </n-form-item>
      <n-text depth="3">{{ t('group.resetTip') }}</n-text>
    </n-form>
    <template #action>
      <n-button @click="showReset = false">{{ t('common.cancel') }}</n-button>
      <n-button type="warning" :loading="resetLoading" @click="doReset">{{ t('common.enter') }}</n-button>
    </template>
  </n-modal>

  <n-drawer v-model:show="showDrawer" :width="800">
    <n-drawer-content :title="t('group.member')">
      <n-data-table
          :columns="refColumns(members_columns)"
          :data="members_data"
          :bordered="false"
          :pagination="pagination"
      />
    </n-drawer-content>
  </n-drawer>

</template>
<script setup>
import {h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NButtonGroup, NDataTable, NIcon, NInput, NInputNumber, NModal, NDatePicker, NPopconfirm, NSelect, NTag, NText, useMessage} from 'naive-ui'
import {createCsvContent, download_file, refColumns, renderIcon} from "../utils/common";
import {DeleteForeverTwotone, DriveFileMoveTwotone, RefreshOutlined, SettingsTwotone, RestoreOutlined} from "@vicons/material";
import {DeleteGroup, GetGroupMembers, GetGroups, ResetGroupOffsets} from "../../wailsjs/go/service/Service";
import {useI18n} from "vue-i18n";

const {t} = useI18n()

const group_data = ref([])
const members_data = ref([])
const loading = ref(false)
const showDrawer = ref(false)
const message = useMessage()

const filter_data = ref([])
const searchText = ref(null)

const selectNode = async (node) => {
  group_data.value = []
  filter_data.value = []
  members_data.value = []
  searchText.value = null

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
    const res = await GetGroups()
    if (res.err !== "") {
      message.error(res.err, {duration: 5000})
    } else {
      if (res.results) {
        res.results.sort((a, b) => a['Group'] > b['Group'] ? 1 : -1)
        group_data.value = res.results
        console.log(res.results)
        searchData()
      }
    }
  } catch (e) {
    message.error(e.message, {duration: 5000})
  }
  loading.value = false
}

const getMembers = async (group) => {
  loading.value = true
  try {
    const res = await GetGroupMembers([group])
    if (res.err !== "") {
      message.error(res.err, {duration: 5000})
    } else {
      if (res.results[0]) {
        let data0 = res.results[0]
        members_data.value = data0['Members']
      } else {
        message.warning(t('message.noMemberFound'))
      }
    }

  } catch (e) {
    message.error(e.message, {duration: 5000})
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
      group_data.value, columns
  )
  download_file(csvContent, 'kafka-group.csv', 'text/csv;charset=utf-8;')
}


const columns = [
  {title: 'Group', key: 'Group', width: 60},
  {
    title: 'Coordinator', key: 'Coordinator', width: 20,
    render: (row) => h(NTag, {type: "info"}, {default: () => row['Coordinator']}),
  },
  {
    title: 'State', key: 'State', width: 20,
    render: (row) => h(NTag, {type: "success"}, {default: () => row['State'] || 'unknown'}),
  },
  {
    title: 'ProtocolType',
    key: 'ProtocolType',
    width: 20,
  },
  {
    title: t('common.action'),
    key: 'actions',
    width: 80,  // 调整宽度以适应两个按钮
    render: (row) => h(
        NButtonGroup,
        {
          vertical: false,
        },
        {
          default: () => [
            h(
                NButton,
                {
                  strong: true,
                  secondary: true,
                  onClick: async () => {
                    await getMembers(row['Group'])
                    showDrawer.value = true
                  }
                },
                {default: () => t('group.member'), icon: () => h(NIcon, null, {default: () => h(SettingsTwotone)})}
            ),
            h(
                NButton,
                {
                  strong: true,
                  secondary: true,
                  type: 'warning',
                  onClick: () => openReset(row['Group'])
                },
                {
                  default: () => t('group.resetOffset'),
                  icon: () => h(NIcon, null, {default: () => h(RestoreOutlined)})
                }
            ),
            h(
                NPopconfirm,
                {
                  onPositiveClick: () => deleteGroups(row["Group"])
                },
                {
                  trigger: () =>
                      h(
                          NButton,
                          {
                            strong: true,
                            secondary: true,
                            type: 'error'
                          },
                          {
                            default: () => t('common.delete'),
                            icon: () => h(NIcon, null, {default: () => h(DeleteForeverTwotone)})
                          }
                      )
                  ,
                  default: () => `${t('common.deleteOk')} Group: ${row["Group"]}?`
                }
            ),
          ]
        }
    )
  },
]

const members_columns = [
  {title: 'MemberID', key: 'MemberID', width: 20},
  {title: 'InstanceID', key: 'InstanceID', width: 20},
  {title: 'ClientID', key: 'ClientID', width: 20},
  {title: 'ClientHost', key: 'ClientHost', width: 20},
  {
    title: 'Assigned Topic & Partition',
    key: 'TPs',
    width: 60,
    render(row) {
      const tps = row.TPs;
      if (!tps || Object.keys(tps).length === 0) {
        return h(NText, {depth: 3}, {default: () => 'N/A'});
      }
      const tags = Object.entries(tps).map(([topic, partitions]) => {
        return h(
            NTag,
            {type: 'info', style: {marginRight: '6px', marginBottom: '6px'}},
            {default: () => `${topic}: ${partitions.join(', ')}`}
        );
      });
      return h('div', {style: {display: 'flex', flexWrap: 'wrap'}}, tags);
    }
  }
]

const deleteGroups = async (group) => {
  loading.value = true
  try {
    const res = await DeleteGroup(group)
    if (res.err !== "") {
      message.error(res.err, {duration: 5000})
    } else {
      message.success(t('common.deleteFinish'))
      await getData()
    }
  } catch (e) {
    message.error(e.message, {duration: 5000})
  }
  loading.value = false

}

const searchData = () => {
  if (searchText.value) {
    const query = searchText.value.toLowerCase();
    filter_data.value = group_data.value.filter(item => {
      return Object.values(item).some(val =>
          String(val).toLowerCase().includes(query)
      );
    });
  } else {
    filter_data.value = group_data.value;
  }
};

// ---- 重置消费组 Offset ----
const showReset = ref(false)
const resetLoading = ref(false)
const resetForm = ref({
  group: '',
  strategy: 'end',
  timestamp: null,
  offset: 0,
  topics: [],
})
const resetStrategyOptions = [
  {label: () => t('group.resetToEnd'), value: 'end'},
  {label: () => t('group.resetToStart'), value: 'start'},
  {label: () => t('group.resetToTimestamp'), value: 'timestamp'},
  {label: () => t('group.resetToAbsolute'), value: 'absolute'},
]

const openReset = (group) => {
  resetForm.value = {group, strategy: 'end', timestamp: null, offset: 0, topics: []}
  showReset.value = true
}

const doReset = async () => {
  const f = resetForm.value
  let value = 0
  if (f.strategy === 'timestamp') {
    if (!f.timestamp) {
      message.error(t('group.needTimestamp'), {duration: 5000})
      return
    }
    value = Number(f.timestamp)
  } else if (f.strategy === 'absolute') {
    value = Number(f.offset || 0)
  }
  resetLoading.value = true
  try {
    const res = await ResetGroupOffsets(f.group, f.topics, f.strategy, value)
    if (res.err !== "") {
      message.error(res.err, {duration: 8000})
    } else {
      const count = res.result?.offsets?.length ?? 0
      message.success(t('group.resetDone', {count}))
      showReset.value = false
    }
  } catch (e) {
    message.error(e.message, {duration: 5000})
  } finally {
    resetLoading.value = false
  }
}
</script>


<style scoped>

</style>