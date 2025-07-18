<template>
  <div id="app" class="bg-gray-100 font-sans flex flex-col h-screen">
    <!-- Header -->
    <header class="bg-white shadow-md z-20">
      <nav class="container mx-auto px-6 py-3 flex justify-between items-center">
        <!-- Left: User Info -->
        <div class="flex items-center justify-start w-1/4">
          <div v-if="user" class="relative">
            <div @click="showUserMenu = !showUserMenu" class="cursor-pointer flex items-center">
              <span class="font-semibold text-gray-700">{{ user.username }}</span>
              <svg class="h-5 w-5 ml-1 text-gray-600" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" stroke="currentColor"><path d="M19 9l-7 7-7-7"></path></svg>
            </div>
            <div v-if="showUserMenu" class="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-xl z-30">
              <a @click="showUserDashboard = true; showUserMenu = false" class="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-500 hover:text-white cursor-pointer">用户中心</a>
              <a @click="logout" class="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-500 hover:text-white cursor-pointer">退出登录</a>
            </div>
          </div>
        </div>

        <!-- Center: Categories -->
        <div class="flex-grow flex justify-center">
          <div class="hidden sm:block w-full">
            <nav class="flex justify-center space-x-4" aria-label="Tabs">
              <a v-for="category in categories" :key="category.id" @click="activeCategoryId = category.id"
                 :class="[category.id === activeCategoryId ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600 hover:bg-blue-100', 'cursor-pointer whitespace-nowrap py-2 px-4 rounded-md font-medium text-sm shadow-sm transition-colors duration-200']">
                {{ category.name }}
              </a>
            </nav>
          </div>
        </div>

        <!-- Right: Login/Register -->
        <div class="flex items-center justify-end w-1/4">
          <div v-if="!user" @click="showAuthModal = true" class="cursor-pointer px-4 py-2 text-gray-700 hover:text-blue-500 font-semibold">
            登录 / 注册
          </div>
        </div>
      </nav>
      <div class="container mx-auto px-6 py-3 flex justify-center">
        <input type="text" v-model="searchQuery" placeholder="搜索视频标题或标签..." class="w-1/2 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
      </div>
    </header>

    <!-- Scrollable Content Wrapper -->
    <div class="flex-grow overflow-y-auto hide-scrollbar">
      <main class="container mx-auto px-6 py-8">
        <!-- Category Purchase Button -->
        <div v-if="activeCategory" class="bg-blue-100 border-l-4 border-blue-500 text-blue-700 p-4 rounded-md mb-8 flex justify-between items-center">
          <div>
            <h2 class="font-bold text-lg">{{ activeCategory.name }}</h2>
            <p class="text-sm">打包购买此系列下的所有课程，享受优惠！</p>
          </div>
          <button v-if="!isCategoryPurchased(activeCategory.id)" @click="initiatePurchase('category', activeCategory.id, activeCategory.price)" class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 transition duration-300">
            打包购买 (¥ {{ activeCategory.price }})
          </button>
          <span v-else class="font-bold text-green-600">✓ 已拥有</span>
        </div>

        <!-- Video Grid -->
        <div v-if="filteredVideos.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <div v-for="video in filteredVideos" :key="video.id" class="bg-white rounded-lg shadow-lg overflow-hidden transform hover:-translate-y-1 transition-transform duration-300">
            <img class="h-48 w-full object-cover" :src="`https://picsum.photos/seed/${video.id}/400/300`" :alt="video.title">
            <div class="p-4">
              <h3 class="font-bold text-lg mb-2 text-gray-800">{{ video.title }}</h3>
              <div class="flex justify-between items-center mt-4">
                <button @click="playPreview(video)" class="text-sm font-semibold text-blue-600 hover:text-blue-800">试看</button>
                <button v-if="hasAccess(video.id)" @click="downloadVideo(video.id, video.title)" class="bg-gray-700 text-white text-sm font-bold py-1 px-3 rounded hover:bg-gray-900 transition duration-300">
                  下载
                </button>
                <button v-else @click="initiatePurchase('video', video.id, video.price)" class="bg-green-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-green-700 transition duration-300">
                  购买 ￥{{ video.price }}
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center text-gray-500 text-lg mt-12">
          没有找到匹配的视频。
        </div>
      </main>
    </div>

    <!-- Footer (Sticky) -->
    <footer class="bg-gray-800 text-white py-4">
      <div class="container mx-auto px-6 flex flex-col justify-center items-center text-center space-y-2 text-sm">
        <p>联系方式: @xxx.mail.com</p>
        <a @click="showWebsiteInfo = true" class="text-blue-400 hover:underline cursor-pointer">网址发布页</a>
      </div>
    </footer>

    <!-- Modals -->
    <AuthModal v-if="showAuthModal" @close="showAuthModal = false" @authenticated="onAuthenticated" />
    <PreviewModal v-if="showPreviewModal" :video="previewVideo" @close="showPreviewModal = false" />
    <PaymentModal 
      v-if="showPaymentModal" 
      :amount="paymentDetails.amount" 
      @close="showPaymentModal = false" 
      @payment-successful="handleSuccessfulPayment" 
    />
    <UserDashboard v-if="showUserDashboard" :user="user" @close="showUserDashboard = false" @password-changed="fetchUser" />

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

import AuthModal from './components/AuthModal.vue';
import PreviewModal from './components/PreviewModal.vue';
import PaymentModal from './components/PaymentModal.vue';
import UserDashboard from './components/UserDashboard.vue';
import WebsiteInfoModal from './components/WebsiteInfoModal.vue';

// --- Main App Logic ---
const categories = ref([]);
const activeCategoryId = ref(null);
const user = ref(null);
const showAuthModal = ref(false);
const showPreviewModal = ref(false);
const showUserMenu = ref(false);
const previewVideo = ref(null);
const showWebsiteInfo = ref(false);
const searchQuery = ref('');
const showUserDashboard = ref(false);
const showPaymentModal = ref(false);
const paymentDetails = ref({ item_type: '', item_id: 0, amount: 0 });

const activeCategory = computed(() => {
  return categories.value.find(c => c.id === activeCategoryId.value) || null;
});

const filteredVideos = computed(() => {
  if (!activeCategory.value) return [];
  const query = searchQuery.value.toLowerCase();
  if (!query) return activeCategory.value.videos;
  return activeCategory.value.videos.filter(video => {
    const titleMatch = video.title.toLowerCase().includes(query);
    return titleMatch;
  });
});

const fetchCourses = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/courses');
    categories.value = response.data;
    if (categories.value.length > 0) {
      activeCategoryId.value = categories.value[0].id;
    }
  } catch (error) {
    console.error("Failed to fetch courses:", error);
  }
};

const fetchUser = async () => {
  const token = localStorage.getItem('token');
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    try {
      const response = await axios.get('http://localhost:8000/api/users/me');
      user.value = response.data;
    } catch (error) {
      console.error("Session expired or invalid:", error);
      logout();
    }
  }
};

const onAuthenticated = (token) => {
  localStorage.setItem('token', token);
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  fetchUser();
  showAuthModal.value = false;
};

const logout = () => {
  localStorage.removeItem('token');
  delete axios.defaults.headers.common['Authorization'];
  user.value = null;
  showUserMenu.value = false;
};

const playPreview = (video) => {
  previewVideo.value = video;
  showPreviewModal.value = true;
};

const initiatePurchase = (item_type, item_id, price) => {
  if (!user.value) {
    showAuthModal.value = true;
    return;
  }
  paymentDetails.value = { item_type, item_id, amount: price };
  showPaymentModal.value = true;
};

const handleSuccessfulPayment = async () => {
  try {
    await axios.post('http://localhost:8000/api/purchase', {
      item_type: paymentDetails.value.item_type,
      item_id: paymentDetails.value.item_id
    });
    // Payment successful, just close the modal and refresh user data.
    fetchUser(); // Refresh user data to get new purchases
  } catch (error) {
    alert('购买记录更新失败: ' + (error.response?.data?.detail || '请稍后再试'));
  }
  showPaymentModal.value = false;
};

const downloadVideo = async (video_id, video_title) => {
  if (!user.value) {
    showAuthModal.value = true;
    return;
  }
  try {
    const response = await axios.get(`http://localhost:8000/api/download/${video_id}`, {
      responseType: 'blob', // Important: expect a binary response
    });

    // Create a URL for the blob data
    const url = window.URL.createObjectURL(new Blob([response.data]));
    
    // Create a temporary link to trigger the download
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${video_title.replace(/ /g, '_')}.mp4`);
    document.body.appendChild(link);
    link.click();

    // Clean up the temporary URL and link
    window.URL.revokeObjectURL(url);
    document.body.removeChild(link);

    fetchUser(); // Refresh user data to update download count
  } catch (error) {
    let errorMessage = '下载失败，请稍后再试。';
    if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        try {
            // The response data is a blob, we need to read it as text
            const errorBlob = new Blob([error.response.data]);
            const errorText = await errorBlob.text();
            const errorJson = JSON.parse(errorText);
            errorMessage = `下载失败: ${errorJson.detail || '未知服务端错误'}`;
        } catch (e) {
            errorMessage = `下载失败: 无法解析错误详情 (状态码: ${error.response.status})`
        }
    } else if (error.request) {
        // The request was made but no response was received
        errorMessage = '下载失败: 无法连接到服务器，请检查您的网络和后端服务状态。';
    } else {
        // Something happened in setting up the request that triggered an Error
        errorMessage = `下载失败: ${error.message}`;
    }
    alert(errorMessage);
  }
};

const isCategoryPurchased = (categoryId) => {
  if (!user.value || !user.value.purchases) return false;
  return user.value.purchases.some(p => p.item_type === 'category' && p.item_id === categoryId);
};

const hasAccess = (videoId) => {
  if (!user.value || !user.value.purchases) return false;
  
  const categoryOfVideo = categories.value.find(c => c.videos.some(v => v.id === videoId));
  if (!categoryOfVideo) return false;

  const hasCategoryAccess = isCategoryPurchased(categoryOfVideo.id);
  if (hasCategoryAccess) return true;

  const hasVideoAccess = user.value.purchases.some(p => p.item_type === 'video' && p.item_id === videoId);
  return hasVideoAccess;
};

onMounted(() => {
  fetchUser();
  fetchCourses();
});
</script>

<style>
/* Basic styling for the app */
#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Custom scrollbar hiding utility */
.hide-scrollbar::-webkit-scrollbar {
    display: none; /* for Chrome, Safari, and Opera */
}

.hide-scrollbar {
  -ms-overflow-style: none;  /* for Internet Explorer, Edge */
  scrollbar-width: none;  /* for Firefox */
}
</style>
