<script setup>
import { computed, watch } from 'vue'
import { useProjectsStore } from '@/stores/projects'
import { useNotesStore } from '@/stores/notes'
import NoteEditor from '@/components/NoteEditor.vue'

const projectsStore = useProjectsStore()
const notesStore = useNotesStore()

const projectId = computed(() => projectsStore.selectedProjectId)
const notes = computed(() => notesStore.notesByProject[projectId.value] || [])

watch(
  projectId,
  async (id) => {
    notesStore.activeNote = null
    if (id) await notesStore.fetchNotes(id)
  },
  { immediate: true },
)

async function createNote() {
  const note = await notesStore.createNote(projectId.value, { title: 'Новая заметка' })
  await notesStore.openNote(note.id)
}

async function openNote(id) {
  await notesStore.openNote(id)
}

async function removeNote(id) {
  if (confirm('Удалить заметку?')) {
    await notesStore.deleteNote(id, projectId.value)
  }
}
</script>

<template>
  <div v-if="!projectId" class="placeholder">Выберите проект слева, чтобы увидеть заметки</div>
  <div v-else class="notes-layout">
    <div class="notes-list">
      <button type="button" class="new-note" @click="createNote">+ Новая заметка</button>
      <ul>
        <li
          v-for="note in notes"
          :key="note.id"
          :class="{ active: notesStore.activeNote?.id === note.id }"
          @click="openNote(note.id)"
        >
          <span class="note-title">{{ note.title || 'Без названия' }}</span>
          <button type="button" class="delete" @click.stop="removeNote(note.id)">✕</button>
        </li>
      </ul>
      <p v-if="!notes.length" class="empty">Заметок пока нет</p>
    </div>
    <div class="note-panel">
      <NoteEditor v-if="notesStore.activeNote" :note="notesStore.activeNote" :key="notesStore.activeNote.id" />
      <div v-else class="placeholder">Выберите заметку или создайте новую</div>
    </div>
  </div>
</template>

<style scoped>
.placeholder {
  color: var(--faint);
  padding: 40px;
  text-align: center;
}

.notes-layout {
  display: flex;
  gap: 16px;
  height: 100%;
}

.notes-list {
  width: 260px;
  flex-shrink: 0;
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--border);
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
}

.new-note {
  border: 1px dashed var(--link);
  background: none;
  color: var(--link);
  border-radius: 6px;
  padding: 8px;
  font-size: 13px;
}

.notes-list ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.notes-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text);
}

.notes-list li:hover {
  background: var(--hover-bg);
}

.notes-list li.active {
  background: var(--active-bg);
}

.note-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.delete {
  border: none;
  background: none;
  font-size: 11px;
  color: var(--faint);
}

.note-panel {
  flex: 1;
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--border);
  padding: 16px;
  min-width: 0;
}

.empty {
  font-size: 13px;
  color: var(--faint);
  padding: 8px;
}

@media (max-width: 720px) {
  .notes-layout {
    flex-direction: column;
    height: auto;
  }

  .notes-list {
    width: 100%;
    max-height: 200px;
  }

  .note-panel {
    min-height: 400px;
  }
}
</style>
