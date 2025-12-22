<template>
  <div class="login-wrapper">
    <div class="login-box">
      <!-- 左侧装饰区域 -->
      <div class="login-left">
        <!-- 动态波纹背景 -->
        <div class="waves-container">
          <div class="wave wave-1"></div>
          <div class="wave wave-2"></div>
          <div class="wave wave-3"></div>
        </div>

        <div class="brand-header">
          <el-icon :size="24"><Headset /></el-icon>
          <span class="brand-text">MUSIC CORE</span>
        </div>
        
        <div class="illustration-container">
          <!-- 模拟图中的插画效果 -->
          <div class="illustration-content">
            <el-icon :size="120" class="main-icon"><Monitor /></el-icon>
            <div class="floating-card card-1">
              <el-icon><VideoPlay /></el-icon>
            </div>
            <div class="floating-card card-2">
              <el-icon><Files /></el-icon>
            </div>
            <!-- 装饰性音符 -->
            <div class="music-note note-1">♪</div>
            <div class="music-note note-2">♫</div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区域 -->
      <div class="login-right">
        <!-- 背景特效 -->
        <div class="right-bg-effects">
          <div class="bg-wave w1"></div>
          <div class="bg-wave w2"></div>
          <div class="floating-lyric l1">Music is life</div>
          <div class="floating-lyric l2">Feel the rhythm</div>
          <div class="floating-lyric l3">Dance to the beat</div>
          <div class="floating-lyric l4">Sound of silence</div>
        </div>

        <div class="form-content">
          <h2 class="form-title">{{ isRegister ? 'Create Account' : 'Log in' }}</h2>
          
          <el-form 
            :model="loginForm" 
            :rules="rules" 
            ref="loginFormRef" 
            class="login-form"
            label-position="top"
            hide-required-asterisk
          >
            <el-form-item label="Username" prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="Enter your username"
                size="large"
              />
            </el-form-item>

            <el-form-item label="Password" prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="Enter your password"
                size="large"
                show-password
                @keyup.enter="handleSubmit"
              />
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe" label="Remember me" />
              <el-link type="primary" :underline="false" class="forgot-pwd">Forgot your password?</el-link>
            </div>

            <el-button
              type="primary"
              size="large"
              class="submit-btn"
              :loading="loading"
              @click="handleSubmit"
            >
              {{ isRegister ? 'Sign Up' : 'Login' }}
            </el-button>

            <div class="toggle-mode">
              <span>{{ isRegister ? 'Already have an account?' : 'Don\'t have an account?' }}</span>
              <el-link type="primary" @click="toggleMode" :underline="false" class="toggle-link">
                {{ isRegister ? 'Log in' : 'Sign up' }}
              </el-link>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Monitor, VideoPlay, Files, Headset } from '@element-plus/icons-vue'
import { authAPI } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const isRegister = ref(false)
const loading = ref(false)
const rememberMe = ref(false)
const loginFormRef = ref(null)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: 'Please enter username', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ]
}

const toggleMode = () => {
  isRegister.value = !isRegister.value
  loginFormRef.value?.resetFields()
}

const handleSubmit = async () => {
  try {
    await loginFormRef.value?.validate()
    loading.value = true

    if (isRegister.value) {
      await authAPI.register(loginForm)
      ElMessage.success('Registration successful! Please login.')
      isRegister.value = false
      loginForm.password = ''
    } else {
      const res = await authAPI.login(loginForm)
      console.log('Login Response:', res)
      if (res.token) {
        userStore.setToken(res.token)
        userStore.setUserInfo(res.user)
        ElMessage.success('Login successful!')
        router.push('/')
      } else {
        console.error('No token in login response')
        ElMessage.error('Login failed: No token received')
      }
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 登录页不应受主界面 PlayerBar / Sidebar 的全局偏移影响
  document.documentElement.style.setProperty('--app-sidebar-width', '0px')
  document.documentElement.style.setProperty('--playerbar-height', '0px')
  document.body.style.paddingBottom = ''
})
</script>

<style scoped>
.login-wrapper {
  font-family: "Noto Sans SC", "Microsoft YaHei", sans-serif;
  min-height: 100vh;
  background-color: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-box {
  width: 1000px;
  height: 600px;
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  display: flex;
  overflow: hidden;
}

/* Left Side */
.login-left {
  width: 45%;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  padding: 40px;
  display: flex;
  flex-direction: column;
  position: relative;
  color: white;
  overflow: hidden;
}

.waves-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.wave {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: ripple 8s linear infinite;
}

.wave-1 { width: 300px; height: 300px; animation-delay: 0s; }
.wave-2 { width: 500px; height: 500px; animation-delay: -2.5s; }
.wave-3 { width: 700px; height: 700px; animation-delay: -5s; }

@keyframes ripple {
  0% {
    width: 0;
    height: 0;
    opacity: 0.8;
    border-width: 2px;
  }
  100% {
    width: 1000px;
    height: 1000px;
    opacity: 0;
    border-width: 0;
  }
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  z-index: 10;
}

.illustration-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 10;
}

.illustration-content {
  position: relative;
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.music-note {
  position: absolute;
  color: rgba(255, 255, 255, 0.6);
  font-size: 24px;
  animation: floatNote 4s ease-in-out infinite;
}

.note-1 { top: 20%; left: 20%; animation-delay: 0s; }
.note-2 { bottom: 30%; right: 20%; animation-delay: -2s; }

@keyframes floatNote {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(10deg); }
}

.main-icon {
  filter: drop-shadow(0 10px 20px rgba(0,0,0,0.2));
}

.floating-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-1 {
  top: 20%;
  right: 10%;
  width: 60px;
  height: 60px;
  font-size: 24px;
  animation: float 6s ease-in-out infinite;
}

.card-2 {
  bottom: 20%;
  left: 10%;
  width: 50px;
  height: 50px;
  font-size: 20px;
  animation: float 8s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

/* Right Side */
.login-right {
  flex: 1;
  padding: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #fff;
  position: relative;
  overflow: hidden;
}

.right-bg-effects {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.bg-wave {
  position: absolute;
  border-radius: 40% 45% 40% 45%;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(37, 99, 235, 0.02) 100%);
  animation: spinWave 15s linear infinite;
}

.w1 {
  width: 600px;
  height: 600px;
  top: -200px;
  right: -100px;
  animation-duration: 20s;
}

.w2 {
  width: 500px;
  height: 500px;
  bottom: -100px;
  left: -100px;
  animation-direction: reverse;
  animation-duration: 15s;
}

@keyframes spinWave {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.floating-lyric {
  position: absolute;
  font-size: 1.8rem;
  font-weight: 800;
  color: rgba(0, 0, 0, 0.04);
  white-space: nowrap;
  font-family: 'Georgia', serif;
  font-style: italic;
  user-select: none;
}

.l1 { top: 15%; left: 10%; animation: floatLyric 20s ease-in-out infinite; }
.l2 { top: 25%; right: 5%; animation: floatLyric 25s ease-in-out infinite reverse; }
.l3 { bottom: 30%; left: 15%; animation: floatLyric 22s ease-in-out infinite; }
.l4 { bottom: 15%; right: 10%; animation: floatLyric 28s ease-in-out infinite reverse; }

@keyframes floatLyric {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

.form-content {
  max-width: 400px;
  width: 100%;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.form-title {
  font-size: 28px;
  color: #1a1a1a;
  margin-bottom: 40px;
  font-weight: 600;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #374151;
  padding-bottom: 8px;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #e5e7eb inset;
  padding: 8px 12px;
  border-radius: 8px;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #2563eb inset;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  background-color: #2563eb;
  border-color: #2563eb;
  margin-bottom: 24px;
}

.submit-btn:hover {
  background-color: #1d4ed8;
  border-color: #1d4ed8;
}

.toggle-mode {
  text-align: center;
  font-size: 14px;
  color: #6b7280;
}

.toggle-link {
  margin-left: 5px;
  font-weight: 500;
  color: #2563eb;
}

.toggle-link:hover {
  color: #1d4ed8;
}

/* Responsive */
@media (max-width: 900px) {
  .login-box {
    flex-direction: column;
    height: auto;
    width: 100%;
    max-width: 500px;
  }

  .login-left {
    display: none;
  }

  .login-right {
    padding: 40px;
  }
}
</style>