<template>
  <n-page-header :subtitle="subtitle" style="padding: 4px;--wails-draggable:drag">
    <template #avatar>
      <n-avatar :src="logo"/>
    </template>
    <template #title>
      <div style="font-weight: 800">{{app_name}}</div>
    </template>
    <template #extra>
      <n-flex justify="flex-end" style="--wails-draggable:no-drag" class="right-section">
        <n-button quaternary :focusable="false" @click="changeTheme" :render-icon="renderIcon(MoonOrSunnyOutline)"/>
        <n-button quaternary @click="openUrl(update_url)"
                  :render-icon="renderIcon(CodeFilled)"/>
        <n-tooltip placement="bottom" trigger="hover">
          <template #trigger>
            <n-button quaternary :focusable="false" :loading="update_loading" @click="checkForUpdates"
                      :render-icon="renderIcon(SystemUpdateAltSharp)"/>
          </template>
          <span> 检查版本：{{ version.tag_name }} {{ check_msg }}</span>
        </n-tooltip>
        <n-button quaternary :focusable="false" @click="minimizeWindow" :render-icon="renderIcon(RemoveOutlined)"/>
        <n-button quaternary :focusable="false" @click="resizeWindow" :render-icon="renderIcon(MaxMinIcon)"/>
        <n-button quaternary style="font-size: 22px" :focusable="false" @click="closeWindow">
          <n-icon>
            <CloseFilled/>
          </n-icon>
        </n-button>
      </n-flex>
    </template>
  </n-page-header>
</template>

<script setup>
import {darkTheme, lightTheme, NAvatar, NButton,  NFlex, useMessage} from 'naive-ui'
import {
  CodeFilled,
  SystemUpdateAltSharp,
  RemoveOutlined,
  CloseFilled,
  CropSquareFilled,
  WbSunnyOutlined,
  NightlightRoundFilled, ContentCopyFilled
} from '@vicons/material'
import logo from '../assets/images/logo.svg'
import {h, onMounted, ref, shallowRef} from "vue";
import {BrowserOpenURL, Quit, WindowMaximise, WindowMinimise, WindowUnmaximise} from "../../wailsjs/runtime";
import {CheckUpdate} from '../../wailsjs/go/system/Update'
import {useNotification} from 'naive-ui'
import {openUrl, renderIcon} from "../utils/common";
import {GetConfig, GetVersion, GetAppName} from "../../wailsjs/go/config/AppConfig";
import emitter from "../utils/eventBus";

defineProps(['options', 'value']);

const MoonOrSunnyOutline = shallowRef(WbSunnyOutlined)
const isMaximized = ref(false);
const check_msg = ref("");
const app_name = ref("");
const MaxMinIcon = shallowRef(CropSquareFilled)
const update_url = "https://github.com/Bronya0/wails-template/releases"
const update_loading = ref(false)
let theme = lightTheme

let version = ref({
  tag_name: "",
  body: "",
})

const desc = "让音频更懂视觉 "
const subtitle = ref("")

const notification = useNotification()
const message = useMessage()

const checkForUpdates = async () => {
  update_loading.value = true
  try {
    const v = await GetVersion()
    const resp = await CheckUpdate()
    if (!resp) {
      check_msg.value = "无法连接github，请检查网络"
    } else if (resp.tag_name !== v) {
      check_msg.value = '发现新版本 ' + resp.tag_name
      version.value.body = resp.body
      const n = notification.success({
        title: '发现新版本 ' + resp.tag_name,
        description: resp.body,
        action: () =>
              h(NFlex, {justify: "flex-end" }, () => [
                h(
                    NButton,
                    {
                      type: 'primary',
                      secondary: true,
                      onClick: () => BrowserOpenURL(update_url),
                    },
                    () => "立即下载",
                ),
                h(
                    NButton,
                    {
                      secondary: true,
                      onClick: () => {
                        n.destroy()
                      },
                    },
                    () => "取消",
                ),
            ]),
        onPositiveClick: () => BrowserOpenURL(update_url),
      })
    }
  } finally {
    update_loading.value = false
  }
}

onMounted(async () => {
  app_name.value = await GetAppName()

  const config = await GetConfig()
  MoonOrSunnyOutline.value = config.theme === lightTheme.name ? WbSunnyOutlined : NightlightRoundFilled
  const v = await GetVersion()
  version.value.tag_name = v
  subtitle.value = desc + v
  await checkForUpdates()
})


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
const changeTheme = () => {
  MoonOrSunnyOutline.value = MoonOrSunnyOutline.value === NightlightRoundFilled ? WbSunnyOutlined : NightlightRoundFilled;
  theme = MoonOrSunnyOutline.value === NightlightRoundFilled ? darkTheme : lightTheme
  emitter.emit('update_theme', theme)
}
</script>

<style scoped>


.right-section .n-button {
  padding: 0 8px;
}
</style>