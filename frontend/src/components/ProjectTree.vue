<script setup>
import { onMounted } from 'vue'
import { useProjectsStore } from '@/stores/projects'
import ProjectTreeNode from './ProjectTreeNode.vue'

const store = useProjectsStore()

onMounted(() => {
  store.fetchTree()
})

async function createRootProject() {
  const title = prompt('Название нового проекта')
  if (title && title.trim()) {
    await store.createProject({ title: title.trim() })
  }
}

async function createChild(parentId, title) {
  await store.createProject({ title, parentId })
}

async function rename(id, title) {
  await store.renameProject(id, title)
}

async function remove(id) {
  await store.deleteProject(id)
}

function select(id) {
  store.selectProject(id)
}
</script>

<template>
  <div class="project-tree">
    <div class="header">
      <span>Проекты</span>
      <button type="button" @click="createRootProject">+ Новый</button>
    </div>
    <ul class="root-list">
      <ProjectTreeNode
        v-for="node in store.tree"
        :key="node.id"
        :node="node"
        :selected-id="store.selectedProjectId"
        @select="select"
        @create-child="createChild"
        @rename="rename"
        @delete="remove"
      />
    </ul>
    <p v-if="!store.tree.length" class="empty">Пока нет проектов</p>
  </div>
</template>

<style scoped>
.project-tree {
  padding: 12px 8px;
  height: 100%;
  overflow-y: auto;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4px 8px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
}

.header button {
  border: none;
  background: none;
  font-size: 12px;
  color: var(--link);
}

.root-list {
  margin: 0;
  padding: 0;
}

.empty {
  padding: 8px;
  font-size: 13px;
  color: var(--faint);
}
</style>
