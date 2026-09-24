import { describe, expect, it, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DrawingCanvas from '../DrawingCanvas.vue'

function stubCanvasApi() {
  const ctxStub = {
    fillRect: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    stroke: vi.fn(),
    fillStyle: '',
    strokeStyle: '',
    lineWidth: 0,
    lineCap: '',
  }
  HTMLCanvasElement.prototype.getContext = vi.fn(() => ctxStub)
  HTMLCanvasElement.prototype.toBlob = vi.fn(function (callback) {
    callback(new Blob(['fake-png-bytes'], { type: 'image/png' }))
  })
  return ctxStub
}

describe('DrawingCanvas', () => {
  beforeEach(() => {
    stubCanvasApi()
  })

  it('clears the canvas on mount', () => {
    const ctx = stubCanvasApi()
    mount(DrawingCanvas)
    expect(ctx.fillRect).toHaveBeenCalled()
  })

  it('emits save with a PNG blob when Save is clicked', async () => {
    const wrapper = mount(DrawingCanvas)
    await wrapper.find('.footer .primary').trigger('click')

    const emitted = wrapper.emitted('save')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toBeInstanceOf(Blob)
    expect(emitted[0][0].type).toBe('image/png')
  })

  it('emits cancel when Cancel is clicked', async () => {
    const wrapper = mount(DrawingCanvas)
    await wrapper.find('.footer button:not(.primary)').trigger('click')
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })
})
