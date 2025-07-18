<template>
    <div class="fixed inset-0 bg-black bg-opacity-50 z-40 flex justify-center items-center" @click.self="$emit('close')">
      <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h2 class="text-2xl font-bold mb-6 text-center">我的课程</h2>
        <div v-if="purchases.length === 0" class="text-gray-500 text-center">您还没有购买任何课程。</div>
        <div v-else>
          <div v-if="purchasedItems.categories.length > 0">
            <h3 class="font-semibold text-lg mb-2">已购系列:</h3>
            <ul class="list-disc list-inside bg-gray-100 p-3 rounded">
              <li v-for="cat in purchasedItems.categories" :key="cat">{{ cat }}</li>
            </ul>
          </div>
          <div v-if="purchasedItems.videos.length > 0" class="mt-4">
            <h3 class="font-semibold text-lg mb-2">已购单课:</h3>
            <ul class="list-disc list-inside bg-gray-100 p-3 rounded">
              <li v-for="vid in purchasedItems.videos" :key="vid">{{ vid }}</li>
            </ul>
          </div>
        </div>
        <button @click="$emit('close')" class="mt-6 w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">关闭</button>
      </div>
    </div>
  </template>

<script setup>
import { computed } from 'vue';

const props = defineProps(['purchases', 'categories']);
const emit = defineEmits(['close']);

const purchasedItems = computed(() => {
  const items = { videos: [], categories: [] };
  if (!props.purchases) return items;

  props.purchases.forEach(p => {
    if (p.item_type === 'category') {
      const cat = props.categories.find(c => c.id === p.item_id);
      if (cat) items.categories.push(cat.name);
    } else {
       for (const category of props.categories) {
         const vid = category.videos.find(v => v.id === p.item_id);
         if (vid) {
           items.videos.push(vid.title);
           break;
         }
       }
    }
  });
  return items;
});
</script>
