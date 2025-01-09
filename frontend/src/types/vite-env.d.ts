/// <reference types="vite/client" />
import { VNode } from 'vue';

declare module '*.vue' {
  import type { DefineComponent } from 'vue'

  const component: DefineComponent<{}, {}, any>
  export default component
}

declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elem: string]: any;
    }
    interface Element extends VNode {}
    interface ElementClass {
      $props: any;
    }
    interface IntrinsicAttributes {
      [attr: string]: any;
    }
  }
}