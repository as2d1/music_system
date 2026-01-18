<!-- filepath: c:\Users\Chen junxin\Desktop\上课课件以及资料\数据库\BH\musicsystem\frontend\src\views\Artists.vue -->
<template>
  <div class="artists-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>歌手管理</h1>
        <p class="subtitle">共 {{ artists.length }} 位歌手</p>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索歌手..."
          prefix-icon="Search"
          class="search-input"
          clearable
        />
        <el-button type="primary" @click="handleAdd" :icon="Plus">
          添加歌手
        </el-button>
      </div>
    </div>

    <!-- 歌手卡片网格 -->
    <div class="artists-content" v-loading="loading">
      <div class="artists-grid">
        <div
          v-for="artist in filteredArtists"
          :key="artist.artist_id"
          class="artist-card"
          @click="handleView(artist)"
        >
          <div class="artist-avatar">
            <el-icon :size="50" color="#409EFF">
              <User />
            </el-icon>
          </div>
          <div class="artist-info">
            <h3>{{ artist.name }}</h3>
            <p>歌手 ID: {{ artist.artist_id }}</p>
          </div>
          <div class="artist-actions">
            <el-button
              type="primary"
              size="small"
              text
              @click.stop="handleEdit(artist)"
              :icon="Edit"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              text
              @click.stop="handleDelete(artist)"
              :icon="Delete"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="filteredArtists.length === 0 && !loading"
        description="暂无歌手数据"
      />
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑歌手' : '添加歌手'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="歌手名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入歌手名称"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 歌手详情抽屉 -->
    <el-drawer
      v-model="detailVisible"
      direction="rtl"
      size="820px"
      :with-header="false"
    >
      <div class="artist-detail">
        <div class="detail-header">
          <div class="detail-avatar">
            <el-icon :size="64" color="#fff">
              <User />
            </el-icon>
          </div>
          <div class="detail-info">
            <div class="detail-title">{{ selectedArtist?.name || '歌手' }}</div>
            <div class="detail-meta">
              歌曲 {{ artistSongs.length }} 首 · 专辑 {{ artistAlbums.length }} 张
            </div>
            <div class="detail-actions">
              <el-button
                type="primary"
                :icon="VideoPlay"
                @click="handlePlayAll"
                :disabled="artistSongs.length === 0"
              >
                播放全部
              </el-button>
            </div>
          </div>
        </div>

        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="歌曲" name="songs">
            <div class="detail-content" v-loading="songsLoading">
              <el-table
                :data="artistSongs"
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
                <el-table-column prop="title" label="歌曲名称" min-width="220" />
                <el-table-column prop="album_title" label="专辑" min-width="180">
                  <template #default="{ row }">
                    <el-tag v-if="row.album_title" effect="plain">
                      {{ row.album_title }}
                    </el-tag>
                    <span v-else style="color: #999">未知专辑</span>
                  </template>
                </el-table-column>
                <el-table-column prop="duration" label="时长" width="120" align="center">
                  <template #default="{ row }">
                    {{ formatDuration(row.duration) }}
                  </template>
                </el-table-column>
              </el-table>

              <el-empty
                v-if="artistSongs.length === 0 && !songsLoading"
                description="暂无歌曲"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="专辑" name="albums">
            <div class="albums-panel" v-loading="albumsLoading">
              <div class="albums-grid">
                <div
                  v-for="album in artistAlbums"
                  :key="album.album_id"
                  class="mini-album-card"
                  @click="handleAlbumJump(album)"
                >
                  <div class="mini-album-cover">
                    <el-icon :size="36" color="#fff">
                      <Collection />
                    </el-icon>
                  </div>
                  <div class="mini-album-info">
                    <div class="mini-album-title">{{ album.title }}</div>
                    <div class="mini-album-meta">{{ getAlbumSongCount(album.album_id) }} 首歌曲</div>
                  </div>
                </div>
              </div>

              <el-empty
                v-if="artistAlbums.length === 0 && !albumsLoading"
                description="暂无专辑"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, User, VideoPlay, Collection } from '@element-plus/icons-vue'
import { artistsAPI, songsAPI, albumsAPI } from '@/api'
import { usePlayerStore } from '@/stores/player'
import { useRouter } from 'vue-router'

const artists = ref([])
const songs = ref([])
const albums = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const searchKeyword = ref('')
const formRef = ref(null)
const detailVisible = ref(false)
const selectedArtist = ref(null)
const songsLoading = ref(false)
const albumsLoading = ref(false)
const activeTab = ref('songs')

const playerStore = usePlayerStore()
const router = useRouter()

const formData = reactive({
  artist_id: null,
  name: ''
})

const rules = {
  name: [
    { required: true, message: '请输入歌手名称', trigger: 'blur' }
  ]
}

const filteredArtists = computed(() => {
  if (!searchKeyword.value) return artists.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return artists.value.filter(artist => 
    artist.name?.toLowerCase().includes(keyword)
  )
})

const artistSongs = computed(() => {
  if (!selectedArtist.value) return []
  return songs.value.filter(song => song.artist_id === selectedArtist.value.artist_id)
})

const artistAlbums = computed(() => {
  if (!selectedArtist.value) return []
  return albums.value.filter(album => album.artist_id === selectedArtist.value.artist_id)
})

const formatDuration = (seconds) => {
  if (!seconds && seconds !== 0) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const loadArtists = async () => {
  loading.value = true
  try {
    artists.value = await artistsAPI.getAll()
  } catch (error) {
    console.error('加载歌手失败:', error)
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

const loadAlbums = async () => {
  albumsLoading.value = true
  try {
    albums.value = await albumsAPI.getAll()
  } catch (error) {
    console.error('加载专辑失败:', error)
  } finally {
    albumsLoading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  formData.artist_id = row.artist_id
  formData.name = row.name
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除歌手《${row.name}》吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await artistsAPI.delete(row.artist_id)
      ElMessage.success('删除成功')
      loadArtists()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const handleView = async (artist) => {
  selectedArtist.value = artist
  detailVisible.value = true
  activeTab.value = 'songs'
  if (songs.value.length === 0) {
    await loadSongs()
  }
  if (albums.value.length === 0) {
    await loadAlbums()
  }
}

const handlePlay = (song) => {
  if (!song?.file_url) return
  playerStore.setPlaylist(artistSongs.value)
  playerStore.play(song)
}

const handlePlayAll = () => {
  const playable = artistSongs.value.filter(item => item.file_url)
  if (playable.length === 0) return
  playerStore.setPlaylist(playable)
  playerStore.play(playable[0])
}

const handleAlbumJump = (album) => {
  if (!album?.album_id) return
  detailVisible.value = false
  router.push({ path: '/albums', query: { albumId: String(album.album_id) } })
}

const getAlbumSongCount = (albumId) => {
  return artistSongs.value.filter(song => song.album_id === albumId).length
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitLoading.value = true

    const data = { name: formData.name }

    if (isEdit.value) {
      await artistsAPI.update(formData.artist_id, data)
      ElMessage.success('更新成功')
    } else {
      await artistsAPI.create(data)
      ElMessage.success('添加成功')
    }

    dialogVisible.value = false
    loadArtists()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const resetForm = () => {
  formData.artist_id = null
  formData.name = ''
  formRef.value?.resetFields()
}

onMounted(() => {
  loadArtists()
  loadSongs()
  loadAlbums()
})
</script>

<style scoped>
.artists-container {
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

.artists-content {
  flex: 1;
  padding: 30px;
  overflow: auto;
}

.artists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.artist-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 25px;
  text-align: center;
  transition: all 0.3s;
  cursor: pointer;
}

.artist-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-5px);
}

.artist-avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
}

.artist-info h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 600;
}

.artist-info p {
  color: #999;
  font-size: 13px;
  margin-bottom: 15px;
}

.artist-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.artist-detail {
  padding: 20px;
}

.detail-header {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-avatar {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.detail-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-title {
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.detail-meta {
  color: #999;
  font-size: 13px;
}

.detail-actions {
  margin-top: 8px;
}

.detail-tabs {
  margin-top: 10px;
}

.detail-content {
  padding-bottom: 20px;
}

.albums-panel {
  padding: 10px 0 20px;
}

.albums-panel .albums-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 18px;
}

.mini-album-card {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
}

.mini-album-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-4px);
}

.mini-album-cover {
  height: 100px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-album-info {
  padding: 12px;
}

.mini-album-title {
  font-size: 14px;
  color: #333;
  font-weight: 600;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mini-album-meta {
  font-size: 12px;
  color: #999;
}
</style>