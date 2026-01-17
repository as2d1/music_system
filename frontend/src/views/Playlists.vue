<!-- filepath: c:\Users\Chen junxin\Desktop\上课课件以及资料\数据库\BH\musicsystem\frontend\src\views\Playlists.vue -->
<template>
  <div class="playlists-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>我的歌单</h1>
        <p class="subtitle">共 {{ playlists.length }} 个歌单</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleAddPlaylist" :icon="Plus">
          创建歌单
        </el-button>
      </div>
    </div>

    <!-- 歌单列表 -->
    <div class="playlists-content" v-loading="loading">
      <div class="playlists-grid">
        <div
          v-for="playlist in playlists"
          :key="playlist.playlist_id"
          class="playlist-card"
          @click="viewPlaylistDetail(playlist)"
        >
          <div class="playlist-cover">
            <el-icon :size="50" color="#fff">
              <Menu />
            </el-icon>
            <div class="playlist-count">{{ playlist.song_count || 0 }} 首</div>
          </div>
          <div class="playlist-info">
            <h3>{{ playlist.name }}</h3>
            <p>创建者: {{ playlist.username || '未知' }}</p>
          </div>
          <div class="playlist-actions" @click.stop>
            <el-button
              type="danger"
              size="small"
              text
              @click="handleDeletePlaylist(playlist)"
              :icon="Delete"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="playlists.length === 0 && !loading"
        description="还没有歌单，快去创建一个吧"
      />
    </div>

    <!-- 创建歌单对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建歌单"
      width="500px"
      @close="resetCreateForm"
    >
      <el-form
        ref="createFormRef"
        :model="createFormData"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="歌单名称" prop="name">
          <el-input
            v-model="createFormData.name"
            placeholder="请输入歌单名称"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreatePlaylist" :loading="submitLoading">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 歌单详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentPlaylist?.name"
      width="800px"
    >
      <div class="playlist-detail">
        <div class="detail-header">
          <el-button type="primary" @click="showAddSongDialog" :icon="Plus">
            添加歌曲
          </el-button>
        </div>

        <el-table
          :data="currentPlaylist?.songs || []"
          style="width: 100%"
          v-loading="detailLoading"
        >
          <el-table-column type="index" label="#" width="60" />
          <el-table-column prop="title" label="歌曲名称" min-width="200" />
          <el-table-column prop="artist_name" label="歌手" min-width="150" />
          <el-table-column prop="album_title" label="专辑" min-width="150" />
          <el-table-column prop="duration" label="时长" width="100">
            <template #default="{ row }">
              {{ formatDuration(row.duration) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button
                type="danger"
                size="small"
                text
                @click="handleRemoveSong(row)"
                :icon="Delete"
              >
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-if="!currentPlaylist?.songs?.length && !detailLoading"
          description="歌单是空的，快去添加歌曲吧"
        />
      </div>
    </el-dialog>

    <!-- 添加歌曲对话框 -->
    <el-dialog
      v-model="addSongDialogVisible"
      title="添加歌曲到歌单"
      width="700px"
    >
      <el-input
        v-model="songSearchKeyword"
        placeholder="搜索歌曲..."
        prefix-icon="Search"
        class="search-input"
        clearable
        style="margin-bottom: 15px"
      />

      <el-table
        :data="filteredAvailableSongs"
        style="width: 100%"
        max-height="400px"
        v-loading="songsLoading"
      >
        <el-table-column prop="title" label="歌曲名称" min-width="200" />
        <el-table-column prop="artist_name" label="歌手" min-width="120" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleAddSongToPlaylist(row)"
            >
              添加
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Menu } from '@element-plus/icons-vue'
import { playlistsAPI, songsAPI } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const playlists = ref([])
const allSongs = ref([])
const currentPlaylist = ref(null)
const loading = ref(false)
const detailLoading = ref(false)
const songsLoading = ref(false)
const submitLoading = ref(false)
const createDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const addSongDialogVisible = ref(false)
const songSearchKeyword = ref('')
const createFormRef = ref(null)

const createFormData = reactive({
  name: ''
})

const createRules = {
  name: [
    { required: true, message: '请输入歌单名称', trigger: 'blur' }
  ]
}

const filteredAvailableSongs = computed(() => {
  if (!songSearchKeyword.value) return allSongs.value
  
  const keyword = songSearchKeyword.value.toLowerCase()
  return allSongs.value.filter(song => 
    song.title?.toLowerCase().includes(keyword) ||
    song.artist_name?.toLowerCase().includes(keyword)
  )
})

const formatDuration = (seconds) => {
  if (!seconds) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const loadPlaylists = async () => {
  loading.value = true
  try {
    playlists.value = await playlistsAPI.getAll(userStore.userInfo?.user_id)
  } catch (error) {
    console.error('加载歌单失败:', error)
  } finally {
    loading.value = false
  }
}

const loadAllSongs = async () => {
  songsLoading.value = true
  try {
    allSongs.value = await songsAPI.getAll()
  } catch (error) {
    console.error('加载歌曲失败:', error)
  } finally {
    songsLoading.value = false
  }
}

const handleAddPlaylist = () => {
  createDialogVisible.value = true
}

const handleCreatePlaylist = async () => {
  try {
    await createFormRef.value?.validate()
    submitLoading.value = true

    await playlistsAPI.create({
      name: createFormData.name,
      user_id: userStore.userInfo?.user_id
    })

    ElMessage.success('创建成功')
    createDialogVisible.value = false
    loadPlaylists()
  } catch (error) {
    console.error('创建失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleDeletePlaylist = (playlist) => {
  ElMessageBox.confirm(
    `确定要删除歌单《${playlist.name}》吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await playlistsAPI.delete(playlist.playlist_id)
      ElMessage.success('删除成功')
      loadPlaylists()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const viewPlaylistDetail = async (playlist) => {
  detailLoading.value = true
  detailDialogVisible.value = true
  
  try {
    currentPlaylist.value = await playlistsAPI.getOne(playlist.playlist_id)
  } catch (error) {
    console.error('加载歌单详情失败:', error)
  } finally {
    detailLoading.value = false
  }
}

const showAddSongDialog = () => {
  addSongDialogVisible.value = true
  if (allSongs.value.length === 0) {
    loadAllSongs()
  }
}

const handleAddSongToPlaylist = async (song) => {
  try {
    await playlistsAPI.addSong(currentPlaylist.value.playlist_id, song.song_id)
    ElMessage.success('添加成功')
    
    // 重新加载歌单详情
    const updated = await playlistsAPI.getOne(currentPlaylist.value.playlist_id)
    currentPlaylist.value = updated
  } catch (error) {
    console.error('添加失败:', error)
  }
}

const handleRemoveSong = (song) => {
  ElMessageBox.confirm(
    `确定要从歌单中移除《${song.title}》吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await playlistsAPI.removeSong(currentPlaylist.value.playlist_id, song.song_id)
      ElMessage.success('移除成功')
      
      // 重新加载歌单详情
      const updated = await playlistsAPI.getOne(currentPlaylist.value.playlist_id)
      currentPlaylist.value = updated
    } catch (error) {
      console.error('移除失败:', error)
    }
  }).catch(() => {})
}

const resetCreateForm = () => {
  createFormData.name = ''
  createFormRef.value?.resetFields()
}

onMounted(() => {
  loadPlaylists()
})
</script>

<style scoped>
.playlists-container {
  height: 100%;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px;
  border-bottom: 1px solid #f0f0f0;
}

.header-left h1 {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  color: #999;
  font-size: 14px;
}

.playlists-content {
  flex: 1;
  padding: 30px;
  overflow: auto;
}

.playlists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.playlist-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  cursor: pointer;
}

.playlist-card:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-5px);
}

.playlist-cover {
  height: 200px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.playlist-count {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.3);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.playlist-info {
  padding: 15px;
}

.playlist-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.playlist-info p {
  font-size: 13px;
  color: #999;
}

.playlist-actions {
  padding: 0 15px 15px;
}

.playlist-detail {
  min-height: 300px;
}

.detail-header {
  margin-bottom: 15px;
}
</style>