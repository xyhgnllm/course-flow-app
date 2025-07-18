<template>
  <div class="fixed inset-0 bg-black bg-opacity-60 z-40 flex justify-center items-center" @click.self="$emit('close')">
    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-sm text-center">
      <h2 class="text-2xl font-bold mb-2">扫码支付</h2>
      <p class="text-gray-600 mb-4">请使用微信或支付宝扫码</p>
      
      <div class="flex justify-center mb-4">
        <img :src="qrCodeUrl" alt="QR Code" class="w-48 h-48 border rounded-lg p-2">
      </div>

      <p class="text-xl font-semibold mb-6">支付金额: <span class="text-red-500">¥ {{ amount.toFixed(2) }}</span></p>

      <div class="space-y-3">
        <button @click="$emit('payment-successful')" class="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg transition-colors">
          我已完成支付
        </button>
        <button @click="$emit('close')" class="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded-lg transition-colors">
          取消支付
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  amount: {
    type: Number,
    required: true,
  }
});

// In a real application, you would generate a unique QR code from your payment provider.
// For this demo, we use a placeholder QR code generator.
const qrCodeUrl = computed(() => `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=amount%3D${props.amount}`);

</script>
