<!-- filepath: c:\Users\Chen junxin\Desktop\上课课件以及资料\数据库\BH\musicsystem\frontend\src\views\Albums.vue -->
<template>
  <div class="albums-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>专辑管理</h1>
        <p class="subtitle">共 {{ albums.length }} 张专辑</p>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索专辑或歌手..."
          prefix-icon="Search"
          class="search-input"
          clearable
        />
        <el-button type="primary" @click="handleAdd" :icon="Plus">
          添加专辑
        </el-button>
      </div>
    </div>

    <!-- 专辑网格 -->
    <div class="albums-content" v-loading="loading">
      <div class="albums-grid">
        <div
          v-for="album in filteredAlbums"
          :key="album.album_id"
          class="album-card"
          @click="handleView(album)"
        >
          <div class="album-cover">
            <el-icon :size="60" color="#fff">
              <Collection />
            </el-icon>
          </div>
          <div class="album-info">
            <h3 class="album-title">{{ album.title }}</h3>
            <p class="album-artist">
              <el-icon><User /></el-icon>
              {{ album.artist_name || '未知歌手' }}
            </p>
          </div>
          <div class="album-actions">
            <el-button
              type="primary"
              size="small"
              @click.stop="handleEdit(album)"
              :icon="Edit"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click.stop="handleDelete(album)"
              :icon="Delete"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="filteredAlbums.length === 0 && !loading"
        description="暂无专辑数据"
      />
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑专辑' : '添加专辑'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="专辑名称" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="请输入专辑名称"
          />
        </el-form-item>

        <el-form-item label="歌手" prop="artist_id">
          <el-select
            v-model="formData.artist_id"
            placeholder="请选择歌手"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="artist in artists"
              :key="artist.artist_id"
              :label="artist.name"
              :value="artist.artist_id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 专辑歌曲抽屉 -->
    <el-drawer
      v-model="detailVisible"
      direction="rtl"
      size="720px"
      :with-header="false"
    >
      <div class="album-detail">
        <div class="detail-header">
          <div class="detail-cover">
            <el-icon :size="64" color="#fff">
              <Collection />
            </el-icon>
          </div>
          <div class="detail-info">
            <div class="detail-title">{{ selectedAlbum?.title || '专辑' }}</div>
            <div class="detail-artist">
              <el-icon><User /></el-icon>
              <span>{{ selectedAlbum?.artist_name || '未知歌手' }}</span>
            </div>
            <div class="detail-meta">
              共 {{ albumSongs.length }} 首歌曲
            </div>
            <div class="detail-actions">
              <el-button
                type="primary"
                :icon="VideoPlay"
                @click="handlePlayAll"
                :disabled="albumSongs.length === 0"
              >
                播放全部
              </el-button>
              <el-button type="primary" plain @click="openAddSongDialog">
                添加歌曲
              </el-button>
            </div>
          </div>
        </div>

        <div class="detail-content" v-loading="songsLoading">
          <el-table
            :data="albumSongs"
            style="width: 100%"
            :header-cell-style="{ background: '#fafafa', color: '#333' }"
            stripe
          >
            <el-table-column type="index" label="#" width="60" align="center" />
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
            <el-table-column prop="artist_name" label="歌手" min-width="150">
              <template #default="{ row }">
                <el-tag v-if="row.artist_name" type="info" effect="plain">
                  {{ row.artist_name }}
                </el-tag>
                <span v-else style="color: #999">未知歌手</span>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="时长" width="120" align="center">
              <template #default="{ row }">
                {{ formatDuration(row.duration) }}
              </template>
            </el-table-column>
          </el-table>

          <el-empty
            v-if="albumSongs.length === 0 && !songsLoading"
            description="暂无歌曲"
          />
        </div>
      </div>
    </el-drawer>

    <!-- 添加歌曲到专辑对话框 -->
    <el-dialog
      v-model="addSongDialogVisible"
      title="添加歌曲到专辑"
      width="800px"
    >
      <el-input
        v-model="songSearchKeyword"
        placeholder="搜索歌曲或歌手..."
        prefix-icon="Search"
        class="search-input"
        clearable
        style="margin-bottom: 15px"
      />

      <div class="add-actions">
        <el-button
          type="primary"
          @click="handleBatchAddSongs"
          :disabled="selectedSongs.length === 0"
          :loading="addSongsLoading"
        >
          批量添加
        </el-button>
        <span class="add-tip">已选择 {{ selectedSongs.length }} 首</span>
      </div>

      <el-table
        :data="filteredAvailableSongs"
        style="width: 100%"
        max-height="420px"
        @selection-change="handleSelectionChange"
        v-loading="addSongsLoading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="title" label="歌曲名称" min-width="220" />
        <el-table-column prop="artist_name" label="歌手" min-width="150">
          <template #default="{ row }">
            <el-tag v-if="row.artist_name" type="info" effect="plain">
              {{ row.artist_name }}
            </el-tag>
            <span v-else style="color: #999">未知歌手</span>
          </template>
        </el-table-column>
        <el-table-column prop="album_title" label="专辑" min-width="150">
          <template #default="{ row }">
            <el-tag v-if="row.album_title" effect="plain">
              {{ row.album_title }}
            </el-tag>
            <span v-else style="color: #999">未归属</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleAddSong(row)">
              添加
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Collection, User, VideoPlay } from '@element-plus/icons-vue'
import { albumsAPI, artistsAPI, songsAPI } from '@/api'
import { usePlayerStore } from '@/stores/player'
import { useRoute } from 'vue-router'

const albums = ref([])
const artists = ref([])
const songs = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const searchKeyword = ref('')
const formRef = ref(null)
const detailVisible = ref(false)
const selectedAlbum = ref(null)
const songsLoading = ref(false)
const addSongDialogVisible = ref(false)
const songSearchKeyword = ref('')
const selectedSongs = ref([])
const addSongsLoading = ref(false)

const playerStore = usePlayerStore()
const route = useRoute()

const formData = reactive({
  album_id: null,
  title: '',
  artist_id: null
})

const rules = {
  title: [
    { required: true, message: '请输入专辑名称', trigger: 'blur' }
  ]
}

const filteredAlbums = computed(() => {
  if (!searchKeyword.value) return albums.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return albums.value.filter(album => 
    album.title?.toLowerCase().includes(keyword) ||
    album.artist_name?.toLowerCase().includes(keyword)
  )
})

const albumSongs = computed(() => {
  if (!selectedAlbum.value) return []
  return songs.value.filter(song => song.album_id === selectedAlbum.value.album_id)
})

const availableSongs = computed(() => {
  if (!selectedAlbum.value) return []
  return songs.value.filter(song => !song.album_id)
})

const filteredAvailableSongs = computed(() => {
  if (!songSearchKeyword.value) return availableSongs.value
  const keyword = songSearchKeyword.value.toLowerCase()
  return availableSongs.value.filter(song =>
    song.title?.toLowerCase().includes(keyword) ||
    song.artist_name?.toLowerCase().includes(keyword)
  )
})

const formatDuration = (seconds) => {
  if (!seconds && seconds !== 0) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const loadAlbums = async () => {
  loading.value = true
  try {
    albums.value = await albumsAPI.getAll()
  } catch (error) {
    console.error('加载专辑失败:', error)
  } finally {
    loading.value = false
  }
}

const loadSongs = async () => {
  songsLoading.value = true
  try {
    songs.value = await songsAPI.getAll()
  } catch (error) {
    console.error('加载歌曲失败:', error)
  } finally {
    songsLoading.value = false
  }
}

const loadArtists = async () => {
  try {
    artists.value = await artistsAPI.getAll()
  } catch (error) {
    console.error('加载歌手失败:', error)
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  formData.album_id = row.album_id
  formData.title = row.title
  formData.artist_id = row.artist_id
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除专辑《${row.title}》吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await albumsAPI.delete(row.album_id)
      ElMessage.success('删除成功')
      loadAlbums()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const handleView = async (album) => {
  selectedAlbum.value = album
  detailVisible.value = true
  if (songs.value.length === 0) {
    await loadSongs()
  }
}

const openAlbumById = async (albumId) => {
  const id = Number(albumId)
  if (!id) return
  if (albums.value.length === 0) {
    await loadAlbums()
  }
  const target = albums.value.find(item => item.album_id === id)
  if (target) {
    await handleView(target)
  }
}

const handlePlay = (song) => {
  if (!song?.file_url) return
  playerStore.setPlaylist(albumSongs.value)
  playerStore.play(song)
}

const handlePlayAll = () => {
  const playable = albumSongs.value.filter(item => item.file_url)
  if (playable.length === 0) return
  playerStore.setPlaylist(playable)
  playerStore.play(playable[0])
}

const openAddSongDialog = async () => {
  addSongDialogVisible.value = true
  selectedSongs.value = []
  songSearchKeyword.value = ''
  if (songs.value.length === 0) {
    await loadSongs()
  }
}

const handleSelectionChange = (rows) => {
  selectedSongs.value = rows
}

const updateSongAlbum = async (song) => {
  const payload = {
    title: song.title,
    artist_id: song.artist_id,
    album_id: selectedAlbum.value.album_id,
    duration: song.duration
  }
  await songsAPI.update(song.song_id, payload)
}

const handleAddSong = async (song) => {
  if (!selectedAlbum.value) return
  addSongsLoading.value = true
  try {
    await updateSongAlbum(song)
    ElMessage.success('添加成功')
    await loadSongs()
  } catch (error) {
    console.error('添加失败:', error)
    ElMessage.error('添加失败')
  } finally {
    addSongsLoading.value = false
  }
}

const handleBatchAddSongs = async () => {
  if (!selectedAlbum.value || selectedSongs.value.length === 0) return
  addSongsLoading.value = true
  try {
    await Promise.all(selectedSongs.value.map(song => updateSongAlbum(song)))
    ElMessage.success(`已添加 ${selectedSongs.value.length} 首歌曲`)
    selectedSongs.value = []
    await loadSongs()
  } catch (error) {
    console.error('批量添加失败:', error)
    ElMessage.error('批量添加失败')
  } finally {
    addSongsLoading.value = false
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitLoading.value = true

    const data = {
      title: formData.title,
      artist_id: formData.artist_id
    }

    if (isEdit.value) {
      await albumsAPI.update(formData.album_id, data)
      ElMessage.success('更新成功')
    } else {
      await albumsAPI.create(data)
      ElMessage.success('添加成功')
    }

    dialogVisible.value = false
    loadAlbums()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const resetForm = () => {
  formData.album_id = null
  formData.title = ''
  formData.artist_id = null
  formRef.value?.resetFields()
}

onMounted(() => {
  loadAlbums()
  loadArtists()
  loadSongs()
})

watch(
  () => route.query.albumId,
  (albumId) => {
    if (albumId) {
      openAlbumById(albumId)
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.albums-container {
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

.header-right {
  display: flex;
  gap: 15px;
  align-items: center;
}

.search-input {
  width: 300px;
}

.albums-content {
  flex: 1;
  padding: 30px;
  overflow: auto;
}

.albums-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 25px;
}

.album-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  cursor: pointer;
}

.album-card:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-8px);
}

.album-cover {
  height: 220px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.album-cover::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.2) 0%, transparent 70%);
}

.album-info {
  padding: 15px;
}

.album-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.album-artist {
  font-size: 13px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 12px;
}

.album-actions {
  padding: 0 15px 15px;
  display: flex;
  gap: 8px;
}

.album-actions .el-button {
  flex: 1;
}

.album-detail {
  padding: 20px;
}

.detail-header {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-cover {
  width: 140px;
  height: 140px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}

.detail-cover::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.2) 0%, transparent 70%);
}

.detail-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-title {
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.detail-artist {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 14px;
}

.detail-meta {
  color: #999;
  font-size: 13px;
}

.detail-actions {
  margin-top: 8px;
  display: flex;
  gap: 10px;
}

.detail-content {
  padding-bottom: 20px;
}

.add-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.add-tip {
  color: #999;
  font-size: 12px;
}
</style>