<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { fetchCalendarRange } from '@/api/calendar'
import { useProjectsStore } from '@/stores/projects'
import { useNotesStore } from '@/stores/notes'
import { priorityMeta } from '@/constants/priority'

const WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
const MAX_VISIBLE = 3
const STATUS_ICONS = { todo: '☐', in_progress: '◐' }

const router = useRouter()
const projectsStore = useProjectsStore()
const notesStore = useNotesStore()

const today = new Date()
const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth()) // 0-based
const calendarData = ref({ todos: [], notes: [] })
const expandedDay = ref(null)
const popoverPos = ref({ top: 0, left: 0 })
const scope = ref('all')

const currentProjectTitle = computed(() => {
  function find(nodes) {
    for (const node of nodes) {
      if (node.id === projectsStore.selectedProjectId) return node.title
      const found = find(node.children)
      if (found) return found
    }
    return null
  }
  return find(projectsStore.tree)
})

function pad(n) {
  return String(n).padStart(2, '0')
}

function isoDate(year, month, day) {
  return `${year}-${pad(month + 1)}-${pad(day)}`
}

const monthLabel = computed(() => {
  const date = new Date(currentYear.value, currentMonth.value, 1)
  return date.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })
})

const days = computed(() => {
  const firstOfMonth = new Date(currentYear.value, currentMonth.value, 1)
  const daysInMonth = new Date(currentYear.value, currentMonth.value + 1, 0).getDate()
  // JS getDay(): 0=Sunday..6=Saturday. Convert to Monday-first index.
  const leadingBlanks = (firstOfMonth.getDay() + 6) % 7

  const cells = []
  for (let i = 0; i < leadingBlanks; i++) cells.push(null)
  for (let day = 1; day <= daysInMonth; day++) cells.push(day)
  return cells
})

const itemsByDate = computed(() => {
  const map = {}
  for (const todo of calendarData.value.todos) {
    ;(map[todo.due_date] ??= { todos: [], notes: [] }).todos.push(todo)
  }
  for (const note of calendarData.value.notes) {
    ;(map[note.due_date] ??= { todos: [], notes: [] }).notes.push(note)
  }
  return map
})

function dayItems(day) {
  const key = isoDate(currentYear.value, currentMonth.value, day)
  const entry = itemsByDate.value[key] || { todos: [], notes: [] }
  return [
    ...entry.todos.map((todo) => ({ kind: 'todo', data: todo })),
    ...entry.notes.map((note) => ({ kind: 'note', data: note })),
  ]
}

function visibleItems(day) {
  return dayItems(day).slice(0, MAX_VISIBLE)
}

function overflowCount(day) {
  return Math.max(0, dayItems(day).length - MAX_VISIBLE)
}

function toggleExpanded(day, evt) {
  if (expandedDay.value === day) {
    expandedDay.value = null
    return
  }
  const rect = evt.currentTarget.closest('.day-cell').getBoundingClientRect()
  const popoverWidth = 200
  popoverPos.value = {
    top: rect.bottom + 4,
    left: Math.min(rect.right - popoverWidth, window.innerWidth - popoverWidth - 8),
  }
  expandedDay.value = day
}

function goToItem(item) {
  expandedDay.value = null
  if (item.kind === 'todo') return goToTodo(item.data)
  return goToNote(item.data)
}

async function load() {
  const from = isoDate(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0).getDate()
  const to = isoDate(currentYear.value, currentMonth.value, lastDay)
  const projectId = scope.value === 'project' ? projectsStore.selectedProjectId : null
  calendarData.value = await fetchCalendarRange(from, to, projectId)
}

function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value -= 1
  } else {
    currentMonth.value -= 1
  }
}

function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value += 1
  } else {
    currentMonth.value += 1
  }
}

watch([currentYear, currentMonth, scope], load)
watch(
  () => projectsStore.selectedProjectId,
  () => {
    if (scope.value === 'project') load()
  },
)
onMounted(load)

async function goToTodo(todo) {
  projectsStore.selectProject(todo.project_id)
  await router.push({ name: 'todos' })
}

async function goToNote(note) {
  projectsStore.selectProject(note.project_id)
  await router.push({ name: 'notes' })
  await notesStore.openNote(note.id)
}
</script>

<template>
  <div class="calendar">
    <div class="calendar-header">
      <button type="button" @click="prevMonth">←</button>
      <h2>{{ monthLabel }}</h2>
      <button type="button" @click="nextMonth">→</button>
    </div>
    <div class="scope-toggle">
      <button
        type="button"
        class="scope-btn"
        :class="{ active: scope === 'all' }"
        @click="scope = 'all'"
      >
        Все проекты
      </button>
      <button
        type="button"
        class="scope-btn"
        :class="{ active: scope === 'project' }"
        :disabled="!projectsStore.selectedProjectId"
        @click="scope = 'project'"
      >
        {{ currentProjectTitle || 'Текущий проект' }}
      </button>
    </div>
    <div class="grid weekdays">
      <div v-for="wd in WEEKDAYS" :key="wd" class="weekday">{{ wd }}</div>
    </div>
    <div class="grid days">
      <div v-for="(day, idx) in days" :key="idx" class="day-cell" :class="{ empty: day === null }">
        <template v-if="day">
          <div class="day-number">{{ day }}</div>
          <button
            v-if="overflowCount(day) > 0"
            type="button"
            class="overflow-badge"
            @click.stop="toggleExpanded(day, $event)"
          >
            +{{ overflowCount(day) }}
          </button>
          <div class="chips">
            <button
              v-for="item in visibleItems(day)"
              :key="`${item.kind}-${item.data.id}`"
              type="button"
              class="chip"
              :class="item.kind"
              :style="item.kind === 'todo' ? { borderLeftColor: priorityMeta(item.data.priority).color } : {}"
              :title="item.data.title"
              @click="goToItem(item)"
            >
              <template v-if="item.kind === 'todo'">{{ STATUS_ICONS[item.data.status] || '☐' }} {{ item.data.title }}</template>
              <template v-else>📝 {{ item.data.title || 'Без названия' }}</template>
            </button>
          </div>

        </template>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="expandedDay !== null" class="day-popover-backdrop" @click="expandedDay = null"></div>
      <div v-if="expandedDay !== null" class="day-popover" :style="{ top: popoverPos.top + 'px', left: popoverPos.left + 'px' }">
        <div class="day-popover-header">{{ expandedDay }} {{ monthLabel }}</div>
        <button
          v-for="item in dayItems(expandedDay)"
          :key="`p-${item.kind}-${item.data.id}`"
          type="button"
          class="chip"
          :class="item.kind"
          :style="item.kind === 'todo' ? { borderLeftColor: priorityMeta(item.data.priority).color } : {}"
          @click="goToItem(item)"
        >
          <template v-if="item.kind === 'todo'">{{ STATUS_ICONS[item.data.status] || '☐' }} {{ item.data.title }}</template>
          <template v-else>📝 {{ item.data.title || 'Без названия' }}</template>
        </button>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.calendar {
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--border);
  padding: 16px;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 12px;
}

.calendar-header h2 {
  margin: 0;
  font-size: 16px;
  text-transform: capitalize;
  min-width: 160px;
  text-align: center;
  color: var(--text);
}

.calendar-header button {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  border-radius: 6px;
  padding: 4px 10px;
}

.scope-toggle {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.scope-btn {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  cursor: pointer;
}

.scope-btn.active {
  background: var(--link);
  border-color: var(--link);
  color: #fff;
}

.scope-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.weekday {
  text-align: center;
  font-size: 12px;
  color: var(--muted);
  padding-bottom: 6px;
}

.day-cell {
  position: relative;
  min-height: 84px;
  border: 1px solid var(--border-light);
  border-radius: 6px;
  padding: 4px;
  overflow: hidden;
}

.overflow-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  z-index: 5;
  border: none;
  border-radius: 8px;
  background: var(--link);
  color: #fff;
  font-size: 9px;
  line-height: 1;
  padding: 2px 5px;
  cursor: pointer;
}

.day-popover-backdrop {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: transparent;
}

.day-popover {
  position: fixed;
  z-index: 61;
  width: 200px;
  max-height: 260px;
  overflow-y: auto;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.day-popover-header {
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 4px;
  text-transform: capitalize;
}

.day-cell.empty {
  border-color: transparent;
}

.day-number {
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 4px;
}

.chips {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.chip {
  display: block;
  width: 100%;
  text-align: left;
  border: none;
  font-size: 11px;
  padding: 1px 4px;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.chip.todo {
  background: var(--chip-todo-bg);
  color: var(--chip-todo-text);
  border-left: 3px solid transparent;
}

.chip.note {
  background: var(--chip-note-bg);
  color: var(--chip-note-text);
}

.chip:hover {
  filter: brightness(0.93);
}

@media (max-width: 720px) {
  .calendar {
    padding: 8px;
  }

  .calendar-header {
    gap: 8px;
  }

  .calendar-header h2 {
    min-width: 0;
    font-size: 14px;
  }

  .grid {
    gap: 2px;
  }

  .weekday {
    font-size: 10px;
  }

  .day-cell {
    min-height: 100px;
    padding: 2px;
  }

  .day-number {
    font-size: 10px;
  }

  .chip {
    font-size: 9px;
  }

  .day-popover {
    width: 180px;
  }

  .scope-toggle {
    flex-wrap: wrap;
  }

  .scope-btn {
    font-size: 11px;
    padding: 3px 10px;
  }
}
</style>
