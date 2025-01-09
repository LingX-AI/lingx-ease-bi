import MarkdownIt from 'markdown-it'
import mdDeflist from 'markdown-it-deflist'
import mk from 'markdown-it-katex'
import MarkdownItHighlightjs from 'markdown-it-highlightjs'
import 'highlight.js/styles/a11y-light.css'

export const markdown = new MarkdownIt({
  html: true,
  xhtmlOut: true,
  breaks: true,
  linkify: true,
  typographer: true,
})
  .use(mdDeflist)
  .use(MarkdownItHighlightjs, { auto: true, inline: true })
  .use(mk)

export const jsonObj2JsonFile = (jsonObj: any, fileName: string) => {
  const jsonString = JSON.stringify(jsonObj, null, 2)
  const blob = new Blob([jsonString], { type: 'application/json' })
  const urlToDownload = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = urlToDownload
  link.download = fileName
  link.click()
  URL.revokeObjectURL(urlToDownload)
}
