<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProjectsStore } from '@/stores/projects'
import { useThemeStore } from '@/stores/theme'
import ProjectTree from '@/components/ProjectTree.vue'

const auth = useAuthStore()
const projects = useProjectsStore()
const theme = useThemeStore()
const router = useRouter()
const route = useRoute()

const sidebarOpen = ref(false)

watch(route, () => {
  sidebarOpen.value = false
})

watch(
  () => projects.selectedProjectId,
  () => {
    sidebarOpen.value = false
  },
)

const currentProjectTitle = computed(() => {
  function find(nodes) {
    for (const node of nodes) {
      if (node.id === projects.selectedProjectId) return node.title
      const found = find(node.children)
      if (found) return found
    }
    return null
  }
  return find(projects.tree) || 'Выберите проект'
})

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="workspace">
    <div v-if="sidebarOpen" class="sidebar-backdrop" @click="sidebarOpen = false"></div>
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <ProjectTree />
    </aside>
    <div class="main">
      <header class="topbar">
        <button type="button" class="burger" @click="sidebarOpen = !sidebarOpen" aria-label="Проекты">☰</button>
        <div class="project-title">{{ currentProjectTitle }}</div>
        <nav class="tabs">
          <router-link :to="{ name: 'notes' }">Заметки</router-link>
          <router-link :to="{ name: 'todos' }">Задачи</router-link>
          <router-link :to="{ name: 'calendar' }">Календарь</router-link>
        </nav>
        <div class="user">
          <button type="button" class="theme-toggle" :title="theme.theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'" @click="theme.toggle()">
            {{ theme.theme === 'dark' ? '☀️' : '🌙' }}
          </button>
          <span class="user-name">{{ auth.user?.display_name }}</span>
          <button type="button" @click="logout">Выйти</button>
        </div>
      </header>
      <section class="content">
        <router-view />
      </section>
    </div>
  </div>
</template>

<style scoped>
.workspace {
  height: 100%;
  display: flex;
}

.sidebar {
  width: 260px;
  flex-shrink: 0;
  background: var(--surface);
  border-right: 1px solid var(--border);
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}

.project-title {
  font-weight: 600;
  color: var(--text);
}

.tabs {
  display: flex;
  gap: 16px;
  flex: 1;
}

.tabs a {
  text-decoration: none;
  color: var(--muted);
  font-size: 14px;
  padding: 4px 0;
  border-bottom: 2px solid transparent;
}

.tabs a.router-link-active {
  color: var(--link);
  border-bottom-color: var(--link);
}

.user {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text);
}

.theme-toggle {
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 14px;
  line-height: 1;
}

.user button:not(.theme-toggle) {
  border: none;
  background: none;
  color: var(--danger);
  font-size: 13px;
}

.content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.burger {
  display: none;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 16px;
  line-height: 1;
}

.sidebar-backdrop {
  display: none;
}

@media (max-width: 720px) {
  .burger {
    display: block;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 40;
    width: 80vw;
    max-width: 300px;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.2);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    background: var(--overlay);
    z-index: 30;
  }

  .topbar {
    gap: 12px;
    padding: 10px 12px;
    flex-wrap: wrap;
  }

  .project-title {
    order: 1;
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 14px;
  }

  .tabs {
    order: 3;
    flex-basis: 100%;
    gap: 12px;
  }

  .user {
    order: 2;
  }

  .user-name {
    display: none;
  }

  .content {
    padding: 12px;
  }
}
</style>
