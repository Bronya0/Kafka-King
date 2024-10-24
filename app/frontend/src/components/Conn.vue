<template>
  <div>
    <n-flex vertical>
      <n-flex align="center">
        <h2 style="width: 42px;">集群</h2>
        <n-text>共有 {{ esNodes.length }} 个</n-text>
        <n-button @click="addNewNode" :render-icon="renderIcon(AddFilled)">添加集群</n-button>
      </n-flex>
      <n-spin :show="spin_loading" description="Connecting...">

        <n-grid :x-gap="12" :y-gap="12" :cols="4">
          <n-gi v-for="node in esNodes" :key="node.id">
            <n-card :title="node.name" @click="selectNode(node)" hoverable class="conn_card">

              <template #header-extra>
                <n-space>
                  <n-button @click.stop="editNode(node)" size="small">
                    编辑
                  </n-button>
                  <n-popconfirm @positive-click="deleteNode(node.id)" negative-text="取消" positive-text="确定">
                    <template #trigger>
                      <n-button @click.stop size="small">
                        删除
                      </n-button>
                    </template>
                    确定删除该节点吗？
                  </n-popconfirm>
                </n-space>
              </template>
              <n-descriptions :column="1" label-placement="left">
                <n-descriptions-item label="主机">
                  {{ node.host }}
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
              name: {required: true, message: '请输入名称', trigger: 'blur'},
              bootstrap_servers: {required: true, message: '请输入kafka连接地址', trigger: 'blur'},
              port: {required: true, type: 'number', message: '请输入有效的端口号', trigger: 'blur'},
            }"
            label-placement="left"
        >
          <n-form-item label="名称" path="name">
            <n-input v-model:value="currentNode.name" placeholder="输入名称"/>
          </n-form-item>
          <n-form-item label="bootstrap_servers" path="bootstrap_servers">
            <n-input v-model:value="currentNode.host" placeholder="127.0.0.1:9092"/>
          </n-form-item>
          <n-form-item label="用户名" path="username">
            <n-input v-model:value="currentNode.username" placeholder="输入用户名"/>
          </n-form-item>
          <n-form-item label="密码" path="password">
            <n-input
                v-model:value="currentNode.password"
                type="password"
                placeholder="输入密码"
            />
          </n-form-item>

          <n-form-item label="使用 SSL" path="useSSL">
            <n-switch v-model:value="currentNode.useSSL"/>
          </n-form-item>

          <n-form-item label="跳过 SSL 验证" path="skipSSLVerify">
            <n-switch v-model:value="currentNode.skipSSLVerify"/>
          </n-form-item>

          <n-form-item label="CA 证书" path="caCert">
            <n-input v-model:value="currentNode.caCert" type="textarea" placeholder="输入 CA 证书内容"/>
          </n-form-item>

        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="test_connect" :loading="test_connect_loading">连接测试</n-button>
            <n-button @click="showEditDrawer = false">取消</n-button>
            <n-button type="primary" @click="saveNode">保存</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {useMessage} from 'naive-ui'
import {renderIcon} from "../utils/common";
import {AddFilled} from "@vicons/material";
import emitter from "../utils/eventBus";
import {SetConnect} from "../../wailsjs/go/service/Service";
import {GetConfig, SaveConfig} from "../../wailsjs/go/config/AppConfig";


const message = useMessage()

const esNodes = ref([])

const showEditDrawer = ref(false)
const currentNode = ref({})
const isEditing = ref(false)
const spin_loading = ref(false)
const test_connect_loading = ref(false)

const drawerTitle = computed(() => isEditing.value ? '编辑 ES 连接' : '添加 ES 连接')

const formRef = ref(null)

onMounted(async () => {
  await refreshNodeList()
})

const refreshNodeList = async () => {
  spin_loading.value = true
  const config = await GetConfig()
  esNodes.value = config.connects
  spin_loading.value = false
}

function editNode(node) {
  currentNode.value = {...node}
  isEditing.value = true
  showEditDrawer.value = true
}

const addNewNode = async () => {
  currentNode.value = {
    name: '',
    host: '',
    port: 9200,
    username: '',
    password: '',
    useSSL: false,
    skipSSLVerify: false,
    caCert: ''
  }
  isEditing.value = false
  showEditDrawer.value = true
}

const saveNode = async () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {

      const config = await GetConfig()
      // edit
      if (isEditing.value) {
        console.log("edit")
        const index = esNodes.value.findIndex(node => node.id === currentNode.value.id)
        console.log(index)
        console.log(currentNode.value)
        if (index !== -1) {
          esNodes.value[index] = {...currentNode.value}
          console.log(currentNode.value)
        }
      } else {
        // add
        const newId = Math.max(...esNodes.value.map(node => node.id), 0) + 1
        esNodes.value.push({...currentNode.value, id: newId})
      }
      console.log(config)

      // 保存
      config.connects = esNodes.value
      console.log(config)
      await SaveConfig(config)
      showEditDrawer.value = false

      await refreshNodeList()
      message.success('保存成功')
    } else {
      message.error('请填写所有必填字段')
    }
  })
}

const deleteNode = async (id) => {
  console.log(esNodes.value)
  console.log(id)
  esNodes.value = esNodes.value.filter(node => node.id !== id)
  console.log(esNodes.value)
  const config = await GetConfig()
  config.connects = esNodes.value
  await SaveConfig(config)
  await refreshNodeList()
  message.success('删除成功')
}

const test_connect = async () => {
  test_connect_loading.value = true
  try {
    const node = currentNode.value
    const res = await TestClient(node.host, node.username, node.password, node.caCert, node.useSSL, node.skipSSLVerify)
    if (res !== "") {
      message.error("连接失败：" + res)
    } else {
      message.success('连接成功')
    }
  }catch (e) {
    message.error(e)
  }
  test_connect_loading.value = false
}
const selectNode = async (node) => {
  // 这里实现切换菜单的逻辑
  console.log('选中节点:', node)
  spin_loading.value = true

  // node：{ id: 1, name: 'ES节点1', host: 'localhost', port: 9200, username: 'user1', password: 'pass1' },
  const res = await TestClient(node.host, node.username, node.password, node.caCert, node.useSSL, node.skipSSLVerify)
  spin_loading.value = false

  console.log(res)
  if (res !== "") {
    message.error("连接失败：" + res)
  } else {
    message.success('连接成功')
    await SetConnect(node.name, node.host, node.username, node.password, node.caCert, node.useSSL, node.skipSSLVerify)
    emitter.emit('menu_select', "节点")
    emitter.emit('selectNode', node)
  }
}
</script>

<style>

.lightTheme .conn_card {
  background-color: #fafafc
}
</style>