# Frontend Component Specification Template

## Component: [ComponentName]

### Overview
- **Type**: [Presentational | Container | Layout | Form | Navigation]
- **Framework**: [React | Vue | Angular | Svelte]
- **Reusability**: [Project-specific | Shared library]

---

## Component API

### Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `id` | `string` | No | auto | Unique identifier |
| `variant` | `'primary' \| 'secondary'` | No | `'primary'` | Visual variant |
| `disabled` | `boolean` | No | `false` | Disabled state |
| `onAction` | `() => void` | No | - | Action callback |
| `children` | `ReactNode` | Yes | - | Content |

### Events/Callbacks

| Event | Payload | Description |
|-------|---------|-------------|
| `onAction` | `void` | Triggered when [action] |
| `onChange` | `{ value: T }` | Triggered when value changes |
| `onError` | `{ error: Error }` | Triggered on error |

### Slots/Children

| Slot | Purpose | Default |
|------|---------|---------|
| `default` | Main content | Required |
| `header` | Header area | None |
| `footer` | Footer area | None |

---

## States

### Visual States
- **Default**: Normal appearance
- **Hover**: [Describe hover state]
- **Focus**: [Describe focus state + outline]
- **Active**: [Describe pressed state]
- **Disabled**: [Describe disabled appearance]
- **Loading**: [Describe loading state]
- **Error**: [Describe error state]

### Data States
- **Empty**: No data to display
- **Loading**: Fetching data
- **Success**: Data loaded
- **Error**: Failed to load
- **Partial**: Some items failed

---

## Accessibility

### Requirements
- [ ] Keyboard navigable
- [ ] Screen reader compatible
- [ ] Focus indicators visible
- [ ] Color contrast meets WCAG AA
- [ ] Touch targets >= 44x44px

### ARIA Attributes
```tsx
<Component
  role="[role]"
  aria-label="[label]"
  aria-describedby="[id]"
  aria-expanded={isOpen}
  aria-disabled={disabled}
/>
```

### Keyboard Interactions
| Key | Action |
|-----|--------|
| Enter/Space | Activate |
| Escape | Close/Cancel |
| Arrow keys | Navigate |
| Tab | Focus next |

---

## Styling

### CSS Variables
```css
--component-bg: var(--color-surface);
--component-border: var(--color-border);
--component-text: var(--color-text-primary);
--component-radius: var(--radius-md);
--component-padding: var(--spacing-md);
```

### Responsive Breakpoints
| Breakpoint | Changes |
|------------|---------|
| Mobile (<640px) | Stack layout, full width |
| Tablet (640-1024px) | Side-by-side, compact |
| Desktop (>1024px) | Full layout |

---

## Usage Examples

### Basic Usage
```tsx
<Component variant="primary" onAction={handleAction}>
  Content here
</Component>
```

### With All Options
```tsx
<Component
  id="my-component"
  variant="secondary"
  disabled={false}
  onAction={handleAction}
  onChange={handleChange}
>
  <Header slot="header">Title</Header>
  Main content
  <Footer slot="footer">Actions</Footer>
</Component>
```

---

## Testing Requirements

- [ ] Renders correctly with required props
- [ ] Handles all prop variations
- [ ] Keyboard navigation works
- [ ] Screen reader announces correctly
- [ ] Callbacks fire appropriately
- [ ] Error states display correctly

---
*Generated from pact-frontend-patterns skill template*
