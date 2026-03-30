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
  <n-page-header style="padding: 4px;--wails-draggable:drag">
    <template #avatar>
      <n-avatar :src="logo" />
    </template>
    <template #title>
      <div>{{app_name}}</div>
    </template>
    <template #subtitle>
      <n-tooltip>
        <template #trigger>
          <n-tag :type=title_tag v-if="subtitle">{{subtitle}}</n-tag>
          <n-p v-else>{{t('header.desc')}}</n-p>
        </template>
      </n-tooltip>
    </template>
    <template #extra>
      <n-flex justify="flex-end" style="--wails-draggable:no-drag" class="right-section">

        <n-button v-if="locale === 'zh-CN'" quaternary :focusable="false" @click="openUrl(qq_url)">技术交流群</n-button>

        <n-tooltip placement="bottom" trigger="hover">
          <template #trigger>
            <n-button quaternary @click="openUrl(update_url)" :render-icon="renderIcon(HouseOutlined)"/>
          </template>
          <span>HomePage</span>
        </n-tooltip>

        <n-tooltip placement="bottom" trigger="hover">
          <template #trigger>
            <n-button quaternary :focusable="false" :loading="update_loading" @click="checkForUpdates"
                      :render-icon="renderIcon(SystemUpdateAltSharp)"/>
          </template>
          <span> Check Version：{{ version.tag_name }} {{ check_msg }}</span>
        </n-tooltip>
        <n-button quaternary :focusable="false" @click="minimizeWindow" :render-icon="renderIcon(RemoveOutlined)"/>
        <n-button quaternary :focusable="false" @click="resizeWindow" :render-icon="renderIcon(MaxMinIcon)"/>
        <n-button quaternary class="close-btn" style="font-size: 22px" :focusable="false" @click="closeWindow">
          <n-icon>
            <CloseFilled/>
          </n-icon>
        </n-button>
      </n-flex>
    </template>
  </n-page-header>
</template>

<script setup>
import {NAvatar, NButton, NFlex, useNotification} from 'naive-ui'
import {
  CloseFilled,
  HouseOutlined,
  ContentCopyFilled,
  CropSquareFilled,
  RemoveOutlined,
  SystemUpdateAltSharp
} from '@vicons/material'
import logo from '../assets/images/appicon.png'
import {h, onMounted, ref, shallowRef, watch} from "vue";
import {BrowserOpenURL, Quit, WindowMaximise, WindowMinimise, WindowUnmaximise} from "../../wailsjs/runtime";
import {CheckUpdate} from '../../wailsjs/go/system/Update'
import {openUrl, renderIcon} from "../utils/common";
import {GetAppName, GetVersion} from "../../wailsjs/go/config/AppConfig";
import emitter from "../utils/eventBus";
import {useI18n} from "vue-i18n";

const {t, locale} = useI18n()

// defineProps(['options', 'value']);

// const MoonOrSunnyOutline = shallowRef(WbSunnyOutlined)
const isMaximized = ref(false);
const check_msg = ref("");
const app_name = ref("");
const title_tag = ref("success");
const MaxMinIcon = shallowRef(CropSquareFilled)
const update_url = "https://github.com/Bronya0/Kafka-King/releases"
const update_loading = ref(false)
// let theme = lightTheme
const qq_url = "https://qm.qq.com/cgi-bin/qm/qr?k=pDqlVFyLMYEEw8DPJlRSBN27lF8qHV2v&jump_from=webapi&authKey=Wle/K0ARM1YQWlpn6vvfiZuMedy2tT9BI73mUvXVvCuktvi0fNfmNR19Jhyrf2Nz"

let version = ref({
  tag_name: "",
  body: "",
})

const subtitle = ref("")

const notification = useNotification()

onMounted(async () => {
  emitter.on('selectNode', selectNode)
  // emitter.on('changeTitleType', changeTitleType)

  app_name.value = await GetAppName()

  // const config = await GetConfig()
  // MoonOrSunnyOutline.value = config.theme === lightTheme.name ? WbSunnyOutlined : NightlightRoundFilled
  const v = await GetVersion()
  version.value.tag_name = v
  subtitle.value = t('header.desc') + " " + v
  await checkForUpdates()
})

const selectNode = (node) => {
  subtitle.value = `${t('header.c_node')}：【` + node.name + "】"
}

const checkForUpdates = async () => {
  update_loading.value = true
  try {
    const v = await GetVersion()
    const resp = await CheckUpdate()
    if (!resp) {
      check_msg.value = `${t('header.netErr')}`
    } else if (resp.tag_name !== v) {
      check_msg.value = `${t('header.newVersion')}: ` + resp.name
      version.value.body = resp.body
      const n = notification.success({
        title: check_msg.value,
        content: resp.body,
        action: () =>
              h(NFlex, {justify: "flex-end" }, () => [
                h(
                    NButton,
                    {
                      type: 'primary',
                      secondary: true,
                      onClick: () => BrowserOpenURL(update_url),
                    },
                    () => t('header.down'),
                ),
                h(
                    NButton,
                    {
                      secondary: true,
                      onClick: () => {
                        n.destroy()
                      },
                    },
                    () => t('common.cancel'),
                ),
            ]),
        onPositiveClick: () => BrowserOpenURL(update_url),
      })
    }
  } finally {
    update_loading.value = false
  }
}

const minimizeWindow = () => {
  WindowMinimise()
}

const resizeWindow = () => {
  isMaximized.value = !isMaximized.value;
  if (isMaximized.value) {
    WindowMaximise();
    MaxMinIcon.value = ContentCopyFilled;
  } else {
    WindowUnmaximise();
    MaxMinIcon.value = CropSquareFilled;
  }
  console.log(isMaximized.value)

}

const closeWindow = () => {
  Quit()
}

// 监听语言变化，重新设置 subtitle
watch(locale, (newLocale) => {
  subtitle.value = t('header.desc') + " " + version.value.tag_name
})
</script>

<style scoped>

.close-btn:hover {
  background-color: red;
}
.right-section .n-button {
  padding: 0 8px;
}
</style>