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
  <div>
    <n-flex vertical>
      <n-flex align="center">
        <h2>{{ t('conn.title') }}</h2>
        <n-text>{{ t('common.count') }}：{{ Nodes?Nodes.length:0 }}</n-text>
        <n-button tertiary type="primary" @click="addNewNode" :render-icon="renderIcon(AddFilled)">{{
            t('conn.add')
          }}
        </n-button>
      </n-flex>
      <n-spin :show="spin_loading" description="Connecting...">

        <n-grid :x-gap="12" :y-gap="12" :cols="4">
          <n-gi v-for="node in Nodes" :key="node.id">
            <n-card :title="node.name" @click="selectNode(node)" hoverable class="conn_card">

              <template #header-extra>
                <n-space>
                  <n-button @click.stop="editNode(node)" size="small">
                    {{ t('common.edit') }}
                  </n-button>
                  <n-popconfirm @positive-click="deleteNode(node.id)">
                    <template #trigger>
                      <n-button @click.stop size="small">
                        {{ t('common.delete') }}
                      </n-button>
                    </template>
                    {{ t('common.deleteOk') }}
                  </n-popconfirm>
                </n-space>
              </template>
              <n-descriptions :column="1" label-placement="left">
                <n-descriptions-item label="address">
                  {{ node.bootstrap_servers.length > 30 ? node.bootstrap_servers.substring(0, 30) + '...' : node.bootstrap_servers }}
                </n-descriptions-item>
              </n-descriptions>
            </n-card>
          </n-gi>
        </n-grid>
      </n-spin>
    </n-flex>

    <n-drawer v-model:show="showEditDrawer" :width="500" placement="right">
      <n-drawer-content :title="drawerTitle">
        <n-form
            ref="formRef"
            :model="currentNode"
            :rules="{
              name: {required: true, message: t('conn.please_add_name'), trigger: 'blur'},
              bootstrap_servers: {required: true, message: t('conn.please_add_link'), trigger: 'blur'},
            }"
            label-placement="top"
            style="text-align: left;"
        >
          <n-form-item :label="t('common.name')" path="name">
            <n-input v-model:value="currentNode.name" :placeholder="t('conn.input_name')"/>
          </n-form-item>

          <n-form-item :label="t('conn.bootstrap_servers')" path="bootstrap_servers">
            <n-flex vertical>
              <n-input v-model:value="currentNode.bootstrap_servers" placeholder="127.0.0.1:9092,127.0.0.1:9093"/>
              {{ t('conn.tip') }}
            </n-flex>
          </n-form-item>
          <n-form-item :label="t('conn.tls')" path="tls">
            <n-switch :round="false" checked-value="enable" unchecked-value="disable" v-model:value="currentNode.tls"/>
          </n-form-item>

          <div v-if="currentNode.tls === 'enable'" style="margin-left: 10px">
            <n-form-item :label="t('conn.skipTLSVerify')" path="skipTLSVerify">
              <n-switch :round="false" checked-value="true" unchecked-value="false"
                        v-model:value="currentNode.skipTLSVerify"/>
            </n-form-item>

            <n-form-item label="TLS Cert File" path="tls_cert_file">
              <!--客户端或服务器证书用于验证客户端或服务器的身份。-->
              <n-flex vertical align="flex-start">
                <n-button @click="SelectFile('tls_cert_file','*.crt;*.pem;*.cer;*.der')">.crt/pem/cer/der</n-button>
                <n-flex align="center" v-if="currentNode.tls_cert_file">
                  <p style="color: gray;">{{ currentNode.tls_cert_file }}</p>
                  <n-button size="tiny" @click="currentNode.tls_cert_file=''" :render-icon="renderIcon(CloseFilled)"/>
                </n-flex>
              </n-flex>

            </n-form-item>

            <n-form-item label="TLS Key File" path="tls_key_file">
              <!--私钥文件用于加密和解密数据，必须妥善保管。-->
              <n-flex vertical align="flex-start">
                <n-button @click="SelectFile('tls_key_file','*.key;*.pem;*.der')">.key/pem/der</n-button>
                <n-flex align="center" v-if="currentNode.tls_key_file">
                  <p style="color: gray;">{{ currentNode.tls_key_file }}</p>
                  <n-button size="tiny" @click="currentNode.tls_key_file=''" :render-icon="renderIcon(CloseFilled)"/>
                </n-flex>
              </n-flex>

            </n-form-item>

            <n-form-item label="TLS CA File" path="tls_ca_file">
              <!--CA 证书是用于验证服务器或客户端证书的根证书或中间证书。-->
              <n-flex vertical align="flex-start">
                <n-button @click="SelectFile('tls_ca_file','*.crt;*.pem;*.cer;*.der')">.crt/pem/cer/der</n-button>
                <n-flex align="center" v-if="currentNode.tls_ca_file">
                  <p style="color: gray;">{{ currentNode.tls_ca_file }}</p>
                  <n-button size="tiny" @click="currentNode.tls_ca_file=''" :render-icon="renderIcon(CloseFilled)"/>
                </n-flex>
              </n-flex>
            </n-form-item>
          </div>


          <!-- 添加 SSH 代理配置 -->
          <n-form-item :label="t('conn.use_ssh')" path="use_ssh">
            <n-switch :round="false" checked-value="enable" unchecked-value="disable" v-model:value="currentNode.use_ssh" />
          </n-form-item>
          <div v-if="currentNode.use_ssh === 'enable'" style="margin-left: 10px">
            <n-form-item :label="t('conn.ssh_host')" path="ssh_host" >
              <n-input v-model:value="currentNode.ssh_host" placeholder="SSH Host (e.g., 192.168.1.100)" />
            </n-form-item>
            <n-form-item :label="t('conn.ssh_port')" path="ssh_port" >
              <n-input-number v-model:value="currentNode.ssh_port" :default-value="22" :min="1" :max="65535" />
            </n-form-item>
            <n-form-item :label="t('conn.ssh_user')" path="ssh_user">
              <n-input v-model:value="currentNode.ssh_user" placeholder="SSH Username" />
            </n-form-item>
            <n-form-item :label="t('conn.ssh_password')" path="ssh_password">
              <n-input v-model:value="currentNode.ssh_password" type="password" placeholder="SSH Password" />
            </n-form-item>
            <n-form-item :label="t('conn.ssh_key_file')" path="ssh_key_file" >
              <n-flex vertical align="flex-start">
                <n-button @click="SelectFile('ssh_key_file')">SSH Key</n-button>
                <n-flex align="center" v-if="currentNode.ssh_key_file">
                  <p style="color: gray;">{{ currentNode.ssh_key_file }}</p>
                  <n-button size="tiny" @click="currentNode.ssh_key_file=''" :render-icon="renderIcon(CloseFilled)" />
                </n-flex>
              </n-flex>
            </n-form-item>
          </div>


          <n-form-item :label="t('conn.use_sasl')" path="sasl">
            <n-switch :round="false" checked-value="enable" unchecked-value="disable" v-model:value="currentNode.sasl"/>
          </n-form-item>

          <div v-if="currentNode.sasl === 'enable'" style="margin-left: 10px">
            <n-form-item :label="t('conn.sasl_mechanism')" path="sasl_mechanism">
              <n-select
                  v-model:value="currentNode.sasl_mechanism"
                  :options="sasl_mechanism_options"
                  :placeholder="t('common.check')"
                  filterable
                  clearable
                  style="width: 200px"
              />
            </n-form-item>

            <n-form-item :label="t('conn.sasl_user')" path="sasl_user">
              <n-input v-model:value="currentNode.sasl_user" :placeholder="t('conn.sasl_user')"/>
            </n-form-item>

            <n-form-item :label="t('conn.sasl_pwd')" path="sasl_pwd">
              <n-input
                  v-model:value="currentNode.sasl_pwd"
                  type="password"
                  :placeholder="saslPwdPlaceholder"
              />
            </n-form-item>
            <n-text v-if="currentNode.sasl_mechanism === 'OAUTHBEARER'" depth="3" style="font-size: 12px">
              {{ t('conn.oauthTip') }}
            </n-text>
            <n-form-item v-if="currentNode.sasl_mechanism === 'AWS_MSK_IAM'"
                         :label="t('conn.sessionToken')" path="sasl_session_token">
              <n-input v-model:value="currentNode.sasl_session_token"
                       :placeholder="t('conn.sessionTokenOptional')"/>
            </n-form-item>
            <n-text v-if="currentNode.sasl_mechanism === 'AWS_MSK_IAM'" depth="3" style="font-size: 12px">
              {{ t('conn.mskTip') }}
            </n-text>
          </div>

          <n-form-item label="kerberos" path="sasl">
            <n-switch :round="false" checked-value="enable" unchecked-value="disable" v-model:value="currentNode.use_kerberos"/>
          </n-form-item>

          <div v-if="currentNode.use_kerberos === 'enable'" style="margin-left: 10px">
            <n-form-item :label="t('conn.kerberos_user_keytab')" path="kerberos_user_keytab">
              <n-flex vertical align="flex-start">
                <n-button @click="SelectFile('kerberos_user_keytab')">keytab</n-button>
                <n-flex align="center" v-if="currentNode.kerberos_user_keytab">
                  <p style="color: gray;">{{ currentNode.kerberos_user_keytab }}</p>
                  <n-button size="tiny" @click="currentNode.kerberos_user_keytab=''"
                            :render-icon="renderIcon(CloseFilled)"/>
                </n-flex>
              </n-flex>

            </n-form-item>

            <n-form-item :label="t('conn.kerberos_krb5_conf')" path="kerberos_krb5_conf">
              <n-flex vertical align="flex-start">
                <n-button @click="SelectFile('kerberos_krb5_conf')">krb5_conf</n-button>
                <n-flex align="center" v-if="currentNode.kerberos_krb5_conf">
                  <p style="color: gray;">{{ currentNode.kerberos_krb5_conf }}</p>
                  <n-button size="tiny" @click="currentNode.kerberos_krb5_conf=''"
                            :render-icon="renderIcon(CloseFilled)"/>
                </n-flex>
              </n-flex>
            </n-form-item>

            <n-form-item :label="t('conn.Kerberos_user')" path="Kerberos_user">
              <n-input v-model:value="currentNode.Kerberos_user"/>
            </n-form-item>

            <n-form-item :label="t('conn.Kerberos_realm')" path="Kerberos_realm">
              <n-input v-model:value="currentNode.Kerberos_realm"/>
            </n-form-item>

            <n-form-item :label="t('conn.kerberos_service_name')" path="kerberos_service_name">
              <n-input v-model:value="currentNode.kerberos_service_name"/>
            </n-form-item>
          </div>


        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button tertiary type="primary" @click="test_connect" :loading="test_connect_loading">{{
                t('conn.test')
              }}
            </n-button>
            <n-button @click="showEditDrawer = false">{{ t('common.cancel') }}</n-button>
            <n-button type="primary" @click="saveNode">{{ t('common.save') }}</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {NButton, useMessage} from 'naive-ui'
import {renderIcon} from "../utils/common";
import {AddFilled, CloseFilled} from "@vicons/material";
import emitter, { setConnectName } from "../utils/eventBus";
import {SetConnect, TestClient} from "../../wailsjs/go/service/Service";
import {GetConfig, OpenFileDialog, SaveConfig} from "../../wailsjs/go/config/AppConfig";
import {useI18n} from 'vue-i18n'

const {t} = useI18n()


const message = useMessage()

const Nodes = ref([])

const showEditDrawer = ref(false)
const currentNode = ref({
  id: 0,
  name: '',
  bootstrap_servers: '',
  tls: 'disable',
  skipTLSVerify: 'true',
  tls_cert_file: '',
  tls_key_file: '',
  tls_ca_file: '',
  sasl: 'disable',
  sasl_mechanism: "PLAIN",
  sasl_user: '',
  sasl_pwd: '',
  sasl_session_token: '',
  use_kerberos: 'disable',
  kerberos_user_keytab: '',
  kerberos_krb5_conf: '',
  Kerberos_user: '',
  Kerberos_realm: '',
  kerberos_service_name: '',
  use_ssh: 'disable', // 新增 SSH 开关
  ssh_host: '',       // SSH 主机
  ssh_port: 22,       // SSH 端口
  ssh_user: '',       // SSH 用户名
  ssh_password: '',   // SSH 密码
  ssh_key_file: '',   // SSH 私钥文件
})
const isEditing = ref(false)
const spin_loading = ref(false)
const test_connect_loading = ref(false)
const sasl_mechanism_options = [
  {
    label: 'PLAIN',
    value: 'PLAIN'
  },
  {
    label: 'SCRAM-SHA-256',
    value: 'SCRAM-SHA-256'
  },
  {
    label: 'SCRAM-SHA-512',
    value: 'SCRAM-SHA-512'
  },
  {
    label: 'GSSAPI',
    value: 'GSSAPI'
  },
  {
    label: 'OAUTHBEARER (static token)',
    value: 'OAUTHBEARER'
  },
  {
    label: 'AWS MSK IAM',
    value: 'AWS_MSK_IAM'
  },
]

const drawerTitle = computed(() => isEditing.value ? t('conn.edit') : t('conn.add_link'))

const saslPwdPlaceholder = computed(() => {
  if (currentNode.value.sasl_mechanism === 'OAUTHBEARER') return t('conn.oauthTokenPlaceholder')
  return t('conn.sasl_pwd')
})

const formRef = ref(null)

onMounted(() => {
  refreshNodeList()
})

const refreshNodeList = async () => {
  spin_loading.value = true
  const config = await GetConfig()
  // 去掉name为null的历史脏数据
  Nodes.value = config.connects.filter(node => node.name !== null && node.name !== "")
  spin_loading.value = false
}

function editNode(node) {
  currentNode.value = {...node}
  isEditing.value = true
  showEditDrawer.value = true
}

// 新增
const addNewNode = async () => {
  currentNode.value = {
    id: 0,
    name: '',
    bootstrap_servers: '',
    tls: 'disable',
    skipTLSVerify: 'true',
    tls_cert_file: '',
    tls_key_file: '',
    tls_ca_file: '',
    sasl: 'disable',
    sasl_mechanism: 'PLAIN',
    sasl_user: '',
    sasl_pwd: '',
    sasl_session_token: '',
    kerberos_user_keytab: '',
    kerberos_krb5_conf: '',
    Kerberos_user: '',
    Kerberos_realm: '',
    kerberos_service_name: '',
    use_ssh: 'disable',
    ssh_host: '',
    ssh_port: 22,
    ssh_user: '',
    ssh_password: '',
    ssh_key_file: '',
  };
  isEditing.value = false
  showEditDrawer.value = true
}

// 保存
const saveNode = async () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {

      const config = await GetConfig()
      // edit
      if (isEditing.value) {
        const index = Nodes.value.findIndex(node => node.id === currentNode.value.id)
        if (index !== -1) {
          Nodes.value[index] = {...currentNode.value}
        }
      } else {
        // add
        const newId = Math.max(...Nodes.value.map(node => node.id), 0) + 1
        Nodes.value.push({...currentNode.value, id: newId})
      }
      console.log(config)

      // 保存
      config.connects = Nodes.value
      await SaveConfig(config)
      showEditDrawer.value = false

      await refreshNodeList()
      message.success(t('message.saveSuccess'))
    } else {
      message.error(t('message.mustFill'), {duration:  5000})
    }
  })
}

// 删除
const deleteNode = async (id) => {
  Nodes.value = Nodes.value.filter(node => node.id !== id)
  const config = await GetConfig()
  config.connects = Nodes.value
  await SaveConfig(config)
  await refreshNodeList()
  message.success(t('common.deleteFinish'))
}

// 测试连接
const test_connect = async () => {
  console.log(currentNode.value)
  formRef.value?.validate(async (errors) => {
    if (!errors) {

      test_connect_loading.value = true
      try {
        const res = await TestClient(currentNode.value.name, currentNode.value)
        if (res.err !== "") {
          message.error(t('message.connectErr') + "：" + res.err, {duration:  5000})
        } else {
          message.success(t('message.connectSuccess'), {duration:  5000})
        }
      } catch (e) {
        message.error(e.message, {duration:  5000})
      }
      test_connect_loading.value = false
    } else {
      message.error(t('message.mustFill'), {duration:  5000})
    }
  })
}

// 选择节点连接
const selectNode = async (node) => {
  // 这里实现切换菜单的逻辑
  console.log('选中节点:', node)
  spin_loading.value = true
  try {
    const res = await SetConnect(node.name, node, false)
    if (res.err !== "") {
      message.error(t('message.connectErr') + "：" + res.err, {duration:  5000})
    } else {
      emitter.emit('menu_select', "node")
      setConnectName(node.name)
      emitter.emit('selectNode', node)
      message.success(t('message.connectSuccess'))
    }
  } catch (e) {
    message.error(e.message, {duration:  5000})
  }
  spin_loading.value = false
}

// 文件选择
const SelectFile = async (key, pattern) => {
  try {
    const trimmedPattern = typeof pattern === 'string' ? pattern.trim() : ''
    const options = trimmedPattern && trimmedPattern !== '*'
        ? {Filters: [{Pattern: trimmedPattern}]}
        : {}
    const filePath = await OpenFileDialog(options)
    if (filePath) {
      currentNode.value[key] = filePath
    }
  } catch (err) {
    console.error('Failed to open file dialog:', err)
  }
};

</script>

<style>

.lightTheme .conn_card {
  background-color: #fafafc
}
</style>
