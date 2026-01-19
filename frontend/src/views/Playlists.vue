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
          <div class="detail-actions">
            <el-button
              type="primary"
              :icon="VideoPlay"
              @click="handlePlayAll"
              :disabled="!(currentPlaylist?.songs || []).length"
            >
              播放全部
            </el-button>
            <el-button type="primary" @click="showAddSongDialog" :icon="Plus">
              添加歌曲
            </el-button>
            <el-button 
              type="danger" 
              @click="handleBatchRemove" 
              :icon="Delete" 
              :disabled="selectedSongs.length === 0"
            >
              批量移除
            </el-button>
          </div>
        </div>

        <el-table
          ref="tableRef"
          :data="currentPlaylist?.songs || []"
          style="width: 100%"
          v-loading="detailLoading"
          row-key="song_id"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column type="index" label="#" width="60">
            <template #default>
              <el-icon style="cursor: move"><Grid /></el-icon>
            </template>
          </el-table-column>
          <el-table-column label="播放" width="80" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                circle
                size="small"
                :icon="VideoPlay"
                @click="handlePlay(row)"
                :disabled="!row.file_url"
              />
            </template>
          </el-table-column>
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
        >
          <el-button type="primary" @click="showAddSongDialog" :icon="Plus">
            去添加歌曲
          </el-button>
        </el-empty>
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
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Menu, VideoPlay, Grid } from '@element-plus/icons-vue'
import Sortable from 'sortablejs'
import { playlistsAPI, songsAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import { usePlayerStore } from '@/stores/player'

const userStore = useUserStore()
const playerStore = usePlayerStore()

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
const tableRef = ref(null)
const selectedSongs = ref([])
let sortableInstance = null

const createFormData = reactive({
  name: ''
})

const createRules = {
  name: [
    { required: true, message: '请输入歌单名称', trigger: 'blur' }
  ]
}

const handleSelectionChange = (selection) => {
  selectedSongs.value = selection
}

const handleBatchRemove = async () => {
  if (selectedSongs.value.length === 0) return

  try {
    await ElMessageBox.confirm(
      `确定要从歌单中移除选中的 ${selectedSongs.value.length} 首歌曲吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    detailLoading.value = true
    const songIds = selectedSongs.value.map(s => s.song_id)
    
    await playlistsAPI.removeSongsBatch(currentPlaylist.value.playlist_id, songIds)
    ElMessage.success('批量移除成功')
    
    // Refresh playlist
    await viewPlaylistDetail(currentPlaylist.value)
    selectedSongs.value = []
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('批量移除失败')
    }
  } finally {
    detailLoading.value = false
  }
}

const initSortable = () => {
  if (!tableRef.value) return
  const tbody = tableRef.value.$el.querySelector('.el-table__body-wrapper tbody')
  if (!tbody) return
  
  if (sortableInstance) sortableInstance.destroy()

  sortableInstance = Sortable.create(tbody, {
    handle: '.el-icon', // Use the Grid icon as handle
    animation: 150,
    onEnd: async ({ newIndex, oldIndex }) => {
      if (newIndex === oldIndex) return
      
      const playlist = currentPlaylist.value
      if (!playlist || !playlist.songs) return

      // Update local array first for smooth UX
      const targetRow = playlist.songs.splice(oldIndex, 1)[0]
      playlist.songs.splice(newIndex, 0, targetRow)
      
      const songIds = playlist.songs.map(s => s.song_id)
      
      try {
        await playlistsAPI.reorderSongs(playlist.playlist_id, songIds)
      } catch (error) {
        console.error('排序更新失败', error)
        ElMessage.error('排序更新失败')
        // Revert (optional, or just refresh)
        await viewPlaylistDetail(playlist)
      }
    }
  })
}

watch(detailDialogVisible, (val) => {
  if (val) {
    nextTick(() => {
      initSortable()
    })
  } else {
    if (sortableInstance) {
      sortableInstance.destroy()
      sortableInstance = null
    }
  }
})

watch(() => currentPlaylist.value?.songs, () => {
   if (detailDialogVisible.value) {
     nextTick(() => {
       initSortable()
     })
   }
})

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

const hydratePlaylistSongs = (playlist) => {
  if (!playlist?.songs || allSongs.value.length === 0) return playlist
  const songMap = new Map(allSongs.value.map(song => [song.song_id, song]))
  playlist.songs = playlist.songs.map(song => {
    const matched = songMap.get(song.song_id)
    if (!matched) return song
    return {
      ...matched,
      ...song,
      file_url: song.file_url || matched.file_url,
      artist_name: song.artist_name || matched.artist_name,
      album_title: song.album_title || matched.album_title,
      duration: song.duration ?? matched.duration
    }
  })
  return playlist
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
    if (allSongs.value.length === 0) {
      await loadAllSongs()
    }
    const data = await playlistsAPI.getOne(playlist.playlist_id)
    currentPlaylist.value = hydratePlaylistSongs(data)
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
    currentPlaylist.value = hydratePlaylistSongs(updated)
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
      currentPlaylist.value = hydratePlaylistSongs(updated)
    } catch (error) {
      console.error('移除失败:', error)
    }
  }).catch(() => {})
}

const handlePlay = (song) => {
  const list = currentPlaylist.value?.songs || []
  const playableSong = song?.file_url
    ? song
    : (allSongs.value.find(item => item.song_id === song?.song_id) || song)
  if (!playableSong?.file_url) return
  playerStore.setPlaylist(list)
  playerStore.play(playableSong)
}

const handlePlayAll = () => {
  const list = (currentPlaylist.value?.songs || []).map(item => {
    if (item.file_url) return item
    const matched = allSongs.value.find(song => song.song_id === item.song_id)
    return matched ? { ...item, file_url: matched.file_url } : item
  }).filter(item => item.file_url)
  if (list.length === 0) return
  playerStore.setPlaylist(list)
  playerStore.play(list[0])
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
  display: flex;
  justify-content: flex-end;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
</style>