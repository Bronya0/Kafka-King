<template>
  <n-layout-footer bordered class="footer">
    <n-flex justify="center">
      <n-button text tag="a" href="https://wails.io/" target="_blank">
        Wails Docs
      </n-button>
      <n-button text tag="a" href="https://vuejs.org/" target="_blank">
        Vue Docs
      </n-button>
      <n-button text tag="a" href="https://www.naiveui.com/" target="_blank">
        Naive UI Docs
      </n-button>
      <n-button text tag="a" href="https://github.com/bronya0/yourproject" target="_blank">
        GitHub
      </n-button>
    </n-flex>
  </n-layout-footer>
</template>

<script setup>
import { NLayoutFooter, NSpace, NButton } from 'naive-ui'
</script>

<style scoped>
.footer {
  height: 268px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>