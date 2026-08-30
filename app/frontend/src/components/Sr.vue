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
      <h2>{{ t('sr.title') }}</h2>
      <n-tag :type="connected ? 'success' : 'warning'" size="small">
        {{ connected ? t('sr.connected') : t('sr.notConnected') }}
      </n-tag>
      <n-text v-if="connected" depth="3">{{ srUrl }}</n-text>
    </n-flex>

    <!-- 连接配置 -->
    <n-form inline label-placement="top" label-width="auto" style="text-align: left;">
      <n-form-item label="URL" path="url">
        <n-input v-model:value="srForm.url" placeholder="http://localhost:8081" style="width: 260px"/>
      </n-form-item>
      <n-form-item :label="t('sr.user')" path="user">
        <n-input v-model:value="srForm.user" :placeholder="t('sr.userOptional')" style="width: 140px"/>
      </n-form-item>
      <n-form-item :label="t('sr.password')" path="pass">
        <n-input v-model:value="srForm.pass" type="password" :placeholder="t('sr.passwordOptional')" style="width: 140px"/>
      </n-form-item>
      <n-form-item :label="t('conn.skipTLSVerify')" path="skip_tls">
        <n-switch v-model:value="srForm.skip_tls" :round="false" checked-value="true" unchecked-value="false"/>
      </n-form-item>
      <n-form-item>
        <n-button type="primary" :loading="connecting" @click="connectSR" :render-icon="renderIcon(LinkOutlined)">
          {{ t('sr.connect') }}
        </n-button>
      </n-form-item>
    </n-form>

    <!-- Subjects 列表 -->
    <n-flex align="center">
      <n-button @click="getSubjects" :disabled="!connected" :render-icon="renderIcon(RefreshOutlined)">
        {{ t('common.refresh') }}
      </n-button>
      <n-text>{{ t('common.count') }}：{{ subjects.length }}</n-text>
    </n-flex>

    <n-data-table
        :columns="columns"
        :data="subjects"
        size="small"
        :bordered="false"
        striped
        :pagination="pagination"
    />
  </n-flex>

  <!-- 版本抽屉 -->
  <n-drawer v-model:show="showDrawer" :width="720">
    <n-drawer-content :title="`${activeSubject} — ${t('sr.versions')}`">
      <n-flex align="center" style="margin-bottom: 12px">
        <n-select v-model:value="activeVersion" :options="versionOptions" style="width: 160px"
                  :placeholder="t('sr.selectVersion')"/>
        <n-button :disabled="activeVersion === null" @click="loadSchema" :render-icon="renderIcon(RefreshOutlined)">
          {{ t('common.read') }}
        </n-button>
        <n-popconfirm @positive-click="deleteVersion">
          <template #trigger>
            <n-button type="error" secondary :disabled="activeVersion === null">{{ t('sr.deleteVersion') }}</n-button>
          </template>
          {{ t('common.deleteOk') }}
        </n-popconfirm>
      </n-flex>

      <n-descriptions v-if="schemaInfo" :column="3" size="small" bordered style="margin-bottom: 12px">
        <n-descriptions-item label="ID">{{ schemaInfo.id }}</n-descriptions-item>
        <n-descriptions-item label="Version">{{ schemaInfo.version }}</n-descriptions-item>
        <n-descriptions-item label="Type">{{ schemaInfo.type || 'AVRO' }}</n-descriptions-item>
      </n-descriptions>

      <n-input
          v-if="schemaInfo"
          :value="formatSchema"
          type="textarea"
          readonly
          :rows="20"
          style="font-family: monospace"
      />
    </n-drawer-content>
  </n-drawer>
</template>

<script setup>
import {computed, h, onMounted, ref} from "vue"
import {NButton, NButtonGroup, NDataTable, NIcon, NPopconfirm, NTag, NText, useMessage} from 'naive-ui'
import {
  DeleteForeverTwotone,
  LinkOutlined,
  MoreVertFilled,
  RefreshOutlined,
  VisibilityOutlined,
} from "@vicons/material"
import {refColumns, renderIcon} from "../utils/common"
import {useI18n} from "vue-i18n"
import {
  DeleteSRSchemaVersion,
  DeleteSRSubject,
  GetSRSchema,
  GetSRStatus,
  GetSRSubjects,
  GetSRSubjectVersions,
  SetSRCompatibility,
  SetSchemaRegistry,
} from "../../wailsjs/go/service/Service"
import {GetConfig, SaveConfig} from "../../wailsjs/go/config/AppConfig"

const {t} = useI18n()
const message = useMessage()

const connected = ref(false)
const srUrl = ref('')
const connecting = ref(false)
const srForm = ref({url: '', user: '', pass: '', skip_tls: 'false'})

const subjects = ref([])
const showDrawer = ref(false)
const activeSubject = ref('')
const activeVersion = ref(null)
const versions = ref([])
const schemaInfo = ref(null)

const pagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [5, 10, 20, 40],
  onChange: (page) => { pagination.value.page = page },
  onUpdatePageSize: (pageSize) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
  },
})

const versionOptions = computed(() => versions.value.map(v => ({label: `v${v}`, value: v})))

const formatSchema = computed(() => {
  if (!schemaInfo.value) return ''
  try {
    return JSON.stringify(JSON.parse(schemaInfo.value.schema), null, 2)
  } catch (_) {
    return schemaInfo.value.schema
  }
})

const compatOptions = [
  'NONE', 'BACKWARD', 'BACKWARD_TRANSITIVE', 'FORWARD', 'FORWARD_TRANSITIVE', 'FULL', 'FULL_TRANSITIVE',
]

const viewVersions = async (row) => {
  activeSubject.value = row.subject
  const res = await GetSRSubjectVersions(row.subject)
  if (res.err !== "") {
    message.error(res.err, {duration: 5000})
    return
  }
  versions.value = res.result.versions || []
  activeVersion.value = versions.value.length ? versions.value[versions.value.length - 1] : null
  schemaInfo.value = null
  if (activeVersion.value !== null) {
    await loadSchema()
  }
  showDrawer.value = true
}

const loadSchema = async () => {
  const res = await GetSRSchema(activeSubject.value, activeVersion.value)
  if (res.err !== "") {
    message.error(res.err, {duration: 5000})
    return
  }
  schemaInfo.value = res.result
}

const deleteVersion = async () => {
  const res = await DeleteSRSchemaVersion(activeSubject.value, activeVersion.value)
  if (res.err !== "") {
    message.error(res.err, {duration: 5000})
    return
  }
  message.success(t('common.deleteFinish'))
  await viewVersions({subject: activeSubject.value})
  await getSubjects()
}

const deleteSubject = async (subject) => {
  const res = await DeleteSRSubject(subject, false)
  if (res.err !== "") {
    message.error(res.err, {duration: 5000})
    return
  }
  message.success(t('common.deleteFinish'))
  await getSubjects()
}

const setCompat = async (subject, level) => {
  const res = await SetSRCompatibility(subject, level)
  if (res.err !== "") {
    message.error(res.err, {duration: 5000})
    return
  }
  message.success(t('message.editOk'))
  await getSubjects()
}

const columns = [
  {title: 'Subject', key: 'subject', width: 100},
  {title: t('sr.versions'), key: 'version_count', width: 30},
  {
    title: t('sr.compatibility'), key: 'compatibility', width: 40,
    render: (row) => h(NTag, {type: 'info'}, {default: () => row.compatibility || 'N/A'}),
  },
  {
    title: t('common.action'),
    key: 'actions',
    width: 80,
    render: (row) => h(
        NButtonGroup,
        {vertical: false},
        {
          default: () => [
            h(NButton, {
              strong: true, secondary: true,
              onClick: () => viewVersions(row),
            }, {default: () => t('sr.versions'), icon: () => h(NIcon, null, {default: () => h(VisibilityOutlined)})}),
            h(NPopconfirm, {
              onPositiveClick: () => deleteSubject(row.subject),
            }, {
              trigger: () => h(NButton, {strong: true, secondary: true, type: 'error'},
                  {default: () => t('common.delete'), icon: () => h(NIcon, null, {default: () => h(DeleteForeverTwotone)})}),
              default: () => `${t('common.deleteOk')} ${row.subject}?`,
            }),
          ],
        },
    ),
  },
  {
    title: t('sr.setCompatibility'),
    key: 'setCompat',
    width: 60,
    render: (row) => h(NButton, {
      strong: true, secondary: true,
      onClick: () => setCompat(row.subject, row.compatibility || 'BACKWARD'),
    }, {default: () => t('sr.cycleCompatibility'), icon: () => h(NIcon, null, {default: () => h(MoreVertFilled)})}),
  },
]

const getSubjects = async () => {
  const res = await GetSRSubjects()
  if (res.err !== "") {
    message.error(res.err, {duration: 5000})
    return
  }
  subjects.value = (res.results || []).sort((a, b) => a.subject > b.subject ? 1 : -1)
}

const connectSR = async () => {
  if (!srForm.value.url) {
    message.error(t('sr.urlRequired'), {duration: 5000})
    return
  }
  connecting.value = true
  try {
    const res = await SetSchemaRegistry(
        srForm.value.url, srForm.value.user, srForm.value.pass, srForm.value.skip_tls === 'true')
    if (res.err !== "") {
      message.error(res.err, {duration: 5000})
      return
    }
    const config = await GetConfig()
    config.schema_registry = {
      url: srForm.value.url,
      user: srForm.value.user,
      pass: srForm.value.pass,
      skip_tls: srForm.value.skip_tls,
    }
    await SaveConfig(config)
    await refreshStatus()
    await getSubjects()
    message.success(t('message.connectSuccess'))
  } finally {
    connecting.value = false
  }
}

const refreshStatus = async () => {
  const res = await GetSRStatus()
  if (res.err === "") {
    connected.value = res.result.connected
    srUrl.value = res.result.url || ''
  }
}

onMounted(async () => {
  // 从配置恢复 Schema Registry 连接
  try {
    const config = await GetConfig()
    if (config.schema_registry && config.schema_registry.url) {
      srForm.value = {
        url: config.schema_registry.url || '',
        user: config.schema_registry.user || '',
        pass: config.schema_registry.pass || '',
        skip_tls: config.schema_registry.skip_tls || 'false',
      }
      const res = await SetSchemaRegistry(
          srForm.value.url, srForm.value.user, srForm.value.pass, srForm.value.skip_tls === 'true')
      if (res.err === "") {
        connected.value = true
        srUrl.value = srForm.value.url
      }
    } else {
      await refreshStatus()
    }
  } catch (e) {
    console.error(e)
  }
  if (connected.value) {
    await getSubjects()
  }
})
</script>
