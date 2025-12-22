<template>
  <router-view />
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'

const SIDEBAR_SELECTORS = [
  '[data-sidebar]',
  '.sidebar',
  '.app-sidebar',
  '.layout-sidebar',
  '.el-aside'
].join(',')

const PLAYERBAR_SELECTORS = [
  '[data-player-bar]',
  '.player-bar',
  '.playerBar',
  '#player-bar',
  '.audio-player' // 兼容你项目里曾出现过的类名
].join(',')

let mo
let ro
let rafId = 0

const setVar = (name, value) => {
  document.documentElement.style.setProperty(name, value)
}

const updateLayoutVars = () => {
  rafId = 0
  if (typeof window === 'undefined') return

  const sidebarEl = document.querySelector(SIDEBAR_SELECTORS)
  const sidebarW = sidebarEl ? Math.round(sidebarEl.getBoundingClientRect().width) : 0
  setVar('--app-sidebar-width', `${sidebarW}px`)

  const playerEl = document.querySelector(PLAYERBAR_SELECTORS)
  const playerH = playerEl ? Math.round(playerEl.getBoundingClientRect().height) : 0
  setVar('--playerbar-height', `${playerH}px`)

  // 只要播放栏存在，就给 body 预留底部空间；否则清理
  if (playerH > 0) {
    document.body.style.paddingBottom = `calc(${playerH}px + env(safe-area-inset-bottom, 0px))`
  } else {
    document.body.style.paddingBottom = ''
  }

  // 让播放栏不要出现在左侧侧边栏区域（只在右侧主界面）
  if (playerEl) {
    playerEl.style.left = `var(--app-sidebar-width)`
    playerEl.style.width = `calc(100% - var(--app-sidebar-width))`
  }
}

const scheduleUpdate = () => {
  if (rafId) return
  rafId = window.requestAnimationFrame(updateLayoutVars)
}

onMounted(() => {
  scheduleUpdate()

  mo = new MutationObserver(scheduleUpdate)
  mo.observe(document.body, { childList: true, subtree: true, attributes: true })

  if (window.ResizeObserver) {
    ro = new ResizeObserver(scheduleUpdate)
    // 观察侧边栏和播放栏（如果暂时找不到，MutationObserver 会触发后续更新）
    const sidebarEl = document.querySelector(SIDEBAR_SELECTORS)
    const playerEl = document.querySelector(PLAYERBAR_SELECTORS)
    if (sidebarEl) ro.observe(sidebarEl)
    if (playerEl) ro.observe(playerEl)
  } else {
    window.addEventListener('resize', scheduleUpdate)
  }
})

onBeforeUnmount(() => {
  if (rafId) cancelAnimationFrame(rafId)
  mo?.disconnect()
  ro?.disconnect()
  window.removeEventListener('resize', scheduleUpdate)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --app-sidebar-width: 0px;
  --playerbar-height: 0px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

#app {
  width: 100%;
  height: 100vh;
}

/* 强制：播放栏只出现在右侧主界面（侧边栏右边开始），不覆盖左侧侧边栏 */
:where([data-player-bar], .player-bar, .playerBar, #player-bar, .audio-player) {
  left: var(--app-sidebar-width, 0px) !important;
  width: calc(100% - var(--app-sidebar-width, 0px)) !important;
}
</style>