<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import { useNotesStore } from '@/stores/notes'
import { getAccessToken } from '@/api/client'
import DrawingCanvas from './DrawingCanvas.vue'

function attachmentUrl(filePath) {
  return `/api/uploads/${filePath}?token=${encodeURIComponent(getAccessToken() || '')}`
}

const props = defineProps({
  note: { type: Object, required: true },
})

const notesStore = useNotesStore()
const title = ref(props.note.title)
const dueDate = ref(props.note.due_date || '')
const showDrawing = ref(false)
const lightboxSrc = ref(null)
let saveTimer = null

const editor = new Editor({
  extensions: [StarterKit, Image],
  content: safeParse(props.note.content_json),
  onUpdate: () => scheduleSave(),
})

function safeParse(json) {
  try {
    const parsed = JSON.parse(json)
    return Object.keys(parsed).length ? parsed : '<p></p>'
  } catch {
    return '<p></p>'
  }
}

function scheduleSave() {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(saveContent, 600)
}

async function saveContent() {
  await notesStore.updateNote(props.note.id, {
    content_json: JSON.stringify(editor.getJSON()),
  })
}

async function saveTitle() {
  await notesStore.updateNote(props.note.id, { title: title.value })
}

async function saveDueDate() {
  if (dueDate.value) {
    await notesStore.updateNote(props.note.id, { due_date: dueDate.value })
  } else {
    await notesStore.updateNote(props.note.id, { clear_due_date: true })
  }
}

async function insertUploadedImage(file) {
  const attachment = await notesStore.uploadAttachment(props.note.id, file, 'image')
  editor.chain().focus().setImage({ src: attachmentUrl(attachment.file_path) }).run()
}

function onFileInputChange(evt) {
  const file = evt.target.files?.[0]
  if (file) insertUploadedImage(file)
  evt.target.value = ''
}

function onPaste(evt) {
  const items = Array.from(evt.clipboardData?.items || [])
  const imageItem = items.find((item) => item.type.startsWith('image/'))
  if (imageItem) {
    evt.preventDefault()
    const file = imageItem.getAsFile()
    if (file) insertUploadedImage(file)
  }
}

async function onDrawingSave(blob) {
  const file = new File([blob], `drawing-${Date.now()}.png`, { type: 'image/png' })
  await insertUploadedImage(file)
  showDrawing.value = false
}

function onEditorClick(evt) {
  if (evt.target.tagName === 'IMG') {
    lightboxSrc.value = evt.target.getAttribute('src')
  }
}

watch(
  () => props.note.id,
  () => {
    title.value = props.note.title
    dueDate.value = props.note.due_date || ''
    editor.commands.setContent(safeParse(props.note.content_json))
  },
)

onBeforeUnmount(() => {
  clearTimeout(saveTimer)
  editor.destroy()
})
</script>

<template>
  <div class="note-editor" @paste="onPaste">
    <input v-model="title" class="title-input" placeholder="Без названия" @blur="saveTitle" />

    <div class="meta">
      <label>
        Дата
        <input v-model="dueDate" type="date" @change="saveDueDate" />
      </label>
    </div>

    <div class="toolbar">
      <button type="button" @click="editor.chain().focus().toggleBold().run()">B</button>
      <button type="button" @click="editor.chain().focus().toggleItalic().run()"><em>I</em></button>
      <button type="button" @click="editor.chain().focus().toggleHeading({ level: 2 }).run()">H2</button>
      <button type="button" @click="editor.chain().focus().toggleBulletList().run()">• Список</button>
      <label class="upload-btn">
        🖼 Изображение
        <input type="file" accept="image/*" hidden @change="onFileInputChange" />
      </label>
      <button type="button" @click="showDrawing = true">✏️ Рисунок</button>
    </div>

    <EditorContent :editor="editor" class="editor-content" @click="onEditorClick" />

    <div v-if="showDrawing" class="drawing-overlay">
      <DrawingCanvas @save="onDrawingSave" @cancel="showDrawing = false" />
    </div>

    <div v-if="lightboxSrc" class="lightbox-overlay" @click="lightboxSrc = null">
      <img :src="lightboxSrc" class="lightbox-image" @click.stop />
      <button type="button" class="lightbox-close" @click="lightboxSrc = null">✕</button>
    </div>
  </div>
</template>

<style scoped>
.note-editor {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
}

.title-input {
  font-size: 22px;
  font-weight: 600;
  border: none;
  outline: none;
  background: transparent;
}

.meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: var(--muted);
}

.meta label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.toolbar {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.toolbar button,
.upload-btn {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 13px;
  cursor: pointer;
}

.editor-content {
  flex: 1;
  overflow-y: auto;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  background: var(--surface);
}

.editor-content :deep(img) {
  display: block;
  max-width: 160px;
  max-height: 160px;
  width: auto;
  height: auto;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid var(--border);
  cursor: zoom-in;
  margin: 4px 0;
}

.editor-content :deep(.ProseMirror) {
  outline: none;
  min-height: 200px;
  color: var(--text);
}

.drawing-overlay,
.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.lightbox-image {
  max-width: 90vw;
  max-height: 90vh;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.lightbox-close {
  position: absolute;
  top: 24px;
  right: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 16px;
}

@media (max-width: 720px) {
  .title-input {
    font-size: 18px;
  }

  .meta {
    flex-wrap: wrap;
  }

  .toolbar {
    gap: 4px;
  }

  .toolbar button,
  .upload-btn {
    padding: 4px 8px;
    font-size: 12px;
  }

  .lightbox-close {
    top: 12px;
    right: 12px;
  }
}
</style>
