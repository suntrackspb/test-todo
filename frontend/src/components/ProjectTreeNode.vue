<script setup>
import { ref } from 'vue'

const props = defineProps({
  node: { type: Object, required: true },
  selectedId: { type: [Number, null], default: null },
})

const emit = defineEmits(['select', 'create-child', 'rename', 'delete'])

const expanded = ref(true)

function toggle() {
  expanded.value = !expanded.value
}

function rename() {
  const title = prompt('Новое название проекта', props.node.title)
  if (title && title.trim()) emit('rename', props.node.id, title.trim())
}

function createChild() {
  const title = prompt('Название нового вложенного проекта')
  if (title && title.trim()) emit('create-child', props.node.id, title.trim())
}

function remove() {
  if (confirm(`Удалить проект "${props.node.title}" вместе со всем содержимым?`)) {
    emit('delete', props.node.id)
  }
}
</script>

<template>
  <li class="tree-node">
    <div class="row" :class="{ active: selectedId === node.id }">
      <button
        v-if="node.children.length"
        class="toggle"
        type="button"
        @click="toggle"
        :aria-label="expanded ? 'Свернуть' : 'Развернуть'"
      >
        {{ expanded ? '▾' : '▸' }}
      </button>
      <span v-else class="toggle-spacer" />
      <span class="title" @click="emit('select', node.id)">{{ node.title }}</span>
      <span class="actions">
        <button type="button" title="Новый подпроект" @click="createChild">+</button>
        <button type="button" title="Переименовать" @click="rename">✎</button>
        <button type="button" title="Удалить" @click="remove">✕</button>
      </span>
    </div>
    <ul v-if="expanded && node.children.length" class="children">
      <ProjectTreeNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :selected-id="selectedId"
        @select="(id) => emit('select', id)"
        @create-child="(...args) => emit('create-child', ...args)"
        @rename="(...args) => emit('rename', ...args)"
        @delete="(...args) => emit('delete', ...args)"
      />
    </ul>
  </li>
</template>

<style scoped>
.tree-node {
  list-style: none;
}

.row {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 6px;
  border-radius: 6px;
  cursor: default;
}

.row:hover {
  background: var(--hover-bg);
}

.row.active {
  background: var(--active-bg);
}

.toggle,
.toggle-spacer {
  width: 16px;
  border: none;
  background: none;
  padding: 0;
  font-size: 11px;
}

.title {
  flex: 1;
  cursor: pointer;
  font-size: 14px;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.actions {
  display: none;
  gap: 2px;
}

.row:hover .actions {
  display: flex;
}

.actions button {
  border: none;
  background: none;
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 4px;
}

.actions button:hover {
  background: var(--border);
}

.children {
  margin: 0;
  padding-left: 16px;
}
</style>
