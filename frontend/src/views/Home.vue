<template>
  <el-container class="home-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <el-icon :size="30" color="#EC4141">
          <Headset />
        </el-icon>
        <span>音乐管理</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/songs">
          <el-icon><Headset /></el-icon>
          <span>精选</span>
        </el-menu-item>

        <el-menu-item index="/artists">
          <el-icon><User /></el-icon>
          <span>歌手</span>
        </el-menu-item>

        <el-menu-item index="/albums">
          <el-icon><Collection /></el-icon>
          <span>专辑</span>
        </el-menu-item>

        <el-menu-item index="/playlists">
          <el-icon><Menu /></el-icon>
          <span>歌单</span>
        </el-menu-item>
      </el-menu>

      <div class="user-section">
        <el-dropdown>
          <div class="user-info">
            <el-avatar :size="35" :icon="UserFilled" />
            <span>{{ userStore.userInfo?.username }}</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-main class="main-content" :class="{ 'has-player': playerStore.currentSong }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <!-- 全局播放条 -->
    <PlayerBar />
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { usePlayerStore } from '@/stores/player'
import PlayerBar from '@/components/PlayerBar.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const playerStore = usePlayerStore()

const activeMenu = computed(() => route.path)

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
  })
}
</script>

<style scoped>
.home-container {
  height: 100vh;
  background: #f5f5f5;
  font-family: serif;
}

.sidebar {
  background: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 25px 20px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
}

.sidebar-menu {
  flex: 1;
  border: none;
  padding: 10px 0;
  font-family: serif;
}

.sidebar-menu .el-menu-item {
  margin: 5px 10px;
  border-radius: 8px;
  height: 45px;
  line-height: 45px;
}

.sidebar-menu .el-menu-item:hover {
  background: #f5f5f5;
}

.sidebar-menu .el-menu-item.is-active {
  background: #ecf5ff;
  color: #409EFF;
}

.user-section {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.3s;
}

.user-info:hover {
  background: #f5f5f5;
}

.user-info span {
  font-size: 14px;
  color: #333;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.main-content {
  padding: 0;
  overflow-y: auto;
  height: 100%;
}

.main-content.has-player {
  height: calc(100% - 80px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>