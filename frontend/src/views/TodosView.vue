<script setup>
import { computed, ref, watch } from 'vue'
import { useProjectsStore } from '@/stores/projects'
import { useTodosStore } from '@/stores/todos'
import { PRIORITIES, priorityMeta } from '@/constants/priority'

const STATUSES = [
  { value: 'todo', label: 'К выполнению' },
  { value: 'in_progress', label: 'В работе' },
  { value: 'done', label: 'Готово' },
]

const projectsStore = useProjectsStore()
const todosStore = useTodosStore()

const projectId = computed(() => projectsStore.selectedProjectId)
const rawTodos = computed(() => todosStore.todosByProject[projectId.value] || [])

function todayIso() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const newTitle = ref('')
const newDueDate = ref('')
const newPriority = ref('none')
const statusFilter = ref('')
const dateFrom = ref(todayIso())
const dateTo = ref('')
const sortOrder = ref('asc')
const editingId = ref(null)
const editTitle = ref('')
const editDueDate = ref('')
const editPriority = ref('none')

function sortByDate(list) {
  const dir = sortOrder.value === 'asc' ? 1 : -1
  return [...list].sort((a, b) => {
    if (!a.due_date && !b.due_date) return 0
    if (!a.due_date) return 1
    if (!b.due_date) return -1
    return a.due_date < b.due_date ? -dir : a.due_date > b.due_date ? dir : 0
  })
}

const filteredTodos = computed(() => {
  let list = rawTodos.value
  if (dateFrom.value) list = list.filter((t) => !t.due_date || t.due_date >= dateFrom.value)
  if (dateTo.value) list = list.filter((t) => !t.due_date || t.due_date <= dateTo.value)
  return list
})

const todos = computed(() => sortByDate(filteredTodos.value.filter((t) => t.status !== 'done')))
const doneTodos = computed(() => sortByDate(filteredTodos.value.filter((t) => t.status === 'done')))

function toggleSortOrder() {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

function clearDateFilter() {
  dateFrom.value = ''
  dateTo.value = ''
}

async function load() {
  if (projectId.value) await todosStore.fetchTodos(projectId.value, statusFilter.value || null)
}

watch(projectId, load, { immediate: true })
watch(statusFilter, load)

async function addTodo() {
  if (!newTitle.value.trim()) return
  await todosStore.createTodo(projectId.value, {
    title: newTitle.value.trim(),
    due_date: newDueDate.value || null,
    priority: newPriority.value,
  })
  newTitle.value = ''
  newDueDate.value = ''
  newPriority.value = 'none'
}

async function changeStatus(todo, status) {
  await todosStore.updateTodo(todo.id, projectId.value, { status })
}

async function removeTodo(todo) {
  await todosStore.deleteTodo(todo.id, projectId.value)
}

function startEdit(todo) {
  editingId.value = todo.id
  editTitle.value = todo.title
  editDueDate.value = todo.due_date || ''
  editPriority.value = todo.priority || 'none'
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(todo) {
  const title = editTitle.value.trim()
  if (!title) return
  await todosStore.updateTodo(todo.id, projectId.value, {
    title,
    due_date: editDueDate.value || null,
    clear_due_date: !editDueDate.value,
    priority: editPriority.value,
  })
  editingId.value = null
}
</script>

<template>
  <div v-if="!projectId" class="placeholder">Выберите проект слева, чтобы увидеть задачи</div>
  <div v-else class="todos">
    <form class="new-todo" @submit.prevent="addTodo">
      <input v-model="newTitle" type="text" placeholder="Новая задача" />
      <input v-model="newDueDate" type="date" />
      <select v-model="newPriority" class="priority-select">
        <option v-for="p in PRIORITIES" :key="p.value" :value="p.value">{{ p.label }}</option>
      </select>
      <button type="submit">Добавить</button>
    </form>

    <div class="filter">
      <label>Статус:</label>
      <select v-model="statusFilter">
        <option value="">Все</option>
        <option v-for="s in STATUSES" :key="s.value" :value="s.value">{{ s.label }}</option>
      </select>

      <label>Дата:</label>
      <input v-model="dateFrom" type="date" />
      <span class="date-sep">—</span>
      <input v-model="dateTo" type="date" />
      <button v-if="dateFrom || dateTo" type="button" class="clear-date" @click="clearDateFilter">✕</button>

      <button type="button" class="sort-toggle" @click="toggleSortOrder">
        Дата {{ sortOrder === 'asc' ? '↑' : '↓' }}
      </button>
    </div>

    <ul class="todo-list">
      <li v-for="todo in todos" :key="todo.id" :class="`status-${todo.status}`">
        <template v-if="editingId === todo.id">
          <input v-model="editTitle" type="text" class="edit-title" @keyup.enter="saveEdit(todo)" @keyup.esc="cancelEdit" />
          <input v-model="editDueDate" type="date" class="edit-due" />
          <select v-model="editPriority" class="priority-select">
            <option v-for="p in PRIORITIES" :key="p.value" :value="p.value">{{ p.label }}</option>
          </select>
          <button type="button" class="save" @click="saveEdit(todo)">Сохранить</button>
          <button type="button" class="cancel" @click="cancelEdit">Отмена</button>
        </template>
        <template v-else>
          <span class="priority-dot" :style="{ background: priorityMeta(todo.priority).color }" :title="priorityMeta(todo.priority).label"></span>
          <select :value="todo.status" @change="changeStatus(todo, $event.target.value)">
            <option v-for="s in STATUSES" :key="s.value" :value="s.value">{{ s.label }}</option>
          </select>
          <span class="title">{{ todo.title }}</span>
          <span v-if="todo.due_date" class="due">до {{ todo.due_date }}</span>
          <button type="button" class="edit" @click="startEdit(todo)">✎</button>
          <button type="button" class="delete" @click="removeTodo(todo)">✕</button>
        </template>
      </li>
    </ul>
    <p v-if="!todos.length" class="empty">Задач пока нет</p>

    <div class="done-section">
      <h3 class="done-heading">Выполнено ({{ doneTodos.length }})</h3>
      <ul v-if="doneTodos.length" class="todo-list done-list">
        <li v-for="todo in doneTodos" :key="todo.id" :class="`status-${todo.status}`">
          <template v-if="editingId === todo.id">
            <input v-model="editTitle" type="text" class="edit-title" @keyup.enter="saveEdit(todo)" @keyup.esc="cancelEdit" />
            <input v-model="editDueDate" type="date" class="edit-due" />
            <select v-model="editPriority" class="priority-select">
              <option v-for="p in PRIORITIES" :key="p.value" :value="p.value">{{ p.label }}</option>
            </select>
            <button type="button" class="save" @click="saveEdit(todo)">Сохранить</button>
            <button type="button" class="cancel" @click="cancelEdit">Отмена</button>
          </template>
          <template v-else>
            <span class="priority-dot" :style="{ background: priorityMeta(todo.priority).color }" :title="priorityMeta(todo.priority).label"></span>
            <select :value="todo.status" @change="changeStatus(todo, $event.target.value)">
              <option v-for="s in STATUSES" :key="s.value" :value="s.value">{{ s.label }}</option>
            </select>
            <span class="title">{{ todo.title }}</span>
            <span v-if="todo.due_date" class="due">до {{ todo.due_date }}</span>
            <button type="button" class="edit" @click="startEdit(todo)">✎</button>
            <button type="button" class="delete" @click="removeTodo(todo)">✕</button>
          </template>
        </li>
      </ul>
      <p v-else class="empty">Пока ничего не выполнено</p>
    </div>
  </div>
</template>

<style scoped>
.placeholder {
  color: var(--faint);
  padding: 40px;
  text-align: center;
}

.todos {
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--border);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.new-todo {
  display: flex;
  gap: 8px;
}

.new-todo input[type='text'] {
  flex: 1;
}

.new-todo input,
.new-todo button,
.filter select {
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
}

.new-todo button {
  background: var(--button-primary-bg);
  color: var(--button-primary-text);
  border: none;
}

.filter {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text);
  flex-wrap: wrap;
}

.filter input[type='date'] {
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
}

.date-sep {
  color: var(--muted);
}

.clear-date,
.sort-toggle {
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
  background: var(--surface);
  color: var(--text);
}

.sort-toggle {
  margin-left: auto;
}

.todo-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.todo-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid var(--border-light);
}

.status-done .title {
  text-decoration: line-through;
  color: var(--faint);
}

.title {
  flex: 1;
  font-size: 14px;
  color: var(--text);
}

.due {
  font-size: 12px;
  color: var(--muted);
}

.delete,
.edit {
  border: none;
  background: none;
  color: var(--faint);
}

.edit-title {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
}

.edit-due {
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
}

.save,
.cancel {
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
  background: var(--surface);
  color: var(--text);
}

.save {
  background: var(--button-primary-bg);
  color: var(--button-primary-text);
  border: none;
}

.empty {
  font-size: 13px;
  color: var(--faint);
}

.priority-select {
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
}

.priority-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.done-section {
  border-top: 1px solid var(--border-light);
  padding-top: 12px;
}

.done-heading {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
}

.done-list {
  opacity: 0.75;
}

@media (max-width: 720px) {
  .new-todo {
    flex-wrap: wrap;
  }

  .new-todo input[type='text'] {
    flex-basis: 100%;
  }

  .todo-list li {
    flex-wrap: wrap;
  }

  .title {
    flex-basis: 100%;
    order: -1;
  }

  .edit-title,
  .edit-due {
    flex-basis: 100%;
  }

  .filter input[type='date'] {
    flex: 1;
    min-width: 0;
  }

  .sort-toggle {
    margin-left: 0;
    flex-basis: 100%;
  }
}
</style>
