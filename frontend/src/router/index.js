import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true },
    redirect: '/songs',
    children: [
      {
        path: 'songs',
        name: 'Songs',
        component: () => import('@/views/Songs.vue')
      },
      {
        path: 'artists',
        name: 'Artists',
        component: () => import('@/views/Artists.vue')
      },
      {
        path: 'albums',
        name: 'Albums',
        component: () => import('@/views/Albums.vue')
      },
      {
        path: 'playlists',
        name: 'Playlists',
        component: () => import('@/views/Playlists.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
