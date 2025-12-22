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
              @click="handleEdit(artist)"
              :icon="Edit"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              text
              @click="handleDelete(artist)"
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, User } from '@element-plus/icons-vue'
import { artistsAPI } from '@/api'

const artists = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const searchKeyword = ref('')
const formRef = ref(null)

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
</style>