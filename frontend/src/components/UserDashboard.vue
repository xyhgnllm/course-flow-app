<template>
  <div class="fixed inset-0 bg-black bg-opacity-60 z-40 flex justify-center items-center" @click.self="$emit('close')">
    <div class="bg-gray-50 p-8 rounded-2xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto hide-scrollbar">
      <div class="flex items-center mb-8">
        <div class="w-20 h-20 bg-blue-500 rounded-full flex items-center justify-center text-white text-4xl font-bold mr-6">
          {{ user.username.charAt(0).toUpperCase() }}
        </div>
        <div>
          <h2 class="text-3xl font-bold text-gray-800">{{ user.username }}</h2>
          <p class="text-gray-500">欢迎回到您的用户中心</p>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 text-center">
        <div class="bg-white p-6 rounded-xl shadow-md">
          <p class="text-sm text-gray-500">账户余额</p>
          <p class="text-3xl font-semibold text-blue-600">¥ {{ user.balance.toFixed(2) }}</p>
        </div>
        <div class="bg-white p-6 rounded-xl shadow-md">
          <p class="text-sm text-gray-500">已购项目</p>
          <p class="text-3xl font-semibold text-blue-600">{{ purchases.length }}</p>
        </div>
        <div class="bg-white p-6 rounded-xl shadow-md">
          <p class="text-sm text-gray-500">总下载量</p>
          <p class="text-3xl font-semibold text-blue-600">{{ user.download_count }}</p>
        </div>
      </div>

      <!-- Purchases -->
      <div class="bg-white p-6 rounded-xl shadow-md mb-8">
        <h3 class="font-semibold text-xl mb-4 text-gray-700">付费记录</h3>
        <div v-if="purchases.length === 0" class="text-gray-500 text-center py-4">您还没有购买任何课程。</div>
        <div v-else class="max-h-48 overflow-y-auto hide-scrollbar pr-2">
          <ul class="space-y-2">
            <li v-for="item in purchasedItems.all" :key="item.key" class="flex justify-between items-center bg-gray-50 p-3 rounded-lg">
              <span class="font-medium text-gray-800">{{ item.name }}</span>
              <span :class="[item.type === 'category' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800', 'px-2 py-1 text-xs font-semibold rounded-full']">{{ item.type === 'category' ? '系列课程' : '单个视频' }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Change Password -->
      <div class="bg-white p-6 rounded-xl shadow-md">
        <h3 class="font-semibold text-xl mb-4 text-gray-700">账户安全</h3>
        <div v-if="!showChangePasswordForm">
          <button @click="showChangePasswordForm = true" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition-colors">
            修改密码
          </button>
        </div>
        <form v-else @submit.prevent="changePassword">
          <div class="space-y-4">
            <input v-model="currentPassword" type="password" placeholder="当前密码" class="shadow-sm appearance-none border rounded-lg w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500">
            <input v-model="newPassword" type="password" placeholder="新密码 (至少6位)" class="shadow-sm appearance-none border rounded-lg w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500">
            <input v-model="confirmPassword" type="password" placeholder="确认新密码" class="shadow-sm appearance-none border rounded-lg w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500">
          </div>
          <p v-if="passwordMessage" :class="[isPasswordError ? 'text-red-500' : 'text-green-500', 'text-sm mt-3']">{{ passwordMessage }}</p>
          <div class="flex items-center mt-4 space-x-4">
            <button type="submit" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg transition-colors">
              确认修改
            </button>
            <button @click="showChangePasswordForm = false" type="button" class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded-lg transition-colors">
              取消
            </button>
          </div>
        </form>
      </div>

      <button @click="$emit('close')" class="mt-8 w-full bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-4 rounded-lg transition-colors">关闭</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({ user: Object, categories: Array });
const emit = defineEmits(['close', 'password-changed']);

const purchases = ref([]);
const showChangePasswordForm = ref(false);
const currentPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const passwordMessage = ref(null);
const isPasswordError = ref(false);

const fetchPurchases = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/users/me');
    purchases.value = response.data.purchases || [];
  } catch (error) {
    console.error("Failed to fetch user purchase data:", error);
  }
};

const purchasedItems = computed(() => {
  const items = { all: [] };
  if (!purchases.value) return items;

  purchases.value.forEach(p => {
    if (p.item_type === 'category') {
      const cat = props.categories.find(c => c.id === p.item_id);
      if (cat) items.all.push({ key: `cat-${cat.id}`, name: cat.name, type: 'category' });
    } else {
       for (const category of props.categories) {
         const vid = category.videos.find(v => v.id === p.item_id);
         if (vid) {
           items.all.push({ key: `vid-${vid.id}`, name: vid.title, type: 'video' });
           break;
         }
       }
    }
  });
  return items;
});

const changePassword = async () => {
  passwordMessage.value = null;
  isPasswordError.value = false;

  if (newPassword.value !== confirmPassword.value) {
    passwordMessage.value = '两次输入的新密码不一致。';
    isPasswordError.value = true;
    return;
  }
  if (newPassword.value.length < 6) {
    passwordMessage.value = '新密码长度不能少于6位。';
    isPasswordError.value = true;
    return;
  }

  try {
    await axios.post('http://localhost:8000/api/users/change-password', {
      current_password: currentPassword.value,
      new_password: newPassword.value
    });
    passwordMessage.value = '密码修改成功！';
    isPasswordError.value = false;
    currentPassword.value = '';
    newPassword.value = '';
    confirmPassword.value = '';
    setTimeout(() => { showChangePasswordForm.value = false; passwordMessage.value = null; }, 2000);
    emit('password-changed');
  } catch (error) {
    passwordMessage.value = error.response?.data?.detail || '密码修改失败，请重试。';
    isPasswordError.value = true;
  }
};

onMounted(() => {
  if (props.user) {
    fetchPurchases();
  }
});

</script>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
    display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>

