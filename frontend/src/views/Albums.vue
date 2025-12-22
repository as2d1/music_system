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
              @click="handleEdit(album)"
              :icon="Edit"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(album)"
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Collection, User } from '@element-plus/icons-vue'
import { albumsAPI, artistsAPI } from '@/api'

const albums = ref([])
const artists = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const searchKeyword = ref('')
const formRef = ref(null)

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
})
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
</style>