<template>
  <n-flex vertical>
    <h2 style="width: 42px;">hello</h2>
  </n-flex>
  <main>
    <div class="result">{{ data.resultText }}</div>
    <div class="input-box">
      <n-input v-model:value="data.name" type="text" placeholder="input name" class="input"/>
      <n-button type="info" @click="greet"> Greet </n-button>
<!--      <n-button type="info" @click="emitter.emit('selectTab', data.name)"> Select </n-button>-->
    </div>
  </main>
</template>


<script setup>
import {onMounted, reactive} from 'vue'
import {Greet} from '../../wailsjs/go/main/App'
import { useMessage } from 'naive-ui'
import emitter from "../utils/eventBus";

const message = useMessage()

const data = reactive({
  name: "",
  resultText: "Please enter your name below 👇",
})

function greet() {
  Greet(data.name).then(result => {
    data.resultText = result
    message.info(result)
  })
}


onMounted(() => {
  console.info("初始化HelloWorld……")
})


</script>


<style scoped>
.result {
  height: 20px;
  line-height: 20px;
  margin: 1.5rem auto;
}
.input-box {
  text-align: center;
}
.input {
  width: 200px;
  margin-right: 10px;
}
</style>
