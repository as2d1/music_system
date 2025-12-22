<template>
  <div class="player-bar" v-if="playerStore.currentSong">
    <div class="song-info">
      <div class="cover-placeholder">
        <el-icon><Headset /></el-icon>
      </div>
      <div class="details">
        <div class="title">{{ playerStore.currentSong.title }}</div>
        <div class="artist">{{ playerStore.currentSong.artist_name || '未知歌手' }}</div>
      </div>
    </div>

    <div class="controls">
      <el-button circle text @click="playerStore.previous">
        <el-icon :size="20"><ArrowLeftBold /></el-icon>
      </el-button>
      
      <el-button circle type="primary" class="play-btn" @click="togglePlay">
        <el-icon :size="24">
          <VideoPause v-if="playerStore.isPlaying" />
          <VideoPlay v-else />
        </el-icon>
      </el-button>
      
      <el-button circle text @click="playerStore.next">
        <el-icon :size="20"><ArrowRightBold /></el-icon>
      </el-button>
    </div>

    <div class="progress-section">
      <audio 
        ref="audioRef" 
        :src="playerStore.currentSongUrl"
        @ended="playerStore.next"
        @timeupdate="handleTimeUpdate"
        @loadedmetadata="handleLoadedMetadata"
      ></audio>
      <span class="time">{{ formatTime(currentTime) }}</span>
      <el-slider 
        v-model="currentTime" 
        :max="duration" 
        @change="handleSeek"
        :show-tooltip="false"
        class="progress-slider"
      />
      <span class="time">{{ formatTime(duration) }}</span>
    </div>

    <div class="extra-controls">
      <el-button circle text @click="showPlaylist = !showPlaylist">
        <el-icon :size="20"><List /></el-icon>
      </el-button>
    </div>

    <!-- 播放列表抽屉 -->
    <el-drawer
      v-model="showPlaylist"
      title="播放列表"
      direction="rtl"
      size="300px"
    >
      <div class="playlist-items">
        <div 
          v-for="song in playerStore.playlist" 
          :key="song.song_id"
          class="playlist-item"
          :class="{ active: song.song_id === playerStore.currentSong.song_id }"
          @click="playerStore.play(song)"
        >
          <span class="item-title">{{ song.title }}</span>
          <span class="item-artist">{{ song.artist_name }}</span>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { usePlayerStore } from '@/stores/player'
import { VideoPlay, VideoPause, ArrowLeftBold, ArrowRightBold, Headset, List } from '@element-plus/icons-vue'

const playerStore = usePlayerStore()
const audioRef = ref(null)
const currentTime = ref(0)
const duration = ref(0)
const showPlaylist = ref(false)

// 监听播放状态
watch(() => playerStore.isPlaying, (newVal) => {
  nextTick(() => {
    if (newVal) {
      audioRef.value?.play().catch(e => console.warn('播放失败:', e))
    } else {
      audioRef.value?.pause()
    }
  })
})

// 监听歌曲切换
watch(() => playerStore.currentSong, (newVal) => {
  if (newVal) {
    currentTime.value = 0
    playerStore.isPlaying = true
    nextTick(() => {
      audioRef.value?.play().catch(e => console.warn('播放失败:', e))
    })
  }
})

const togglePlay = () => {
  if (playerStore.isPlaying) {
    playerStore.pause()
  } else {
    playerStore.play(playerStore.currentSong)
  }
}

const handleTimeUpdate = (e) => {
  currentTime.value = e.target.currentTime
}

const handleLoadedMetadata = (e) => {
  duration.value = e.target.duration
}

const handleSeek = (val) => {
  if (audioRef.value) {
    audioRef.value.currentTime = val
  }
}

const formatTime = (seconds) => {
  if (!seconds) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.player-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 80px;
  background: white;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  padding: 0 20px;
  z-index: 1000;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
}

.song-info {
  width: 200px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.cover-placeholder {
  width: 50px;
  height: 50px;
  background: #f5f5f5;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

.details {
  overflow: hidden;
}

.title {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.artist {
  font-size: 12px;
  color: #666;
}

.controls {
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 0 30px;
}

.play-btn {
  width: 45px;
  height: 45px;
}

.progress-section {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 15px;
}

.time {
  font-size: 12px;
  color: #999;
  width: 40px;
}

.progress-slider {
  flex: 1;
}

.extra-controls {
  width: 100px;
  display: flex;
  justify-content: flex-end;
}

.playlist-item {
  padding: 10px;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 5px;
}

.playlist-item:hover {
  background: #f5f5f5;
}

.playlist-item.active {
  color: #409EFF;
  background: #ecf5ff;
}

.item-title {
  font-size: 14px;
  display: block;
}

.item-artist {
  font-size: 12px;
  color: #999;
}
</style>
