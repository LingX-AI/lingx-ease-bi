declare module 'markdown-it-deflist' {
  import type { PluginSimple, PluginWithOptions } from 'markdown-it/lib'

  const markdownItDeflist: PluginSimple | PluginWithOptions
  export default markdownItDeflist
}
declare module 'markdown-it-katex' {
  import type { PluginSimple, PluginWithOptions } from 'markdown-it'

  const markdownItKatex: PluginSimple | PluginWithOptions
  export default markdownItKatex
}
