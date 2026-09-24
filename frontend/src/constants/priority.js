export const PRIORITIES = [
  { value: 'critical', label: 'Критично', color: '#e5484d' },
  { value: 'urgent', label: 'Срочно', color: '#f5a623' },
  { value: 'low', label: 'Не срочно', color: '#3b82f6' },
  { value: 'none', label: 'Похуй', color: '#2ecc71' },
]

export function priorityMeta(value) {
  return PRIORITIES.find((p) => p.value === value) || PRIORITIES[PRIORITIES.length - 1]
}
