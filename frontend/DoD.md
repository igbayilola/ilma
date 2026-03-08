# Definition of Done (DoD) - ILMA Project

## Global Requirements

### 1. Code Quality & Architecture
- [ ] No ESLint/TypeScript errors or warnings.
- [ ] Component structure follows the `Atomic Design` or `Feature-based` organization.
- [ ] No hardcoded strings for critical UI (ready for i18n structure, even if mono-lingual now).
- [ ] State management (Zustand) is decoupled from UI components.
- [ ] `console.log` removed (except for specific debug routes).

### 2. Performance
- [ ] **Lazy Loading**: Route-based code splitting implemented using `React.lazy` and `Suspense`.
- [ ] **Bundle Size**: Initial load bundle is minimized.
- [ ] **Rendering**: No unnecessary re-renders in complex lists (Subjects, Users).
- [ ] **Images**: Proper sizing and `alt` tags used.
- [ ] **Animation**: GPU-accelerated transitions (transform, opacity) only.

### 3. Accessibility (WCAG 2.1 AA)
- [ ] **Contrast**: Text/Background contrast ratio > 4.5:1.
- [ ] **Focus**: Visible focus indicators on all interactive elements (Buttons, Inputs, Links).
- [ ] **Keyboard Nav**: Full site navigatable via Tab/Enter/Space.
- [ ] **Screen Readers**: 
    - [ ] Images have `alt` text.
    - [ ] Icons have `aria-hidden="true"`.
    - [ ] Buttons have `aria-label` if text is missing.
    - [ ] Progress bars have `role="progressbar"`.
- [ ] **Touch Targets**: Minimum 44x44px for mobile interactions.

### 4. Offline & PWA
- [ ] **Manifest**: `manifest.json` is valid and linked.
- [ ] **Service Worker**: Caches app shell and static assets.
- [ ] **Fallback**: Custom "You are offline" UI for non-cached dynamic routes.
- [ ] **Sync**: 
    - [ ] Actions performed offline are queued in IndexedDB.
    - [ ] Sync triggers automatically when online.
    - [ ] Visual indicators (Cloud icon) reflect sync status accurately.

---

## Per-Screen Checklist

### 1. Exercise Player (`/exercise/:id`)
- [ ] **Inputs**: MCQ options are clickable via keyboard. Text input is focused on load.
- [ ] **Feedback**: Correct/Incorrect states are distinguishable by Color AND Icon.
- [ ] **Offline**: Can complete full exercise without network. Result is queued.
- [ ] **Paywall**: Free users blocked after 5 daily attempts.

### 2. Dashboard (`/student/dashboard`)
- [ ] **Loading**: Skeletons shown while fetching data.
- [ ] **Empty State**: Friendly message if no subjects/progress found.
- [ ] **Progress**: Progress bars accurately reflect math (e.g. 50%).

### 3. Admin Back-office (`/admin`)
- [ ] **Tables**: Dense but readable on Desktop. Horizontal scroll on Mobile.
- [ ] **Actions**: Destructive actions (Suspend, Delete) require confirmation Modal.
- [ ] **Search**: Filters work instantly (client-side) or debounce correctly (server-side).

### 4. Auth (`/login`, `/register`)
- [ ] **Validation**: Errors are clear and linked to input fields.
- [ ] **Security**: Passwords masked. No sensitive data in URL.
- [ ] **Redirect**: User redirected to correct role-based dashboard.

---

## Manual Test Script (Offline Flow)
1. Open App (Online) -> Login.
2. Go to Dashboard -> Verify content loads.
3. **Turn off Network (DevTools)**.
4. Navigate to an Exercise (cached).
5. Complete questions -> Submit.
6. Verify "Offline Mode" banner appears.
7. Verify "Sync Counter" increments to 1.
8. **Turn on Network**.
9. Verify "Sync Counter" decrements to 0.
10. Check "Progress" page -> XP updated.
