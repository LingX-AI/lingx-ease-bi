<script setup lang="ts">
import type { Form } from 'ant-design-vue'
import { message } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import { useModal } from '@/composables/common'
import { useAppDatabase } from '@/composables/specific/app'

const { id } = defineProps<IProps>()

const emit = defineEmits(['saved'])

const { t } = useI18n()

interface IProps {
  id?: string | number
}
const { visible, handleCancel } = useModal()
const { createApplication, updateApplication, getApplication } = useAppDatabase()
const formRef = ref<InstanceType<typeof Form> | null>(null)
const formData = reactive({
  id,
  name: '',
  clientId: '',
  clientType: 'confidential',
  authorizationGrantType: 'client-credentials',
  clientSecret: '',
  hashClientSecret: false,
  databaseConfiguration: {
    db: 'Mysql',
    dbHost: '',
    dbName: '',
    dbPort: '',
    dbUser: '',
    dbPassword: '',
  },
  description: '',
})
const dbList = ['MySQL', 'PostgreSQL', 'Oracle', 'SQL Server']

const generateRandomString = (length: number) => {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length))
  }
  return result
}

const setDefaultValue = () => {
  if (!id) {
    formData.clientId = generateRandomString(40)
    formData.clientSecret = generateRandomString(128)
  }
}

const handleSaveApp = async () => {
  await (formRef.value as any).validate()
  const request = id ? updateApplication : createApplication
  const res = await request(formData)
  if (res) {
    emit('saved')
    message.success(t('application.saveSuccess'))
    handleCancel()
  }
}

watchEffect(() => {
  setDefaultValue()
  console.log(id)
  if (id) {
    getApplication(id).then((res) => {
      Object.assign(formData, res)
    })
  }
})
</script>

<template>
  <a-modal
    v-model:open="visible"
    :title="id ? t('application.updateApp') : t('application.createApp')"
    width="800px"
    centered
    v-bind="$attrs"
    :ok-text="t('common.save')"
    @cancel="handleCancel"
    @ok="handleSaveApp"
  >
    <div class="p-5 pl-0 pr-10 max-h-[80vh] overflow-y-auto">
      <a-form
        ref="formRef"
        class="w-full"
        :model="formData"
        layout="horizontal"
        :label-col="{ span: 7 }"
      >
        <a-form-item
          :label="t('application.name')"
          name="name"
          :rules="[{ required: true, message: t('application.nameRequired') }]"
        >
          <a-input v-model:value="formData.name" />
        </a-form-item>
        <a-form-item
          :label="t('application.description')"
          name="description"
          :rules="[{ required: true, message: t('application.descRequired') }]"
        >
          <a-textarea
            v-model:value="formData.description"
            auto-size
          />
        </a-form-item>
        <a-form-item
          :label="t('application.clientId')"
          name="clientId"
          :rules="[{ required: true, message: t('application.clientIdRequired') }]"
        >
          <a-input
            v-model:value="formData.clientId"
            :disabled="true"
          />
        </a-form-item>
        <a-form-item
          :label="t('application.clientSecret')"
          name="clientSecret"
          :rules="[{ required: true, message: t('application.clientSecretRequired') }]"
        >
          <a-textarea
            v-model:value="formData.clientSecret"
            auto-size
            :disabled="true"
          />
        </a-form-item>
        <a-form-item
          :label="t('application.database')"
          :name="['databaseConfiguration', 'db']"
          :rules="[{ required: true, message: t('application.dbRequired') }]"
        >
          <a-select v-model:value="formData.databaseConfiguration.db">
            <a-select-option
              v-for="item in dbList"
              :key="item"
              :value="item"
            >
              {{ item }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item
          :label="t('application.dbHost')"
          :name="['databaseConfiguration', 'dbHost']"
          :rules="[{ required: true, message: t('application.dbHostRequired') }]"
        >
          <a-input v-model:value="formData.databaseConfiguration.dbHost" />
        </a-form-item>
        <a-form-item
          :label="t('application.dbPort')"
          :name="['databaseConfiguration', 'dbPort']"
          :rules="[{ required: true, message: t('application.dbPortRequired') }]"
        >
          <a-input v-model:value="formData.databaseConfiguration.dbPort" />
        </a-form-item>
        <a-form-item
          :label="t('application.dbName')"
          :name="['databaseConfiguration', 'dbName']"
          :rules="[{ required: true, message: t('application.dbNameRequired') }]"
        >
          <a-input v-model:value="formData.databaseConfiguration.dbName" />
        </a-form-item>
        <a-form-item
          :label="t('application.dbUser')"
          :name="['databaseConfiguration', 'dbUser']"
          :rules="[{ required: true, message: t('application.dbUserRequired') }]"
        >
          <a-input v-model:value="formData.databaseConfiguration.dbUser" />
        </a-form-item>
        <a-form-item
          :label="t('application.dbPassword')"
          :name="['databaseConfiguration', 'dbPassword']"
          :rules="[{ required: true, message: t('application.dbPasswordRequired') }]"
        >
          <a-input-password v-model:value="formData.databaseConfiguration.dbPassword" />
        </a-form-item>
      </a-form>
    </div>
  </a-modal>
</template>

<style scoped lang="scss"></style>
