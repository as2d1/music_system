import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'

export const usePlayerStore = defineStore('player', () => {
  const currentSong = ref(null)
  const playlist = ref([])
  const isPlaying = ref(false)
  const currentIndex = ref(-1)

  const normalizeToApiUrl = (fileUrl) => {
    if (!fileUrl) return ''

    // If backend returns absolute URL, strip origin and keep pathname.
    if (typeof fileUrl === 'string' && fileUrl.startsWith('http')) {
      try {
        fileUrl = new URL(fileUrl).pathname
      } catch {
        // ignore
      }
    }

    // Always go through Vite proxy (/api -> backend)
    if (fileUrl.startsWith('/api/')) return fileUrl
    if (fileUrl.startsWith('/uploads/')) return `/api${fileUrl}`

    return fileUrl
  }

  const appendToken = (url) => {
    if (!url) return ''
    if (!url.startsWith('/api/songs/') || !url.includes('/stream')) return url

    const userStore = useUserStore()
    const token = userStore.token
    if (!token) return url

    const sep = url.includes('?') ? '&' : '?'
    return `${url}${sep}token=${encodeURIComponent(token)}`
  }

  const currentSongUrl = computed(() => {
    if (!currentSong.value) return ''
    return appendToken(normalizeToApiUrl(currentSong.value.file_url))
  })

  const setPlaylist = (songs) => {
    console.log('设置播放列表:', songs)
    playlist.value = songs
  }

  const play = (song) => {
    console.log('播放歌曲:', song)
    currentSong.value = song
    
    // 找到歌曲在播放列表中的索引
    const index = playlist.value.findIndex(s => s.song_id === song.song_id)
    if (index !== -1) {
      currentIndex.value = index
    }
    
    isPlaying.value = true
  }

  const pause = () => {
    console.log('暂停播放')
    isPlaying.value = false
  }

  const togglePlay = () => {
    console.log('切换播放状态')
    isPlaying.value = !isPlaying.value
  }

  const next = () => {
    console.log('下一曲')
    if (playlist.value.length === 0) return
    
    currentIndex.value = (currentIndex.value + 1) % playlist.value.length
    play(playlist.value[currentIndex.value])
  }

  const previous = () => {
    console.log('上一曲')
    if (playlist.value.length === 0) return
    
    currentIndex.value = currentIndex.value <= 0 
      ? playlist.value.length - 1 
      : currentIndex.value - 1
    play(playlist.value[currentIndex.value])
  }

  return {
    currentSong,
    currentSongUrl,
    playlist,
    isPlaying,
    currentIndex,
    setPlaylist,
    play,
    pause,
    togglePlay,
    next,
    previous
  }
})
