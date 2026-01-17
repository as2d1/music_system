import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(error.response?.data?.error || '请求失败')
    }
    return Promise.reject(error)
  }
)

// API 方法
export const authAPI = {
  login: (data) => request.post('/auth/login', data),
  register: (data) => request.post('/auth/register', data)
}

export const songsAPI = {
  // Flask 蓝图里集合路由是 '/'，不带尾随 '/' 会触发 308 重定向，可能导致 Authorization 头丢失
  getAll: () => request.get('/songs/'),
  getOne: (id) => request.get(`/songs/${id}`),
  create: (data) => {
    // 如果是 FormData，让 axios 自动设置 Content-Type
    if (data instanceof FormData) {
      return request.post('/songs/', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    return request.post('/songs/', data)
  },
  update: (id, data) => request.put(`/songs/${id}`, data),
  delete: (id) => request.delete(`/songs/${id}`)
}

export const artistsAPI = {
  getAll: () => request.get('/artists/'),
  getOne: (id) => request.get(`/artists/${id}`),
  create: (data) => request.post('/artists/', data),
  update: (id, data) => request.put(`/artists/${id}`, data),
  delete: (id) => request.delete(`/artists/${id}`)
}

export const albumsAPI = {
  getAll: () => request.get('/albums/'),
  getOne: (id) => request.get(`/albums/${id}`),
  create: (data) => request.post('/albums/', data),
  update: (id, data) => request.put(`/albums/${id}`, data),
  delete: (id) => request.delete(`/albums/${id}`)
}

export const playlistsAPI = {
  getAll: (userId) => request.get('/playlists/', { params: { user_id: userId } }),
  getOne: (id) => request.get(`/playlists/${id}`),
  create: (data) => request.post('/playlists/', data),
  delete: (id) => request.delete(`/playlists/${id}`),
  addSong: (playlistId, songId) => request.post(`/playlists/${playlistId}/songs`, { song_id: songId }),
  removeSong: (playlistId, songId) => request.delete(`/playlists/${playlistId}/songs/${songId}`)
}

export default request
