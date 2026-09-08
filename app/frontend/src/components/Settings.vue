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
  <n-grid :x-gap="12" :cols="2" style="padding: 16px 0">
    <n-gi>
        <h2 style="text-align: left">{{ t('settings.title') }}</h2>
        <n-form :model="config" label-placement="top" style="text-align: left;">

          <n-form-item :label="t('settings.width')">
            <n-input-number v-model:value="config.width" :min="800" :max="1920" :style="{ maxWidth: '120px' }"/>
          </n-form-item>
          <n-form-item :label="t('settings.height')">
            <n-input-number v-model:value="config.height" :min="600" :max="1080" :style="{ maxWidth: '120px' }"/>
          </n-form-item>
          <n-form-item :label="t('settings.lang')">
            <n-select v-model:value="config.language" :options="languageOptions"
                      :style="{ maxWidth: '120px' }" @update:value="changeLanguage"/>
          </n-form-item>

          <n-form-item :label="t('settings.theme')">
            <n-switch
                :checked-value="darkTheme.name"
                :unchecked-value="lightTheme.name"
                v-model:value="theme"
                @update:value="changeTheme"
            >
              <template #checked-icon>
                <n-icon :component="NightlightRoundFilled"/>
              </template>
              <template #unchecked-icon>
                <n-icon :component="WbSunnyOutlined"/>
              </template>
            </n-switch>
          </n-form-item>

          <n-form-item>
            <n-flex>
              <n-button @click="saveConfig" strong type="primary">{{ t('common.save') }}</n-button>

              <n-tooltip>
                <template #trigger>
                  <n-button @click="getSysInfo()" style="width: 100px">ProcessInfo</n-button>
                </template>
                <span class="sys-info">{{ sys_info }}</span >
              </n-tooltip>
            </n-flex>
          </n-form-item>

        </n-form>
    </n-gi>
  </n-grid>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {darkTheme, lightTheme, NButton, NForm, NFormItem, NInputNumber, NSelect, useMessage,} from 'naive-ui'
import {GetConfig, SaveConfig} from '../../wailsjs/go/config/AppConfig'
import {GetProcessInfo} from '../../wailsjs/go/system/Update'

import {WindowSetSize} from "../../wailsjs/runtime";
import {NightlightRoundFilled, WbSunnyOutlined} from '@vicons/material'
import emitter from "../utils/eventBus";
import {useI18n} from "vue-i18n";

const {t} = useI18n()

const message = useMessage()
const theme = ref(lightTheme.name);
const sys_info = ref("")

const config = ref({
  width: 1248,
  height: 768,
  language: 'en-US',
  theme: theme.value,
})
const languageOptions = [
  {label: '中文', value: 'zh-CN'},
  {label: 'English', value: 'en-US'},
  {label: '日本語', value: 'ja-JP'},
  {label: '한국인', value: 'ko-KR'},
  {label: 'рускі', value: 'ru-RU'},
]

const getSysInfo = async () => {
  sys_info.value = await GetProcessInfo()
}

onMounted(async () => {
  console.info("初始化settings……")

  // 从后端加载配置
  const loadedConfig = await GetConfig()
  console.log(loadedConfig)
  config.value = loadedConfig
  theme.value = loadedConfig.theme;

  await getSysInfo()
})


const saveConfig = async () => {
  config.value.theme = theme.value
  const err = await SaveConfig(config.value)
  if (err !== "") {
    message.error(t('message.saveErr') + "：" + err, {duration:  5000})
    return
  }

  WindowSetSize(config.value.width, config.value.height)

  emitter.emit('update_theme', theme.value)
  // 可以添加保存成功的提示
  message.success(t('message.saveSuccess'))
  config.value = await GetConfig()

}


const changeTheme = () => {
  emitter.emit('update_theme', theme.value);
}

const changeLanguage = (newLang) => {
  config.value.language = newLang
  emitter.emit('language_change', newLang)
}
  
</script>
<style scoped>
.sys-info {
  white-space: pre-wrap;
  max-height: 400px;
  overflow: auto;
  text-align: left;
  display: block;
}
</style>
