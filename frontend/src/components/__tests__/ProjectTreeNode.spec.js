import { describe, expect, it, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ProjectTreeNode from '../ProjectTreeNode.vue'

const node = {
  id: 1,
  title: 'Parent',
  children: [{ id: 2, title: 'Child', children: [] }],
}

describe('ProjectTreeNode', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('renders its title and nested children', () => {
    const wrapper = mount(ProjectTreeNode, { props: { node, selectedId: null } })
    expect(wrapper.text()).toContain('Parent')
    expect(wrapper.text()).toContain('Child')
  })

  it('emits select with the node id when title is clicked', async () => {
    const wrapper = mount(ProjectTreeNode, { props: { node, selectedId: null } })
    await wrapper.find('.title').trigger('click')
    expect(wrapper.emitted('select')[0]).toEqual([1])
  })

  it('emits rename with the new title from prompt', async () => {
    vi.stubGlobal('prompt', () => 'Renamed')
    const wrapper = mount(ProjectTreeNode, { props: { node, selectedId: null } })
    await wrapper.find('button[title="Переименовать"]').trigger('click')
    expect(wrapper.emitted('rename')[0]).toEqual([1, 'Renamed'])
  })

  it('does not emit delete when confirm is cancelled', async () => {
    vi.stubGlobal('confirm', () => false)
    const wrapper = mount(ProjectTreeNode, { props: { node, selectedId: null } })
    await wrapper.find('button[title="Удалить"]').trigger('click')
    expect(wrapper.emitted('delete')).toBeUndefined()
  })

  it('emits delete when confirm is accepted', async () => {
    vi.stubGlobal('confirm', () => true)
    const wrapper = mount(ProjectTreeNode, { props: { node, selectedId: null } })
    await wrapper.find('button[title="Удалить"]').trigger('click')
    expect(wrapper.emitted('delete')[0]).toEqual([1])
  })
})
