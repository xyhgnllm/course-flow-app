<template>
    <div class="fixed inset-0 bg-black bg-opacity-60 z-40 flex justify-center items-center" @click.self="$emit('close')">
      <div class="bg-black p-4 rounded-lg shadow-xl w-full max-w-3xl">
        <video :src="video.preview_url" controls autoplay class="w-full"></video>
        <p class="text-white text-center mt-2">{{ video.title }}</p>
      </div>
    </div>
  </template>

<script setup>
defineProps({
  video: Object,
});
defineEmits(['close']);
</script>
