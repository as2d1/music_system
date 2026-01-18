<!-- filepath: c:\Users\Chen junxin\Desktop\上课课件以及资料\数据库\BH\musicsystem\frontend\src\views\Songs.vue -->
<template>
  <div class="songs-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>歌曲管理</h1>
        <p class="subtitle">共 {{ songs.length }} 首歌曲</p>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索歌曲、歌手或专辑..."
          prefix-icon="Search"
          class="search-input"
          clearable
        />
        <el-button
          type="primary"
          plain
          :icon="VideoPlay"
          @click="handlePlayAll"
          :disabled="playableSongs.length === 0"
        >
          播放全部
        </el-button>
        <el-button
          @click="triggerBatchImport"
          :loading="batchImporting"
        >
          批量导入
        </el-button>
        <el-button type="primary" @click="handleAdd" :icon="Plus">
          添加歌曲
        </el-button>
        <input
          ref="batchInputRef"
          type="file"
          accept="audio/*"
          multiple
          class="file-input"
          style="display: none"
          @change="handleBatchFileChange"
        />
      </div>
    </div>

    <!-- 歌曲列表 -->
    <div class="songs-content">
      <el-table
        :data="filteredSongs"
        style="width: 100%"
        :header-cell-style="{ background: '#fafafa', color: '#333' }"
        stripe
        v-loading="loading"
      >
        <el-table-column type="index" label="#" width="60" align="center" />
        
        <el-table-column label="播放" width="80" align="center">
          <template #default="{ row }">
            <el-button
              type="primary"
              circle
              size="small"
              :icon="VideoPlay"
              @click.stop="handlePlay(row)"
              :disabled="!row.file_url"
            />
          </template>
        </el-table-column>

        <el-table-column prop="title" label="歌曲名称" min-width="200">
          <template #default="{ row }">
            <div class="song-title">
              <el-icon class="song-icon" color="#409EFF">
                <Headset />
              </el-icon>
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>

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
            <span v-else style="color: #999">未知专辑</span>
          </template>
        </el-table-column>

        <el-table-column prop="duration" label="时长" width="120" align="center">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              text
              @click="handleEdit(row)"
              :icon="Edit"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              text
              @click="handleDelete(row)"
              :icon="Delete"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑歌曲' : '添加歌曲'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="歌曲名称" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="请输入歌曲名称"
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

        <el-form-item label="专辑" prop="album_id">
          <el-select
            v-model="formData.album_id"
            placeholder="请选择专辑"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="album in albums"
              :key="album.album_id"
              :label="album.title"
              :value="album.album_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="时长(秒)" prop="duration">
          <el-input-number
            v-model="formData.duration"
            :min="0"
            :max="3600"
            placeholder="请输入时长"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="歌曲文件" v-if="!isEdit">
          <input type="file" @change="handleFileChange" accept="audio/*" class="file-input" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 底部播放器 -->
    <!-- 已移除，使用全局 PlayerBar -->
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, VideoPlay } from '@element-plus/icons-vue'
import { songsAPI, artistsAPI, albumsAPI } from '@/api'
import { usePlayerStore } from '@/stores/player'
import { parseBlob } from 'music-metadata-browser'

const playerStore = usePlayerStore()

// 数据
const songs = ref([])
const artists = ref([])
const albums = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const searchKeyword = ref('')
const formRef = ref(null)
const file = ref(null)
const currentSong = ref(null)
const audioRef = ref(null)
const batchInputRef = ref(null)
const batchImporting = ref(false)

const formData = reactive({
  song_id: null,
  title: '',
  artist_id: null,
  album_id: null,
  duration: null
})

const currentSongUrl = computed(() => {
  if (!currentSong.value?.file_url) return ''
  return `/api${currentSong.value.file_url}`
})

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入歌曲名称', trigger: 'blur' }
  ],
  duration: [
    { required: true, message: '请输入时长', trigger: 'blur' }
  ]
}

// 过滤歌曲
const filteredSongs = computed(() => {
  if (!searchKeyword.value) return songs.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return songs.value.filter(song => 
    song.title?.toLowerCase().includes(keyword) ||
    song.artist_name?.toLowerCase().includes(keyword) ||
    song.album_title?.toLowerCase().includes(keyword)
  )
})

const playableSongs = computed(() => {
  return filteredSongs.value.filter(song => song.file_url)
})

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 加载歌曲列表
const loadSongs = async () => {
  loading.value = true
  try {
    songs.value = await songsAPI.getAll()
  } catch (error) {
    console.error('加载歌曲失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载歌手列表
const loadArtists = async () => {
  try {
    artists.value = await artistsAPI.getAll()
  } catch (error) {
    console.error('加载歌手失败:', error)
  }
}

// 加载专辑列表
const loadAlbums = async () => {
  try {
    albums.value = await albumsAPI.getAll()
  } catch (error) {
    console.error('加载专辑失败:', error)
  }
}

const normalizeName = (val) => (val || '').trim()

const findArtistByName = (name) => {
  const key = normalizeName(name).toLowerCase()
  return artists.value.find(item => (item.name || '').trim().toLowerCase() === key)
}

const findAlbumByTitle = (title, artistId) => {
  const key = normalizeName(title).toLowerCase()
  return albums.value.find(item => {
    const sameTitle = (item.title || '').trim().toLowerCase() === key
    if (!sameTitle) return false
    if (artistId) return item.artist_id === artistId
    return true
  })
}

const ensureArtistByName = async (name) => {
  const artistName = normalizeName(name)
  if (!artistName) return null
  if (artists.value.length === 0) {
    await loadArtists()
  }
  const existing = findArtistByName(artistName)
  if (existing) return existing.artist_id

  try {
    await ElMessageBox.confirm(
      `未找到歌手“${artistName}”，是否添加？`,
      '提示',
      {
        confirmButtonText: '添加',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await artistsAPI.create({ name: artistName })
    await loadArtists()
    const created = findArtistByName(artistName)
    return created?.artist_id || null
  } catch {
    return null
  }
}

const ensureAlbumByTitle = async (title, artistId) => {
  const albumTitle = normalizeName(title)
  if (!albumTitle) return null
  if (albums.value.length === 0) {
    await loadAlbums()
  }
  const existing = findAlbumByTitle(albumTitle, artistId)
  if (existing) return existing.album_id

  try {
    await ElMessageBox.confirm(
      `未找到专辑“${albumTitle}”，是否添加？`,
      '提示',
      {
        confirmButtonText: '添加',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await albumsAPI.create({
      title: albumTitle,
      artist_id: artistId || null
    })
    await loadAlbums()
    const created = findAlbumByTitle(albumTitle, artistId)
    return created?.album_id || null
  } catch {
    return null
  }
}

// 添加歌曲
const handleAdd = () => {
  isEdit.value = false
  file.value = null
  formData.title = ''
  formData.artist_id = null
  formData.album_id = null
  formData.duration = null
  dialogVisible.value = true
}

// 编辑歌曲
const handleEdit = (row) => {
  isEdit.value = true
  formData.song_id = row.song_id
  formData.title = row.title
  formData.artist_id = row.artist_id
  formData.album_id = row.album_id
  formData.duration = row.duration
  dialogVisible.value = true
}

// 文件选择
const handleFileChange = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    file.value = files[0]
    // 自动填充标题
    if (!formData.title) {
      formData.title = file.value.name.replace(/\.[^/.]+$/, "")
    }

    // 自动读取音频时长（秒）
    try {
      const url = URL.createObjectURL(file.value)
      const audio = new Audio()
      audio.preload = 'metadata'
      audio.src = url
      audio.onloadedmetadata = () => {
        const dur = Number.isFinite(audio.duration) ? Math.round(audio.duration) : 0
        if (dur > 0) {
          formData.duration = dur
        } else {
          ElMessage.warning('无法自动识别时长，可手动填写')
        }
        URL.revokeObjectURL(url)
      }
      audio.onerror = () => {
        URL.revokeObjectURL(url)
        ElMessage.warning('读取音频信息失败，可手动填写时长')
      }
    } catch (err) {
      console.error('读取音频时长失败:', err)
      ElMessage.warning('读取音频信息失败，可手动填写时长')
    }
  }
}

const handlePlay = (row) => {
  ensurePlayerBarSafeArea()
  playerStore.setPlaylist(songs.value)
  playerStore.play(row)
}

const handlePlayAll = () => {
  const list = playableSongs.value
  if (list.length === 0) return
  ensurePlayerBarSafeArea()
  playerStore.setPlaylist(list)
  playerStore.play(list[0])
}

const getAudioDuration = (blob) => {
  return new Promise((resolve) => {
    try {
      const url = URL.createObjectURL(blob)
      const audio = new Audio()
      audio.preload = 'metadata'
      audio.src = url
      audio.onloadedmetadata = () => {
        const dur = Number.isFinite(audio.duration) ? Math.round(audio.duration) : 0
        URL.revokeObjectURL(url)
        resolve(dur)
      }
      audio.onerror = () => {
        URL.revokeObjectURL(url)
        resolve(0)
      }
    } catch {
      resolve(0)
    }
  })
}

const triggerBatchImport = () => {
  batchInputRef.value?.click()
}

const handleBatchFileChange = async (e) => {
  const files = Array.from(e.target.files || [])
  if (files.length === 0) return
  batchImporting.value = true
  let success = 0
  let failed = 0

  for (const f of files) {
    try {
      const metadata = await parseBlob(f).catch(() => null)
      const common = metadata?.common || {}
      const titleFromMeta = normalizeName(common.title)
      const artistFromMeta = normalizeName(common.artist || common.albumartist || (common.artists && common.artists[0]))
      const albumFromMeta = normalizeName(common.album)

      const title = titleFromMeta || f.name.replace(/\.[^/.]+$/, '')
      const artistId = artistFromMeta ? await ensureArtistByName(artistFromMeta) : null
      const albumId = albumFromMeta ? await ensureAlbumByTitle(albumFromMeta, artistId) : null

      const durationFromMeta = Number.isFinite(metadata?.format?.duration)
        ? Math.round(metadata.format.duration)
        : 0
      const duration = durationFromMeta || await getAudioDuration(f)

      const data = new FormData()
      data.append('file', f)
      data.append('title', title)
      if (artistId) data.append('artist_id', artistId)
      if (albumId) data.append('album_id', albumId)
      if (duration) data.append('duration', duration)

      await songsAPI.create(data)
      success += 1
    } catch (err) {
      console.error('批量导入失败:', err)
      failed += 1
    }
  }

  batchImporting.value = false
  e.target.value = ''
  loadSongs()
  loadArtists()
  loadAlbums()

  if (failed === 0) {
    ElMessage.success(`批量导入成功：${success} 首`)
  } else {
    ElMessage.warning(`导入完成：成功 ${success} 首，失败 ${failed} 首`)
  }
}

// 删除歌曲
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除歌曲《${row.title}》吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await songsAPI.delete(row.song_id)
      ElMessage.success('删除成功')
      loadSongs()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('应先删除歌单内的歌曲')
    }
  }).catch(() => {})
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (!isEdit.value && !file.value) {
        ElMessage.warning('请选择歌曲文件')
        return
      }

      submitLoading.value = true
      try {
        if (isEdit.value) {
          const data = {
            title: formData.title,
            artist_id: formData.artist_id,
            album_id: formData.album_id,
            duration: formData.duration
          }
          await songsAPI.update(formData.song_id, data)
          ElMessage.success('更新成功')
        } else {
          const data = new FormData()
          data.append('file', file.value)
          data.append('title', formData.title)
          if (formData.artist_id) data.append('artist_id', formData.artist_id)
          if (formData.album_id) data.append('album_id', formData.album_id)
          if (formData.duration !== null && formData.duration !== undefined) {
            data.append('duration', formData.duration)
          }
          
          await songsAPI.create(data)
          ElMessage.success('添加成功')
        }

        dialogVisible.value = false
        loadSongs()
      } catch (error) {
        console.error('提交失败:', error)
        ElMessage.error('提交失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  formData.song_id = null
  formData.title = ''
  formData.artist_id = null
  formData.album_id = null
  formData.duration = null
  file.value = null
  formRef.value?.resetFields()
}

// 预留给全局底部 PlayerBar 的高度（按你的 PlayerBar 实际高度微调）
const PLAYER_BAR_HEIGHT_PX = 88

const ensurePlayerBarSafeArea = () => {
  if (typeof window === 'undefined') return
  const docEl = document.documentElement

  const raw = getComputedStyle(docEl).getPropertyValue('--playerbar-height') || ''
  const existing = parseInt(raw, 10) || 0
  const h = Math.max(existing, PLAYER_BAR_HEIGHT_PX)

  docEl.style.setProperty('--playerbar-height', `${h}px`)
  // 关键：给 body 预留底部空间，避免 fixed 播放栏遮挡底部按钮（含 iPhone 安全区）
  document.body.style.paddingBottom = `calc(${h}px + env(safe-area-inset-bottom, 0px))`
}

// 初始化
onMounted(() => {
  ensurePlayerBarSafeArea()
  loadSongs()
  loadArtists()
  loadAlbums()
})
</script>

<style scoped>
.songs-container {
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

.songs-content {
  flex: 1;
  padding: 20px 30px;
  overflow: auto;
  padding-bottom: calc(var(--playerbar-height, 0px) + env(safe-area-inset-bottom, 0px));
}

.song-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.song-icon {
  font-size: 18px;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header th) {
  font-weight: 600;
}

:deep(.el-table__row) {
  cursor: pointer;
  transition: background 0.2s;
}

:deep(.el-table__row:hover) {
  background: #f5f7fa;
}

.file-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.audio-player {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #fff;
  border-top: 1px solid #e4e7ed;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
  z-index: 1000;
}

.player-info {
  display: flex;
  flex-direction: column;
  min-width: 150px;
}

.player-title {
  font-weight: 600;
  color: #303133;
}

.player-artist {
  font-size: 12px;
  color: #909399;
}

.html-audio {
  flex: 1;
  height: 40px;
}

.close-player {
  margin-left: 10px;
}
</style>