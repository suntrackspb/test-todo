<script setup>
import { onMounted, ref } from 'vue'

const emit = defineEmits(['save', 'cancel'])

const canvasRef = ref(null)
const color = ref('#1f2328')
const lineWidth = ref(4)
const isErasing = ref(false)

let ctx = null
let drawing = false
let lastPoint = null

function getPoint(evt) {
  const canvas = canvasRef.value
  const rect = canvas.getBoundingClientRect()
  const point = evt.touches ? evt.touches[0] : evt
  return {
    x: ((point.clientX - rect.left) / rect.width) * canvas.width,
    y: ((point.clientY - rect.top) / rect.height) * canvas.height,
  }
}

function startDraw(evt) {
  drawing = true
  lastPoint = getPoint(evt)
}

function draw(evt) {
  if (!drawing) return
  const point = getPoint(evt)
  ctx.strokeStyle = isErasing.value ? '#ffffff' : color.value
  ctx.lineWidth = lineWidth.value
  ctx.lineCap = 'round'
  ctx.beginPath()
  ctx.moveTo(lastPoint.x, lastPoint.y)
  ctx.lineTo(point.x, point.y)
  ctx.stroke()
  lastPoint = point
}

function stopDraw() {
  drawing = false
  lastPoint = null
}

function clearCanvas() {
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
}

function save() {
  canvasRef.value.toBlob((blob) => {
    if (blob) emit('save', blob)
  }, 'image/png')
}

onMounted(() => {
  ctx = canvasRef.value.getContext('2d')
  clearCanvas()
})

defineExpose({ clearCanvas, save })
</script>

<template>
  <div class="drawing-modal">
    <div class="toolbar">
      <button type="button" :class="{ active: !isErasing }" @click="isErasing = false">🖌 Кисть</button>
      <button type="button" :class="{ active: isErasing }" @click="isErasing = true">🧹 Ластик</button>
      <input v-model="color" type="color" :disabled="isErasing" />
      <input v-model.number="lineWidth" type="range" min="1" max="20" />
      <button type="button" @click="clearCanvas">Очистить</button>
    </div>
    <canvas
      ref="canvasRef"
      width="640"
      height="420"
      @mousedown="startDraw"
      @mousemove="draw"
      @mouseup="stopDraw"
      @mouseleave="stopDraw"
      @touchstart.prevent="startDraw"
      @touchmove.prevent="draw"
      @touchend.prevent="stopDraw"
    />
    <div class="footer">
      <button type="button" @click="emit('cancel')">Отмена</button>
      <button type="button" class="primary" @click="save">Сохранить</button>
    </div>
  </div>
</template>

<style scoped>
.drawing-modal {
  background: var(--surface);
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar button {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 13px;
}

.toolbar button.active {
  background: var(--active-bg);
  border-color: var(--link);
}

canvas {
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: crosshair;
  touch-action: none;
  background: #fff;
  max-width: 100%;
  height: auto;
}

.footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.footer button {
  padding: 8px 14px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
}

.footer button.primary {
  background: var(--button-primary-bg);
  color: var(--button-primary-text);
  border-color: var(--button-primary-bg);
}

@media (max-width: 720px) {
  .drawing-modal {
    width: 92vw;
    padding: 10px;
  }

  .toolbar {
    flex-wrap: wrap;
  }
}
</style>
