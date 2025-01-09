<script setup lang="ts">
import { CopyOutlined } from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'
import { useDeploymentModel } from '@/composables/specific/app'
import { useCopy, useModal } from '@/composables/common'

interface IProps {
  applicationId: string | number
}

const { applicationId } = defineProps<IProps>()
const emit = defineEmits(['refresh-model-list'])
const { t } = useI18n()
const { visible, handleCancel } = useModal()
const convertFormRef = ref()
const deploymentFormRef = ref()
const loading = ref(false)
const { handleCopy } = useCopy()
const convertCommandExample = `# Initialize conda environment
source /home/os/miniconda3/etc/profile.d/conda.sh

# Change to llama.cpp project directory
cd /home/os/PycharmProjects/llama.cpp

# Activate conda environment for llama.cpp
conda activate llama-cpp

# Convert Hugging Face model to GGUF format
# Parameters:
# - Input: /data/models/fine-tuning-models/lingxai-nl2sql (HF model path)
# - Output: /data/models/fine-tuning-models/<modelName>.gguf (GGUF model path)
python convert_hf_to_gguf.py /data/models/fine-tuning-models/lingxai-nl2sql --outfile /data/models/fine-tuning-models/<modelName>.gguf
./build/bin/llama-quantize /data/models/fine-tuning-models/lingxai-nl2sql.gguf /data/models/fine-tuning-models/<modelName>-Q4_K_M.gguf Q4_K_M
`

const deploymentCommandExample = `# Create directory for custom model
mkdir -p /opt/1panel/apps/ollama/ollama/data/custom_models/<modelName>

# Copy the converted GGUF model to Ollama custom models directory
cp -r /data/models/fine-tuning-models/<modelName>.gguf /opt/1panel/apps/ollama/ollama/data/custom_models/<modelName>/<modelName>.gguf

# Create Modelfile from template
sh -c cat <<'EOF' > /opt/1panel/apps/ollama/ollama/data/custom_models/<modelName>/Modelfile
<Modelfile>
EOF

# Create new model in Ollama using the Modelfile
docker exec Ollama ollama create <modelName> -f /root/.ollama/custom_models/<modelName>/Modelfile
`

const modelfileExample = `from ./<modelName>.gguf
# set the temperature to 1 [higher is more creative, lower is more coherent]
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER repeat_penalty 1.05
PARAMETER top_k 20

TEMPLATE """{{ if .Messages }}
{{- if or .System .Tools }}<|im_start|>system
{{ .System }}
{{- if .Tools }}

# Tools

You are provided with function signatures within <tools></tools> XML tags:
<tools>{{- range .Tools }}
{"type": "function", "function": {{ .Function }}}{{- end }}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>
{{- end }}<|im_end|>
{{ end }}
{{- range $i, $_ := .Messages }}
{{- $last := eq (len (slice $.Messages $i)) 1 -}}
{{- if eq .Role "user" }}<|im_start|>user
{{ .Content }}<|im_end|>
{{ else if eq .Role "assistant" }}<|im_start|>assistant
{{ if .Content }}{{ .Content }}
{{- else if .ToolCalls }}<tool_call>
{{ range .ToolCalls }}{"name": "{{ .Function.Name }}", "arguments": {{ .Function.Arguments }}}
{{ end }}</tool_call>
{{- end }}{{ if not $last }}<|im_end|>
{{ end }}
{{- else if eq .Role "tool" }}<|im_start|>user
<tool_response>
{{ .Content }}
</tool_response><|im_end|>
{{ end }}
{{- if and (ne .Role "assistant") $last }}<|im_start|>assistant
{{ end }}
{{- end }}
{{- else }}
{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
{{ end }}{{ .Response }}{{ if .Response }}<|im_end|>{{ end }}"""

# set the system message
SYSTEM """You are Qwen, created by Alibaba Cloud. You are a helpful assistant."""
`

const convertModelFormData = reactive({
  applicationId,
  modelName: '',
  command: '',
})
const deploymentModelFormData = reactive({
  applicationId,
  modelName: '',
  command: '',
  modelfile: '',
})
const {
  convertModel,
  deploymentModel,
} = useDeploymentModel()

const curSegmented = ref('convert')
const segmentedOptions = computed(() => {
  return [
    { value: 'convert', label: t('dataset.deploymentModel.modelConversion') },
    { value: 'deployment', label: t('dataset.deploymentModel.modelDeployment') },
  ]
})

const handleConvertModel = async () => {
  const command = convertModelFormData.command.replace('<modelName>', convertModelFormData.modelName)
  const payload = { ...deploymentModelFormData, command }
  await convertModel(payload)
}

const handleDeploymentModel = async () => {
  const modelfile = deploymentModelFormData.modelfile.replaceAll('<modelName>', deploymentModelFormData.modelName)
  const command = deploymentModelFormData.command.replaceAll('<Modelfile>', modelfile).replaceAll('<modelName>', deploymentModelFormData.modelName)
  const payload = { ...deploymentModelFormData, command }
  await deploymentModel(payload)
}

const handleOk = async () => {
  const formRef = curSegmented.value === 'convert' ? convertFormRef : deploymentFormRef
  await formRef.value.validate()
  const action: Record<string, any> = {
    convert: handleConvertModel,
    deployment: handleDeploymentModel,
  }
  loading.value = true
  action[curSegmented.value]().finally(() => {
    loading.value = false
    emit('refresh-model-list')
  })
}
</script>

<template>
  <a-modal
    v-model:open="visible"
    :title="loading ? (curSegmented === 'convert' ? t('dataset.deploymentModel.modelConversion') : t('dataset.deploymentModel.modelDeployment')) : t('dataset.deploymentModel.convertAndDeploy')"
    centered
    width="600px"
    :mask-closable="false"
    :footer="null"
    v-bind="$attrs"
  >
    <div
      v-if="loading"
      class="flex flex-col items-center py-5"
    >
      <a-spin class="mb-5" />
      <span class="text-text-2">{{ t('dataset.deploymentModel.executingTask') }}</span>
    </div>
    <div v-else>
      <div class="flex-center pt-2">
        <a-segmented
          v-model:value="curSegmented"
          :options="segmentedOptions"
        />
      </div>
      <a-form
        v-if="curSegmented === 'convert'"
        ref="convertFormRef"
        class="p-5"
        :model="convertModelFormData"
        layout="vertical"
        autocomplete="off"
      >
        <p class="flex flex-col p-5 mb-2 rounded text-text-2 bg-bg-2">
          <span v-html="t('dataset.deploymentModel.llamaCppTip')" />
        </p>
        <a-form-item
          name="modelName"
          :rules="[{ required: true, message: t('dataset.deploymentModel.modelNameRequired') }]"
        >
          <template #label>
            <div>
              <span>{{ t('dataset.deploymentModel.modelName') }}</span>
              <span class="text-text-3 text-xs mb-2 ml-2">{{ t('dataset.deploymentModel.modelNameTip') }}</span>
            </div>
          </template>
          <a-input
            v-model:value="convertModelFormData.modelName"
            @change="deploymentModelFormData.modelName = convertModelFormData.modelName"
          />
        </a-form-item>
        <a-form-item
          name="command"
          :rules="[{ required: true, message: t('dataset.deploymentModel.commandRequired') }]"
        >
          <template #label>
            <div>
              <span>{{ t('dataset.deploymentModel.command') }}</span>
              <span class="text-text-3 text-xs mb-2 ml-2">{{ t('dataset.deploymentModel.commandTip') }}</span>
              <a-popover>
                <template #content>
                  <p class="flex items-center mb-1 text-[13px] font-medium">
                    {{ t('dataset.deploymentModel.commandExample') }}
                    <CopyOutlined
                      class="ml-2 text-text-2 cursor-pointer"
                      @click="handleCopy(convertCommandExample)"
                    />
                  </p>
                  <p class="w-[400px] h-fit whitespace-pre-wrap text-text-2 text-xs">
                    {{ convertCommandExample }}
                  </p>
                </template>
                <span class="ml-2 text-primary text-xs">{{ t('dataset.deploymentModel.example') }}</span>
              </a-popover>
            </div>
          </template>
          <a-textarea
            v-model:value="convertModelFormData.command"
            :auto-size="{ minRows: 4 }"
          />
        </a-form-item>
      </a-form>
      <a-form
        v-if="curSegmented === 'deployment'"
        ref="deploymentFormRef"
        class="p-5"
        :model="deploymentModelFormData"
        layout="vertical"
        autocomplete="off"
      >
        <p class="flex flex-col p-5 mb-2 rounded text-text-2 bg-bg-2">
          <span>{{ t('dataset.deploymentModel.deploymentTips.tip1') }}</span>
          <span>{{ t('dataset.deploymentModel.deploymentTips.tip2') }}</span>
        </p>
        <a-form-item
          name="modelName"
          :rules="[{ required: true, message: t('dataset.deploymentModel.modelNameRequired') }]"
        >
          <template #label>
            <div>
              <span>{{ t('dataset.deploymentModel.modelName') }}</span>
              <span class="text-text-3 text-xs mb-2 ml-2">{{ t('dataset.deploymentModel.modelNameTip') }}</span>
            </div>
          </template>
          <a-input
            v-model:value="deploymentModelFormData.modelName"
            @change="convertModelFormData.modelName = deploymentModelFormData.modelName"
          />
        </a-form-item>
        <a-form-item
          name="modelfile"
          :rules="[{ required: true, message: t('dataset.deploymentModel.modelfileRequired') }]"
        >
          <template #label>
            <div>
              <span>{{ t('dataset.deploymentModel.modelfile') }}</span>
              <span class="text-text-3 text-xs mb-2 ml-2">{{ t('dataset.deploymentModel.modelfileTip') }}</span>
              <a-popover>
                <template #content>
                  <div class="w-[400px]">
                    <p class="flex items-center mb-1 text-[13px] font-medium">
                      {{ t('dataset.deploymentModel.modelfileExample') }}
                      <CopyOutlined
                        class="ml-2 text-text-2 cursor-pointer"
                        @click="handleCopy(modelfileExample)"
                      />
                    </p>
                    <p class="max-h-[500px] whitespace-pre-wrap text-text-2 text-xs overflow-y-auto">
                      {{ modelfileExample }}
                    </p>
                  </div>
                </template>
                <span class="ml-2 text-primary text-xs">{{ t('dataset.deploymentModel.example') }}</span>
              </a-popover>
            </div>
          </template>
          <a-textarea
            v-model:value="deploymentModelFormData.modelfile"
            :auto-size="{ minRows: 4, maxRows: 8 }"
          />
        </a-form-item>
        <a-form-item
          name="command"
          :rules="[{ required: true, message: t('dataset.deploymentModel.commandRequired') }]"
        >
          <template #label>
            <div>
              <span>{{ t('dataset.deploymentModel.command') }}</span>
              <span class="text-text-3 text-xs mb-2 ml-2">{{ t('dataset.deploymentModel.commandTip1') }}</span>
              <a-popover>
                <template #content>
                  <div class="w-[400px]">
                    <p class="flex items-center mb-1 text-[13px] font-medium">
                      {{ t('dataset.deploymentModel.commandExample') }}
                      <CopyOutlined
                        class="ml-2 text-text-2 cursor-pointer"
                        @click="handleCopy(deploymentCommandExample)"
                      />
                    </p>
                    <p class="max-h-[500px] whitespace-pre-wrap text-text-2 text-xs overflow-y-auto">
                      {{ deploymentCommandExample }}
                    </p>
                  </div>
                </template>
                <span class="ml-2 text-primary text-xs">{{ t('dataset.deploymentModel.example') }}</span>
              </a-popover>
            </div>
          </template>
          <a-textarea
            v-model:value="deploymentModelFormData.command"
            :auto-size="{ minRows: 4 }"
          />
        </a-form-item>
      </a-form>
      <div class="flex justify-end w-full">
        <a-button
          class="mr-3"
          @click="handleCancel"
        >
          {{ t('common.cancel') }}
        </a-button>
        <a-button
          type="primary"
          @click="handleOk"
        >
          {{ curSegmented === 'convert' ? t('dataset.deploymentModel.startConversion') : t('dataset.deploymentModel.startDeployment') }}
        </a-button>
      </div>
    </div>
  </a-modal>
</template>

<style scoped lang="scss">

</style>
