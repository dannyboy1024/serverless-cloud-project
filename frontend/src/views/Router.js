import Vue from 'vue'
import VueRouter from 'vue-router'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

Vue.use(VueRouter)
Vue.use(ElementUI)

const routes = [
    {
        path: '/',
        name: 'Login',
        component: () => import('./LoginPage.vue')
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('./MainPage.vue')
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('./RegisterPage.vue')
    },
    {
        path:'/album/',
        name:'AlbumPhotos',
        component: () => import('./AlbumPhotos.vue')
    },
    {
        path:'/index',
        name:'Index',
        component: () => import('./IndexPage.vue')
    }
]
const router = new VueRouter({
    mode: 'hash',
    base: process.env.BASE_URL,
    routes
})

export default router