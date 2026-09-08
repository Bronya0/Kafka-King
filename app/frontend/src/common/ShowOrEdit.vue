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
  <div @dblclick="handleDblClick" style="min-height: 22px">
    <n-input
        v-if="isEdit"
        ref="inputRef"
        v-model:value="inputValue"
        @keydown.enter="handleSubmit"
        @blur="handleBlur"
    />
    <template v-else>
      {{ value }}
    </template>
  </div>
</template>

<script setup>
import {nextTick, ref} from 'vue'

const props = defineProps({
  value: {
    type: [String, Number, null],
    required: true
  },
  onUpdateValue: {
    type: [Function, Array],
    required: true
  }
})

const isEdit = ref(false)
const inputRef = ref(null)
const inputValue = ref(props.value)

// 双击触发编辑
function handleDblClick() {
  // 每次进入编辑都重置为当前值，避免残留上一次编辑的内容
  inputValue.value = props.value
  isEdit.value = true
  nextTick(() => {
    inputRef.value?.focus()
  })
}

// 按回车提交
function handleSubmit() {
  props.onUpdateValue(inputValue.value)
  isEdit.value = false
}

// 失去焦点时取消编辑,恢复原值
function handleBlur() {
  isEdit.value = false
  inputValue.value = props.value
}
</script>