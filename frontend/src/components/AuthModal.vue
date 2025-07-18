<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 z-40 flex justify-center items-center" @click.self="$emit('close')">
    <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
      <h2 class="text-2xl font-bold mb-6 text-center">{{ isLogin ? '登录' : '注册' }}</h2>
      
      <form @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="username">用户名</label>
          <input v-model="username" id="username" type="text" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required>
        </div>
        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="password">密码</label>
          <input v-model="password" id="password" type="password" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline" required>
        </div>
        
        <p v-if="error" class="text-red-500 text-xs italic mb-4">{{ error }}</p>

        <div class="flex items-center justify-between">
          <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
            {{ isLogin ? '登录' : '注册' }}
          </button>
          <a @click.prevent="isLogin = !isLogin" class="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800" href="#">
            {{ isLogin ? '还没有账户？去注册' : '已有账户？去登录' }}
          </a>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const emit = defineEmits(['close', 'authenticated']);

const isLogin = ref(true);
const username = ref('');
const password = ref('');
const error = ref(null);

const handleSubmit = async () => {
  error.value = null;
  const url = isLogin.value ? 'http://localhost:8000/api/login' : 'http://localhost:8000/api/register';
  
  try {
    const response = await axios.post(url, {
      username: username.value,
      password: password.value
    });

    if (response.data.access_token) {
      emit('authenticated', response.data.access_token);
    } else {
      // This case might not happen if backend is consistent, but as a fallback.
      error.value = `An unexpected error occurred.`;
    }

  } catch (err) {
    error.value = err.response?.data?.detail || '操作失败，请检查您的输入或稍后再试。';
  }
};
</script>
