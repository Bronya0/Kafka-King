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
      <h2>{{ t('inspection.title') }}</h2>
      <p>{{ t('inspection.desc') }}</p>
      <n-input v-model:value="schemeName" :placeholder="t('inspection.schemeNamePlaceholder')"
        style="width: 200px; margin-right: 10px;" />
      <n-button @click="saveScheme">
        {{ t('inspection.saveScheme') }}
      </n-button>
      <n-select v-model:value="selectedScheme" :options="savedSchemes"
        :placeholder="t('inspection.loadSchemePlaceholder')" clearable label-field="name" value-field="id"
        style="width: 200px; margin-left: 10px;" @update:value="loadScheme" />
      <!-- 新增删除按钮 -->
      <n-button @click="confirmDeleteScheme" :disabled="!selectedScheme" type="error" secondary
        style="margin-left: 10px;">
        {{ t('inspection.deleteScheme') }}
      </n-button>
      <!-- 新增告警配置按钮 -->
      <n-button @click="showAlertConfig = true" type="info" secondary style="margin-left: 10px;">
        {{ t('inspection.alertConfig') }}
      </n-button>
    </n-flex>
    <n-flex align="center">
      {{ t('inspection.topicsLabel') }}:
      <n-select v-model:value="selectedTopics" @update:value="clear_offset" :options="topic_data"
        :placeholder="t('inspection.topicPlaceholder')" filterable clearable multiple style="width: 600px" />
      {{ t('inspection.groupLabel') }}：
      <n-select v-model:value="selectedGroup" @update:value="clear_offset" :options="group_data"
        :placeholder="t('inspection.groupPlaceholder')" filterable clearable tag style="width: 300px" />

      <n-input-number v-model:value="refreshInterval" :min="1" @update:value="setFetchInterval"
        style="width: 100px; margin-right: 10px;" />
      <n-button @click="toggleInspection" :loading="loading" :render-icon="renderIcon(MessageOutlined)">
        {{ isInspecting ? t('inspection.stopInspection') : t('inspection.startInspection') }}
      </n-button>
      {{ t('inspection.autoFetch', { interval: refreshInterval }) }}
    </n-flex>

    <!-- 告警配置对话框 -->
    <n-modal v-model:show="showAlertConfig" preset="dialog" :title="t('inspection.alertConfig')" style="width: 600px">
      <n-form label-placement="left" label-width="120px">
        <n-form-item :label="t('inspection.enableAlert')">
          <n-switch v-model:value="alertConfig.enabled" />
        </n-form-item>
        <n-form-item :label="t('inspection.webhookUrl')">
          <n-input v-model:value="alertConfig.webhook_url" :placeholder="t('inspection.webhookUrlPlaceholder')" />
        </n-form-item>
        <n-form-item :label="t('inspection.customHeader')">
          <n-input v-model:value="alertConfig.custom_header" :placeholder="t('inspection.customHeaderPlaceholder')" />
        </n-form-item>
        <n-form-item :label="t('inspection.threshold')">
          <n-input-number v-model:value="alertConfig.threshold" :min="1"
            :placeholder="t('inspection.thresholdPlaceholder')" />
        </n-form-item>
        <n-form-item :label="t('inspection.messageTemplate')">
          <n-flex vertical>
            {{ t('inspection.messageTemplatePlaceholder') }}
            <n-input v-model:value="alertConfig.message_template" type="textarea" rows="8" placeholder='{
  "msgtype": "text",
  "text": {
    "content": "kafka积压告警\ntopics: [topics]\ngroup:[group]\nlag:[total_lag]\ntimestamp:[timestamp]"
  }
}' style="text-align: left;" />
          </n-flex>
        </n-form-item>
        <n-form-item>
          <!-- save -->
          <n-button type="primary" @click="saveAlertConfig">{{ t('common.save') }}</n-button>
        </n-form-item>
      </n-form>
    </n-modal>

    <n-flex vertical>
      <n-flex align="center">
        <div ref="lag_chartRef" style="width: 48%; height: 440px"></div>
        <div ref="commit_chartRef" style="width: 48%; height: 440px"></div>
      </n-flex>
      <n-flex align="center">
        <div ref="end_chartRef" style="width: 48%; height: 440px"></div>
        <div ref="productionSpeed_chartRef" style="width: 48%; height: 440px"></div>
      </n-flex>
      <n-flex align="center">
        <div ref="consumptionSpeed_chartRef" style="width: 48%; height: 440px"></div>
      </n-flex>
    </n-flex>
  </n-flex>
</template>

<script setup>
import { onMounted, ref, shallowRef } from 'vue';
import * as echarts from 'echarts/core';
import { GridComponent, LegendComponent, TitleComponent, ToolboxComponent, TooltipComponent } from 'echarts/components';
import { LineChart } from 'echarts/charts';
import { UniversalTransition } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';
import { lightTheme, NButton, NFlex, useDialog, useMessage } from 'naive-ui';
import { GetGroups, GetTopicOffsets, GetTopics } from '../../wailsjs/go/service/Service';
import emitter from '../utils/eventBus';
import { renderIcon } from '../utils/common';
import { MessageOutlined } from '@vicons/material';
import { useI18n } from 'vue-i18n';
import { GetConfig } from '../../wailsjs/go/config/AppConfig';
import { CheckAndSendAlert } from '../../wailsjs/go/service/Service';

const { t } = useI18n();
const message = useMessage();
const topic_data = ref([]);
const group_data = ref([]);
const selectedTopics = ref([]);
const selectedGroup = ref(null);
const monitorSchemesKey = 'kafkaKingMonitorSchemes';

const schemeName = ref('');
const savedSchemes = ref([]);
const selectedScheme = ref(null);
const dialog = useDialog();

const lag_chartRef = shallowRef(null);
const commit_chartRef = shallowRef(null);
const end_chartRef = shallowRef(null);
const productionSpeed_chartRef = shallowRef(null);
const consumptionSpeed_chartRef = shallowRef(null);

const lag_chart = shallowRef(null);
const commit_chart = shallowRef(null);
const end_chart = shallowRef(null);
const productionSpeed_chart = shallowRef(null);
const consumptionSpeed_chart = shallowRef(null);

const offsetData = ref({
  lag: {},
  commit: {},
  end: {},
  productionSpeed: {},
  consumptionSpeed: {},
});
const loading = ref(false);

let echarts_theme = 'dark';

const refreshInterval = ref(5);
let intervalId = null;
const isInspecting = ref(false);

// 告警配置
const showAlertConfig = ref(false);
const alertConfig = ref({
  enabled: false,
  webhook_url: '',
  custom_header: '',
  threshold: 1000,
  message_template: '',
  check_interval: 5
});

onMounted(async () => {
  emitter.on('selectNode', selectNode);
  emitter.on('refreshTopic', refreshTopic);

  const loadedConfig = await GetConfig();
  echarts_theme = loadedConfig.theme === lightTheme.name ? 'light' : 'dark';

  // 加载告警配置
  const savedAlertConfig = localStorage.getItem('kafkaKingAlertConfig');
  if (savedAlertConfig) {
    alertConfig.value = JSON.parse(savedAlertConfig);
  }

  await getData();
  initChart();

  const storedSchemes = localStorage.getItem(monitorSchemesKey);
  if (storedSchemes) {
    savedSchemes.value = JSON.parse(storedSchemes);
  }

  window.addEventListener('resize', handleResize);

});

// 在 script setup 中添加方法
const saveScheme = () => {
  if (!schemeName.value) {
    message.warning(t('message.schemeNameRequired'));
    return;
  }

  // 生成唯一ID
  const newScheme = {
    id: Date.now().toString(),
    name: schemeName.value,
    topics: [...selectedTopics.value],
    group: selectedGroup.value
  };

  // 检查是否已存在同名方案
  const existingIndex = savedSchemes.value.findIndex(s => s.name === schemeName.value);
  if (existingIndex !== -1) {
    savedSchemes.value[existingIndex] = newScheme;
  } else {
    savedSchemes.value.push(newScheme);
  }

  // 保存到 localStorage
  localStorage.setItem(monitorSchemesKey, JSON.stringify(savedSchemes.value));
  message.success(t('message.schemeSaved'));
  schemeName.value = '';
};

const loadScheme = (schemeId) => {
  const scheme = savedSchemes.value.find(s => s.id === schemeId);
  if (scheme) {
    // 停止当前监控
    if (isInspecting.value) stopInspection();

    // 加载方案数据
    selectedTopics.value = [...scheme.topics];
    selectedGroup.value = scheme.group;

    // 清空图表数据
    clear_offset();
    message.success(t('message.schemeLoaded', { name: scheme.name }));
  }
};
// 添加删除方法
const confirmDeleteScheme = () => {
  if (!selectedScheme.value) return;

  const scheme = savedSchemes.value.find(s => s.id === selectedScheme.value);
  if (!scheme) return;

  dialog.warning({
    title: t('inspection.deleteSchemeConfirm'),
    content: t('inspection.deleteSchemeConfirmContent', { name: scheme.name }),
    positiveText: t('common.enter'),
    negativeText: t('common.cancel'),
    onPositiveClick: () => {
      deleteScheme(scheme.id);
    }
  });
};

const deleteScheme = (schemeId) => {
  // 从列表中删除
  const index = savedSchemes.value.findIndex(s => s.id === schemeId);
  if (index !== -1) {
    savedSchemes.value.splice(index, 1);

    // 如果删除的是当前选中的方案，清空选择
    if (selectedScheme.value === schemeId) {
      selectedScheme.value = null;
    }

    // 更新本地存储
    localStorage.setItem(monitorSchemesKey, JSON.stringify(savedSchemes.value));
    message.success(t('message.schemeDeleted'));
  }
};

const getIntervalInMilliseconds = () => {
  return refreshInterval.value * 60 * 1000;
};
const setFetchInterval = () => {
  if (intervalId) {
    clearInterval(intervalId);
  }
  intervalId = setInterval(fetchData, getIntervalInMilliseconds());
};

const toggleInspection = () => {
  if (isInspecting.value) {
    stopInspection();
  } else {
    startInspection();
  }
};


const startInspection = async () => {
  if (selectedTopics.value.length === 0 || !selectedGroup.value) {
    message.warning(t('message.selectTopicGroup'));
    return;
  }
  isInspecting.value = true;
  fetchData();
  setFetchInterval();
};

const stopInspection = () => {
  isInspecting.value = false;
  clearInterval(intervalId);
};


const refreshTopic = async () => {
  await getData();
};

const handleResize = () => {
  [lag_chart, commit_chart, end_chart, productionSpeed_chart, consumptionSpeed_chart].forEach(chart => {
    if (chart.value) chart.value.resize();
  });
};

const initChart = () => {
  echarts.use([
    TitleComponent,
    TooltipComponent,
    GridComponent,
    LegendComponent,
    LineChart,
    CanvasRenderer,
    UniversalTransition,
    ToolboxComponent,
  ]);

  const option = {
    backgroundColor: 'transparent',
    title: { text: '', top: '0%', left: 'center', padding: 20 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', boundaryGap: false, splitLine: { show: true }, data: [] },
    yAxis: { type: 'value' },
    legend: { data: [], top: '5%', height: '20%' },
    series: [],
    grid: { top: '25%', },
  };

  lag_chart.value = echarts.init(lag_chartRef.value, echarts_theme);
  lag_chart.value.setOption({ ...option, title: { text: t('inspection.lag') } });

  commit_chart.value = echarts.init(commit_chartRef.value, echarts_theme);
  commit_chart.value.setOption({ ...option, title: { text: t('inspection.commit') } });

  end_chart.value = echarts.init(end_chartRef.value, echarts_theme);
  end_chart.value.setOption({ ...option, title: { text: t('inspection.end') } });

  productionSpeed_chart.value = echarts.init(productionSpeed_chartRef.value, echarts_theme);
  productionSpeed_chart.value.setOption({ ...option, title: { text: 'ProduceSpeed(msg/s)' } });

  consumptionSpeed_chart.value = echarts.init(consumptionSpeed_chartRef.value, echarts_theme);
  consumptionSpeed_chart.value.setOption({ ...option, title: { text: 'ConsumeSpeed(msg/s)' } });
};

const clear_offset = () => {
  offsetData.value = { lag: {}, commit: {}, end: {}, productionSpeed: {}, consumptionSpeed: {} };
};

const updateChart = () => {
  const chart_map = {
    lag: lag_chart.value,
    commit: commit_chart.value,
    end: end_chart.value,
    productionSpeed: productionSpeed_chart.value,
    consumptionSpeed: consumptionSpeed_chart.value,
  };

  for (const k in offsetData.value) {
    let series = [];
    let legendData = [];
    let xs = [];

    Object.entries(offsetData.value[k]).forEach(([topic, data]) => {
      legendData.push(topic);
      series.push({
        name: topic,
        type: 'line',
        symbol: 'circle',
        data: data.map(item => (k === 'productionSpeed' || k === 'consumptionSpeed' ? item.speed : item.offset)),
      });
      xs = data.map(item => {
        const date = new Date(item.time);
        return `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
      });
    });

    chart_map[k].setOption({
      xAxis: { data: xs },
      legend: { data: legendData },
      series,
    });
  }
};

const fetchData = async () => {
  if (selectedTopics.value.length === 0 || !selectedGroup.value) {
    message.warning(t('message.selectTopicGroup'));
    return;
  }
  loading.value = true;

  try {
    const res = await GetTopicOffsets(selectedTopics.value, selectedGroup.value);
    if (res.err !== '') {
      message.error(res.err, { duration: 5000 });
    } else {
      const now = new Date();
      const time = now.getTime(); // Use timestamp for precise time difference

      // 计算总积压
      let totalLag = 0;

      selectedTopics.value.forEach(topic => {
        const endOffset = addOffsets(res.result.end_map[topic]) || 0;
        const commitOffset = addOffsets(res.result.commit_map[topic]) || 0;
        const lag = endOffset - commitOffset;
        totalLag += lag;

        // Lag
        if (!offsetData.value.lag[topic]) offsetData.value.lag[topic] = [];
        offsetData.value.lag[topic].push({ time, offset: lag });

        // Commit
        if (!offsetData.value.commit[topic]) offsetData.value.commit[topic] = [];
        offsetData.value.commit[topic].push({ time, offset: commitOffset });

        // End
        if (!offsetData.value.end[topic]) offsetData.value.end[topic] = [];
        offsetData.value.end[topic].push({ time, offset: endOffset });

        // Production Speed
        if (!offsetData.value.productionSpeed[topic]) offsetData.value.productionSpeed[topic] = [];
        if (offsetData.value.end[topic].length >= 2) {
          const lastEnd = offsetData.value.end[topic][offsetData.value.end[topic].length - 2];
          const deltaEnd = endOffset - lastEnd.offset;
          const deltaTime = (time - lastEnd.time) / 1000; // Convert to seconds
          const speed = deltaTime > 0 ? deltaEnd / deltaTime : 0;
          offsetData.value.productionSpeed[topic].push({ time, speed });
        }

        // Consumption Speed
        if (!offsetData.value.consumptionSpeed[topic]) offsetData.value.consumptionSpeed[topic] = [];
        if (offsetData.value.commit[topic].length >= 2) {
          const lastCommit = offsetData.value.commit[topic][offsetData.value.commit[topic].length - 2];
          const deltaCommit = commitOffset - lastCommit.offset;
          const deltaTime = (time - lastCommit.time) / 1000; // Convert to seconds
          const speed = deltaTime > 0 ? deltaCommit / deltaTime : 0;
          offsetData.value.consumptionSpeed[topic].push({ time, speed });
        }

        // Keep only the last 100 data points
        for (const key of ['lag', 'commit', 'end', 'productionSpeed', 'consumptionSpeed']) {
          if (offsetData.value[key][topic]?.length > 100) offsetData.value[key][topic].shift();
        }
      });

      updateChart();

      // 检查是否需要发送告警
      if (alertConfig.value.enabled && totalLag >= alertConfig.value.threshold) {
        await checkAndSendAlert(totalLag, res);
      }
    }
  } catch (e) {
    message.error(e.message, { duration: 5000 });
  } finally {
    loading.value = false;
  }
};

const getData = async () => {
  console.log('Initializing consumer data');
  try {
    const [res, res2] = await Promise.all([GetTopics(), GetGroups()]);
    if (res.err !== '' || res2.err !== '') {
      message.error(res.err || res2.err, { duration: 5000 });
    } else {
      topic_data.value = res.results
        ?.sort((a, b) => (a.topic > b.topic ? 1 : -1))
        .map(r => ({ label: r.topic, value: r.topic })) || [];

      group_data.value = res2.results
        ?.map(g => ({
          label: g.Group,
          value: g.Group,
          State: g.State,
          ProtocolType: g.ProtocolType,
          Coordinator: g.Coordinator,
        }))
        .sort((a, b) => (a.label > b.label ? 1 : -1)) || [];
    }
  } catch (e) {
    message.error(e.message, { duration: 5000 });
  }
};

const addOffsets = (item) => {
  return Object.values(item || {}).reduce((sum, { At }) => sum + (At > 0 ? At : 0), 0);
};

// 保存告警配置
const saveAlertConfig = () => {

  if (alertConfig.value.enabled) {
    if (!alertConfig.value.webhook_url) {
      message.error('告警Webhook URL不能为空', { duration: 5000 });
      return;
    }
    if (!alertConfig.value.message_template) {
      message.error('告警消息模板不能为空', { duration: 5000 });
      return;
    }
    // 保存告警配置到localStorage
    // alertConfig.message_template 必须为json
    try {
      JSON.parse(alertConfig.value.message_template);
    } catch (e) {
      message.error('告警消息模板必须为json格式', { duration: 5000 });
      return;
    }
  }

  localStorage.setItem('kafkaKingAlertConfig', JSON.stringify(alertConfig.value));
  message.success(t('message.saveSuccess'));
  showAlertConfig.value = false;
};

// 检查并发送告警
const checkAndSendAlert = async (totalLag, res) => {
  if (!alertConfig.value.enabled) return;

  try {
    const alertData = {
      consumer_group: selectedGroup.value || '',
      total_lag: totalLag,
      threshold: alertConfig.value.threshold,
      topic_lags: selectedTopics.value.map(topic => {
        const endOffset = addOffsets(res?.result?.end_map?.[topic]) || 0;
        const commitOffset = addOffsets(res?.result?.commit_map?.[topic]) || 0;
        return { topic_name: topic, lag: endOffset - commitOffset };
      }),
      timestamp: new Date().toLocaleString()
    };
    console.log('发送告警数据:', alertData);
    console.log('告警配置:', alertConfig.value);
    const result = await CheckAndSendAlert(alertData, alertConfig.value);
    console.log('发送告警结果:', result);
    if (result.err) {
      console.error('发送告警失败:', result.err);
    } else {
      message.success(t('message.alertSent'));
    }
  } catch (error) {
    console.error('发送告警失败:', error);
    message.error(t('message.alertSendFailed'));
  }
};

const selectNode = async () => {
  topic_data.value = [];
  group_data.value = [];
  selectedTopics.value = [];
  selectedGroup.value = null;
  offsetData.value = { lag: {}, commit: {}, end: {}, productionSpeed: {}, consumptionSpeed: {} };
  loading.value = false;
  await getData();
};
</script>

<style scoped></style>
