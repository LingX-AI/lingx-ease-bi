import antfu from '@antfu/eslint-config'

export default antfu(
  {
    vue: true,
    typescript: true,
    ignores: [
      '**/src/assets/**/*',
      '**/*.d.ts',
      '**/node_modules',
      '**/dist',
      '**/public',
    ],
  },
  {
    rules: {
      'antfu/top-level-function': 'off',
      'no-console': 'off',
      'ts/prefer-literal-enum-member': 'off',
      'eslint-comments/no-unlimited-disable': 'off',
      'vue/custom-event-name-casing': 'off',
      'ts/no-use-before-define': 'off',
      'ts/no-unused-expressions': 'off',
      'vue/attribute-hyphenation': 'off',
    },
  },
)
