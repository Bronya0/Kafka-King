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
  <n-config-provider
      :theme="Theme"
      :locale="naive_language"
  >
    <!--https://www.naiveui.com/zh-CN/os-theme/components/layout-->
    <n-message-provider container-style="word-break: break-all;">
      <n-notification-provider placement="bottom-right" container-style="text-align: left;">
        <n-dialog-provider>

          <n-loading-bar-provider>
            <n-layout has-sider position="absolute" style="height: 100vh;" :class="headerClass">
              <!--header-->
              <n-layout-header bordered style="height: 42px; bottom: 0; padding: 0; ">
                <Header/>
              </n-layout-header>
              <!--side + content-->
              <n-layout has-sider position="absolute" style="top: 42px; bottom: 0;">
                <n-layout-sider
                    bordered
                    collapse-mode="width"
                    :collapsed-width="60"
                    :collapsed="true"
                    style="--wails-draggable:drag"
                >
                  <Aside
                      :collapsed-width="60"
                      :value="activeItem.key"
                      :options="sideMenuOptions"
                  />

                </n-layout-sider>
                <n-layout-content style="padding: 0 16px;">
                  <keep-alive>
                    <component :is="activeItem.component"></component>
                  </keep-alive>
                </n-layout-content>
              </n-layout>
            </n-layout>
          </n-loading-bar-provider>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import {computed, onMounted, shallowRef} from 'vue'
import {
  darkTheme,
  enUS,
  jaJP,
  lightTheme,
  NConfigProvider,
  NLayout,
  NLayoutContent,
  NLayoutHeader,
  NMessageProvider,
  zhCN
} from 'naive-ui'
import {
  AddChartOutlined,
  AllOutOutlined,
  GroupsSharp,
  HiveOutlined,
  InfoOutlined,
  LibraryBooksOutlined,
  MessageOutlined,
  PermDataSettingTwotone,
  SchemaOutlined,
  SendTwotone,
  SettingsOutlined,
} from '@vicons/material'
import Header from './components/Header.vue'
import Settings from './components/Settings.vue'
import {GetConfig, SaveConfig} from "../wailsjs/go/config/AppConfig";
import {SetSchemaRegistry} from "../wailsjs/go/service/Service";
import {getLocalLanguage, renderIcon} from "./utils/common";
import Aside from "./components/Aside.vue";
import Conn from "./components/Conn.vue";
import Nodes from "./components/Nodes.vue";
import Topics from "./components/Topics.vue";
import emitter from "./utils/eventBus";
import Groups from "./components/Groups.vue";
import Producer from "./components/Producer.vue";
import Consumer from "./components/Consumer.vue";
import Monitor from "./components/Monitor.vue";
import Acl from "./components/Acl.vue";
import Sr from "./components/Sr.vue";
import About from "./components/About.vue";
import {useI18n} from 'vue-i18n'
import koKR from "./i18n/ko-KR";
import ruRU from "./i18n/ru-RU";

const {t, locale} = useI18n()

let headerClass = shallowRef('darkTheme')
let naive_language = shallowRef(zhCN)

let Theme = shallowRef(darkTheme)
let config = {}

onMounted(async () => {

  // 从后端加载配置
  config = await GetConfig()
  // 自动恢复 Schema Registry 连接（Consumer 的 avro 解码依赖它）
  if (config.schema_registry && config.schema_registry.url) {
    SetSchemaRegistry(
        config.schema_registry.url,
        config.schema_registry.user || '',
        config.schema_registry.pass || '',
        config.schema_registry.skip_tls === 'true',
    ).then(res => {
      if (res.err !== "") {
        console.warn('Schema Registry auto connect failed:', res.err)
      }
    })
  }
  // 设置主题
  themeChange(config.theme)
  // 初始化语言
  await handleLanguageChange(config.language)
  // =====================注册事件监听=====================
  // 主题切换
  emitter.on('update_theme', themeChange)
  // 菜单切换
  emitter.on('menu_select', handleMenuSelect)
  // 语言切换
  emitter.on('language_change', handleLanguageChange)

})

// 左侧菜单
const sideMenuOptions = computed(() => [
  {
    label: t('aside.cluster'),
    key: 'cluster',
    icon: renderIcon(HiveOutlined),
    component: Conn,
  },
  {
    label: t('aside.node'),
    key: 'node',
    icon: renderIcon(AllOutOutlined),
    component: Nodes,
  },

  {
    label: t('aside.topic'),
    key: 'topic',
    icon: renderIcon(LibraryBooksOutlined),
    component: Topics,
  },
  {
    label: t('aside.producer'),
    key: 'producer',
    icon: renderIcon(SendTwotone),
    component: Producer,
  },
  {
    label: t('aside.consumer'),
    key: 'consumer',
    icon: renderIcon(MessageOutlined),
    component: Consumer,
  },
  {
    label: t('aside.group'),
    key: 'group',
    icon: renderIcon(GroupsSharp),
    component: Groups,
  },
  {
    label: "Acl",
    key: 'Acl',
    icon: renderIcon(PermDataSettingTwotone),
    component: Acl,
  },
  {
    label: t('aside.sr'),
    key: 'sr',
    icon: renderIcon(SchemaOutlined),
    component: Sr,
  },
  {
    label: t('aside.monitor'),
    key: 'monitor',
    icon: renderIcon(AddChartOutlined),
    component: Monitor,
  },
  {
    label: t('aside.settings'),
    key: 'settings',
    icon: renderIcon(SettingsOutlined),
    component: Settings
  },
  {
    label: t('about.title'),
    key: "about",
    icon: renderIcon(InfoOutlined),
    component: About
  },

])

const activeItem = shallowRef(sideMenuOptions.value[0])


// 切换菜单
function handleMenuSelect(key) {
  // 根据key寻找item
  activeItem.value = sideMenuOptions.value.find(item => item.key === key)
}


// 主题切换
function themeChange(newTheme) {
  Theme.value = newTheme === lightTheme.name ? lightTheme : darkTheme
  headerClass = newTheme === lightTheme.name ? "lightTheme" : "darkTheme"
}

// naive ui language
const languageMap = {
  'zh-CN': zhCN,
  'en-US': enUS,
  'ja-JP': jaJP,
  'ko-KR': koKR,
  'ru-RU': ruRU,
}

// 语言切换
// 未配置语言时，检查本地语言，合法则使用；否则使用默认语言
async function handleLanguageChange(language) {
  console.info("language配置：" + language);

  const DEFAULT_LANGUAGE = 'en-US';
  const localLanguage = getLocalLanguage();
  const supportedLanguages = Object.keys(languageMap);

  if (language === "" || language === null || language === undefined){
    language =  supportedLanguages.includes(localLanguage) ? localLanguage : DEFAULT_LANGUAGE
    config.language = language;
    console.info("未配置语言，使用本地语言并保存配置：" + language);
    await SaveConfig(config);
  }

  console.info("selectedLanguage：" + language);
  locale.value = language;
  naive_language.value = languageMap[language];
}

</script>

<style>
body {
  margin: 0;
  font-family: sans-serif;

}

.lightTheme .n-layout-header {
  background-color: #f7f7fa;
}

.lightTheme .n-layout-sider {
  background-color: #f7f7fa !important;
}
</style>