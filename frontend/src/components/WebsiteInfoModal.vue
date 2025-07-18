<template>
    <div class="fixed inset-0 bg-black bg-opacity-50 z-40 flex justify-center items-center" @click.self="$emit('close')">
      <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4 text-center">网址发布页</h2>
        <p class="text-gray-700 mb-4">这里是我们的官方网址发布页面，请收藏以获取最新地址。</p>
        <p class="text-gray-700 font-semibold">当前网址: <a href="#" class="text-blue-500 hover:underline">http://your-current-website.com</a></p>
        <button @click="$emit('close')" class="mt-6 w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">关闭</button>
      </div>
    </div>
  </template>

<script setup>
defineEmits(['close']);
</script>