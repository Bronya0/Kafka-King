<template>
<!--  https://www.naiveui.com/zh-CN/os-theme/components/menu-->
    <n-menu
        :mode="'vertical'"
        :value="props.value"
        @update:value="handleMenuSelect"
        :options="props.options"
        style="--wails-draggable:no-drag"
    />

</template>


<script setup>

import emitter from "../utils/eventBus";

const props = defineProps(['options', 'value']);

const handleMenuSelect = (key, item) => {
  emitter.emit('menu_select', key)
}

</script>

<style>
.aside-btn .n-button .n-button__icon {
  font-size: 22px;
}
</style>