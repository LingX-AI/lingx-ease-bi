<script setup lang="ts">
import LangSelection from '@/components/common/LangSelection.vue'
import { useLogin } from '@/composables/specific/login'
import { useUserStore } from '@/store'

const { t } = useI18n()
const store = useUserStore()
const { login } = useLogin()
const formState = reactive({
  username: localStorage.getItem('username') || '',
  password: '',
  remember: true,
})
const loading = ref(false)

store.clear()
const onFinish = async (values: any) => {
  const { username, password, remember } = values
  loading.value = true
  try {
    await login(username, password, remember)
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex-center w-[100vw] h-[100vh]">
    <div class="w-[440px] h-[100vh] p-10 px-12 bg-primary">
      <img
        class="w-[130px] mb-[50px]"
        src="@/assets/images/logo-lingx.png"
        alt="logo"
      >
      <img
        class="w-[60px] mb-5"
        src="@/assets/images/decoration.png"
        alt="decoration"
      >
      <span class="text-[22px] text-white font-medium font-[Lato]">
        {{ t('login.slogan') }}
      </span>
    </div>
    <div class="flex-1 flex-center flex-col h-full bg-bg-2">
      <div>
        <div class="flex flex-col mb-10">
          <img
            class="w-[180px] mb-[10px]"
            src="@/assets/images/logo.png"
            alt="logo"
          >
          <p class="mt-3 text-text-2 text-[14px] font-[500]">
            {{ t('login.welcome') }}
          </p>
        </div>
        <a-form
          class="w-[400px]"
          :model="formState"
          layout="vertical"
          autocomplete="off"
          @finish="onFinish"
        >
          <a-form-item
            name="username"
            :rules="[{ required: true, message: t('login.usernameRequired') }]"
          >
            <template #label>
              <span class="font-bold">{{ t('login.username') }}</span>
            </template>
            <a-input
              v-model:value="formState.username"
              class="h-[50px]"
              size="large"
              :placeholder="t('login.usernamePlaceholder')"
            />
          </a-form-item>

          <a-form-item
            name="password"
            :rules="[{ required: true, message: t('login.passwordRequired') }]"
          >
            <template #label>
              <span class="font-bold">{{ t('login.password') }}</span>
            </template>
            <a-input-password
              v-model:value="formState.password"
              class="h-[50px]"
              size="large"
              :placeholder="t('login.passwordPlaceholder')"
            />
          </a-form-item>

          <a-form-item name="remember">
            <a-checkbox v-model:checked="formState.remember">
              {{ t('login.rememberMe') }}
            </a-checkbox>
          </a-form-item>

          <a-form-item :wrapper-col="{ offset: 0 }">
            <a-button
              block
              type="primary"
              html-type="submit"
              size="large"
              class="min-h-[50px]"
              :loading="loading"
            >
              {{ t('login.login') }}
            </a-button>
          </a-form-item>
        </a-form>
      </div>
    </div>
    <LangSelection class="fixed top-[50px] right-[50px]" />
  </div>
</template>

<style scoped lang="scss"></style>
