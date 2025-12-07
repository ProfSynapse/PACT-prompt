# Accessibility Reference

Comprehensive guide to implementing accessible web applications following WCAG 2.1 guidelines.

## Table of Contents

1. [Core Principles (POUR)](#core-principles-pour)
2. [Semantic HTML](#semantic-html)
3. [ARIA Attributes](#aria-attributes)
4. [Keyboard Navigation](#keyboard-navigation)
5. [Focus Management](#focus-management)
6. [Color and Contrast](#color-and-contrast)
7. [Screen Reader Considerations](#screen-reader-considerations)
8. [Common Patterns](#common-patterns)
9. [Testing Accessibility](#testing-accessibility)

---

## Core Principles (POUR)

### Perceivable
Users must be able to perceive the information being presented.

- Provide text alternatives for non-text content
- Provide captions and alternatives for multimedia
- Create content that can be presented in different ways
- Make it easier to see and hear content

### Operable
Users must be able to operate the interface.

- Make all functionality available from keyboard
- Give users enough time to read and use content
- Don't design content that could cause seizures
- Help users navigate and find content

### Understandable
Users must be able to understand the information and operation.

- Make text readable and understandable
- Make content appear and operate in predictable ways
- Help users avoid and correct mistakes

### Robust
Content must be robust enough to work with current and future technologies.

- Maximize compatibility with current and future tools
- Use valid, semantic HTML
- Provide proper ARIA attributes when needed

---

## Semantic HTML

### Use the Right Element

```html
<!-- Bad: Generic divs -->
<div class="header">
  <div class="nav">
    <div class="link">Home</div>
  </div>
</div>

<!-- Good: Semantic HTML -->
<header>
  <nav>
    <a href="/">Home</a>
  </nav>
</header>
```

### Document Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Descriptive Page Title</title>
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>

  <header>
    <nav aria-label="Main navigation">
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/about">About</a></li>
      </ul>
    </nav>
  </header>

  <main id="main-content">
    <h1>Page Heading</h1>
    <article>
      <h2>Article Heading</h2>
      <p>Content...</p>
    </article>
  </main>

  <aside aria-label="Sidebar">
    <h2>Related Links</h2>
  </aside>

  <footer>
    <p>&copy; 2025 Company Name</p>
  </footer>
</body>
</html>
```

### Heading Hierarchy

```html
<!-- Bad: Skipping levels -->
<h1>Main Title</h1>
<h3>Subsection</h3> <!-- Skipped h2 -->

<!-- Good: Proper hierarchy -->
<h1>Main Title</h1>
<h2>Section</h2>
<h3>Subsection</h3>
<h4>Sub-subsection</h4>
```

**Rules:**
- Only one `<h1>` per page
- Don't skip heading levels
- Use headings for structure, not styling
- Screen readers use headings for navigation

---

## ARIA Attributes

### When to Use ARIA

**First Rule of ARIA**: Don't use ARIA if you can use native HTML instead.

```html
<!-- Bad: ARIA on div -->
<div role="button" tabindex="0" onclick="submit()">Submit</div>

<!-- Good: Native button -->
<button type="submit">Submit</button>
```

**Second Rule**: Don't change native semantics unless absolutely necessary.

### Essential ARIA Attributes

#### aria-label
Provides accessible name when visible label isn't possible.

```html
<!-- Icon-only button -->
<button aria-label="Close dialog">
  <svg><!-- X icon --></svg>
</button>

<!-- Search input with icon -->
<input type="search" aria-label="Search products" />
```

#### aria-labelledby
References visible label element(s).

```html
<h2 id="dialog-title">Confirm Action</h2>
<div role="dialog" aria-labelledby="dialog-title">
  <p>Are you sure?</p>
</div>
```

#### aria-describedby
Provides additional description.

```html
<input
  type="password"
  id="password"
  aria-describedby="password-hint"
/>
<span id="password-hint">
  Password must be at least 8 characters
</span>

<!-- With error -->
<input
  type="email"
  id="email"
  aria-invalid="true"
  aria-describedby="email-error"
/>
<span id="email-error" role="alert">
  Please enter a valid email address
</span>
```

#### aria-hidden
Hides content from screen readers.

```html
<!-- Decorative icon -->
<span aria-hidden="true">★</span>
<span class="sr-only">4 out of 5 stars</span>

<!-- Font icon -->
<button>
  <i class="icon-save" aria-hidden="true"></i>
  Save
</button>
```

#### aria-live
Announces dynamic content changes.

```html
<!-- Polite: Announces when user is idle -->
<div aria-live="polite" aria-atomic="true">
  3 items in cart
</div>

<!-- Assertive: Announces immediately -->
<div role="alert" aria-live="assertive">
  Error: Payment failed
</div>
```

**Politeness levels:**
- `off`: No announcement (default)
- `polite`: Announce when convenient
- `assertive`: Announce immediately

#### aria-expanded
Indicates collapsible content state.

```html
<button
  aria-expanded="false"
  aria-controls="dropdown-menu"
>
  Options
</button>
<ul id="dropdown-menu" hidden>
  <li>Option 1</li>
  <li>Option 2</li>
</ul>

<!-- When expanded -->
<button aria-expanded="true" aria-controls="dropdown-menu">
  Options
</button>
<ul id="dropdown-menu">
  <li>Option 1</li>
  <li>Option 2</li>
</ul>
```

#### aria-current
Indicates current item in a set.

```html
<nav>
  <a href="/" aria-current="page">Home</a>
  <a href="/about">About</a>
  <a href="/contact">Contact</a>
</nav>

<!-- Breadcrumbs -->
<nav aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Home</a></li>
    <li><a href="/products">Products</a></li>
    <li aria-current="page">Laptop</li>
  </ol>
</nav>
```

### ARIA Roles

#### Landmark Roles

```html
<header role="banner"><!-- Main header --></header>
<nav role="navigation"><!-- Navigation --></nav>
<main role="main"><!-- Main content --></main>
<aside role="complementary"><!-- Sidebar --></aside>
<footer role="contentinfo"><!-- Footer --></footer>
<form role="search"><!-- Search form --></form>
```

**Note**: HTML5 semantic elements have implicit roles. Use explicit roles for older browsers or clarification.

#### Widget Roles

```html
<!-- Tab interface -->
<div role="tablist">
  <button role="tab" aria-selected="true" aria-controls="panel-1">Tab 1</button>
  <button role="tab" aria-selected="false" aria-controls="panel-2">Tab 2</button>
</div>
<div role="tabpanel" id="panel-1">Content 1</div>
<div role="tabpanel" id="panel-2" hidden>Content 2</div>

<!-- Alert -->
<div role="alert">Your session will expire in 5 minutes</div>

<!-- Status -->
<div role="status" aria-live="polite">Loading...</div>
```

---

## Keyboard Navigation

### Tab Order

```html
<!-- Default tab order follows DOM order -->
<button>First</button>
<button>Second</button>
<button>Third</button>

<!-- Remove from tab order -->
<div tabindex="-1">Not focusable via keyboard</div>

<!-- Add to tab order (avoid unless necessary) -->
<div tabindex="0" role="button">Focusable custom element</div>
```

**Tab Index Values:**
- `-1`: Programmatically focusable, not in tab order
- `0`: In natural tab order
- `1+`: Explicit tab order (avoid - creates confusion)

### Keyboard Event Handling

```typescript
const handleKeyDown = (event: React.KeyboardEvent) => {
  switch (event.key) {
    case 'Enter':
    case ' ': // Space
      event.preventDefault();
      handleClick();
      break;
    case 'Escape':
      handleClose();
      break;
    case 'ArrowDown':
      event.preventDefault();
      focusNext();
      break;
    case 'ArrowUp':
      event.preventDefault();
      focusPrevious();
      break;
  }
};

<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={handleKeyDown}
>
  Custom Button
</div>
```

### Common Keyboard Patterns

**Modal Dialog:**
- `Escape`: Close dialog
- `Tab`: Cycle through focusable elements (trap focus)
- Focus returns to trigger element on close

**Dropdown Menu:**
- `Enter`/`Space`: Open menu
- `Arrow Down`/`Up`: Navigate items
- `Escape`: Close menu
- `Home`/`End`: First/last item

**Tabs:**
- `Arrow Left`/`Right`: Navigate tabs
- `Home`/`End`: First/last tab
- `Enter`/`Space`: Activate tab

---

## Focus Management

### Focus Trapping (Modals)

```typescript
const Modal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
  onClose,
  children
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    // Save currently focused element
    previousFocusRef.current = document.activeElement as HTMLElement;

    // Focus modal
    modalRef.current?.focus();

    // Trap focus within modal
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }

      if (e.key === 'Tab') {
        const focusableElements = modalRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (!focusableElements?.length) return;

        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      // Restore focus
      previousFocusRef.current?.focus();
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
      className="modal"
    >
      <button onClick={onClose} aria-label="Close">×</button>
      {children}
    </div>
  );
};
```

### Focus Indicators

```css
/* Remove default outline only if providing custom focus style */
*:focus {
  outline: none;
}

/* Provide clear custom focus indicator */
button:focus-visible,
a:focus-visible,
input:focus-visible {
  outline: 2px solid #005fcc;
  outline-offset: 2px;
}

/* :focus-visible only shows focus for keyboard navigation */
/* Doesn't show for mouse clicks */
```

**Best Practices:**
- Never remove focus indicators without replacement
- Use `:focus-visible` for keyboard-only focus styles
- Ensure 3:1 contrast ratio for focus indicators
- Make focus indicators clearly visible

---

## Color and Contrast

### Contrast Ratios (WCAG 2.1)

**Level AA (Minimum):**
- Normal text: 4.5:1
- Large text (18pt+/14pt+ bold): 3:1
- UI components and graphics: 3:1

**Level AAA (Enhanced):**
- Normal text: 7:1
- Large text: 4.5:1

```css
/* Good contrast examples */
.text-primary {
  color: #1a1a1a; /* Dark gray */
  background: #ffffff; /* White */
  /* Ratio: 16.1:1 ✓ */
}

.button-primary {
  color: #ffffff; /* White */
  background: #0066cc; /* Blue */
  /* Ratio: 6.1:1 ✓ */
}

/* Bad contrast */
.text-light {
  color: #cccccc; /* Light gray */
  background: #ffffff; /* White */
  /* Ratio: 1.6:1 ✗ Fails AA */
}
```

### Don't Rely on Color Alone

```html
<!-- Bad: Color only -->
<span style="color: red;">Error</span>
<span style="color: green;">Success</span>

<!-- Good: Color + icon + text -->
<span class="error">
  <svg aria-hidden="true"><!-- Error icon --></svg>
  Error: Invalid input
</span>

<span class="success">
  <svg aria-hidden="true"><!-- Success icon --></svg>
  Success: Changes saved
</span>
```

### Dark Mode Considerations

```css
@media (prefers-color-scheme: dark) {
  :root {
    --text-primary: #e0e0e0;
    --bg-primary: #1a1a1a;
    --accent: #66b3ff;
  }

  /* Ensure contrast in dark mode too */
  body {
    color: var(--text-primary);
    background: var(--bg-primary);
  }
}
```

---

## Screen Reader Considerations

### Visually Hidden Content

```css
/* Screen reader only text */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Make visible on focus (skip links) */
.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

Usage:

```html
<button>
  <svg aria-hidden="true"><!-- Icon --></svg>
  <span class="sr-only">Save document</span>
</button>

<a href="#main-content" class="sr-only-focusable">
  Skip to main content
</a>
```

### Announcing Dynamic Changes

```typescript
const Toast: React.FC<{ message: string; type: 'success' | 'error' }> = ({
  message,
  type
}) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
      className={`toast toast-${type}`}
    >
      {message}
    </div>
  );
};

// Loading state
const LoadingIndicator: React.FC = () => (
  <div role="status" aria-live="polite" aria-busy="true">
    <span class="sr-only">Loading, please wait...</span>
    <div class="spinner" aria-hidden="true"></div>
  </div>
);
```

---

## Common Patterns

### Accessible Forms

```html
<form>
  <!-- Text input with label -->
  <div class="form-field">
    <label for="name">Name:</label>
    <input
      type="text"
      id="name"
      name="name"
      required
      aria-required="true"
    />
  </div>

  <!-- Input with description -->
  <div class="form-field">
    <label for="email">Email:</label>
    <input
      type="email"
      id="email"
      name="email"
      aria-describedby="email-hint"
    />
    <span id="email-hint" class="hint">
      We'll never share your email
    </span>
  </div>

  <!-- Input with error -->
  <div class="form-field">
    <label for="password">Password:</label>
    <input
      type="password"
      id="password"
      name="password"
      aria-invalid="true"
      aria-describedby="password-error password-requirements"
    />
    <span id="password-requirements" class="hint">
      Must be at least 8 characters
    </span>
    <span id="password-error" role="alert" class="error">
      Password is too short
    </span>
  </div>

  <!-- Radio buttons -->
  <fieldset>
    <legend>Subscription plan:</legend>
    <div>
      <input type="radio" id="free" name="plan" value="free" />
      <label for="free">Free</label>
    </div>
    <div>
      <input type="radio" id="pro" name="plan" value="pro" />
      <label for="pro">Pro</label>
    </div>
  </fieldset>

  <!-- Checkbox -->
  <div class="form-field">
    <input type="checkbox" id="agree" name="agree" required />
    <label for="agree">
      I agree to the <a href="/terms">terms and conditions</a>
    </label>
  </div>

  <button type="submit">Submit</button>
</form>
```

### Accessible Dropdown

```typescript
const Dropdown: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLUListElement>(null);

  const options = ['Option 1', 'Option 2', 'Option 3'];

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        setIsOpen(!isOpen);
        break;
      case 'Escape':
        setIsOpen(false);
        buttonRef.current?.focus();
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setSelectedIndex((prev) =>
            prev < options.length - 1 ? prev + 1 : prev
          );
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : prev));
        break;
    }
  };

  return (
    <div className="dropdown">
      <button
        ref={buttonRef}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
      >
        {options[selectedIndex]}
      </button>

      {isOpen && (
        <ul
          ref={menuRef}
          role="listbox"
          aria-labelledby="dropdown-button"
        >
          {options.map((option, index) => (
            <li
              key={option}
              role="option"
              aria-selected={index === selectedIndex}
              onClick={() => {
                setSelectedIndex(index);
                setIsOpen(false);
              }}
            >
              {option}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
```

---

## Testing Accessibility

### Automated Testing Tools

1. **axe DevTools** (Browser extension)
   - Detects 57% of WCAG issues automatically
   - Provides detailed guidance

2. **Lighthouse** (Chrome DevTools)
   - Built into Chrome
   - Accessibility audit in performance tab

3. **WAVE** (Browser extension)
   - Visual feedback on page
   - Identifies errors, warnings, features

### Manual Testing Checklist

- [ ] Navigate entire site using only keyboard
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Verify color contrast with contrast checker
- [ ] Zoom to 200% and verify layout
- [ ] Test with browser's high contrast mode
- [ ] Disable CSS and verify content order
- [ ] Test form validation and error messages
- [ ] Verify all images have alt text
- [ ] Check all interactive elements are focusable
- [ ] Verify focus indicators are visible

### React Testing Library (Accessibility-First)

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('button is accessible', () => {
  render(<button>Save</button>);

  // Find by accessible name
  const button = screen.getByRole('button', { name: /save/i });
  expect(button).toBeInTheDocument();
});

test('form has accessible labels', () => {
  render(<LoginForm />);

  const emailInput = screen.getByLabelText(/email/i);
  const passwordInput = screen.getByLabelText(/password/i);

  expect(emailInput).toHaveAttribute('type', 'email');
  expect(passwordInput).toHaveAttribute('type', 'password');
});

test('error message is associated with input', () => {
  render(<InputWithError />);

  const input = screen.getByRole('textbox');
  const error = screen.getByRole('alert');

  expect(input).toHaveAttribute('aria-invalid', 'true');
  expect(input).toHaveAttribute('aria-describedby', error.id);
});
```

### Screen Reader Testing

**macOS (VoiceOver):**
- Enable: Cmd + F5
- Navigate: Control + Option + Arrow keys
- Interact: Control + Option + Space

**Windows (NVDA - free):**
- Navigate: Arrow keys
- Read: NVDA + Down arrow
- Interact: Enter

**Testing checklist:**
- All content is announced in logical order
- Interactive elements announce their role
- Form inputs announce labels and errors
- Dynamic changes are announced
- Skip links work correctly
