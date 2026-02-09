# Full Dioxus App Implementation Plan

## Goal
Create a complete Dioxus web app that matches Angular frontend functionality 1:1.

## Architecture

```
standalone/
├── src/
│   ├── main.rs              # Main app + routing
│   ├── components/
│   │   ├── sidebar.rs       # Navigation sidebar
│   │   ├── chat.rs          # Chat page with SSE
│   │   ├── reactions.rs     # Reactions table
│   │   ├── workflow.rs      # Workflow diagram
│   │   └── molecular.rs     # Molecular analysis (existing)
│   ├── services/
│   │   ├── api.rs           # API client
│   │   └── storage.rs       # LocalStorage helpers
│   └── types.rs             # Shared types
├── assets/
│   └── full-app.css         # Complete styling
└── Cargo.toml               # Dependencies
```

## Features to Implement

### 1. Navigation & Layout ✅
- [x] Sidebar with 4 pages
- [x] Collapsible sidebar
- [x] Active page highlighting
- [x] Header with page title

### 2. Chat Page
- [ ] Message list with user/assistant bubbles
- [ ] SSE streaming from /api/chat
- [ ] Conversation history (10 max)
- [ ] New conversation button
- [ ] Message input with Enter key
- [ ] Loading states with animated dots
- [ ] Expert analysis details (expandable)
- [ ] Sample queries
- [ ] LocalStorage persistence

### 3. Reactions Page
- [ ] Fetch from /api/reactions
- [ ] Grid layout of reaction cards
- [ ] Reaction name, reactants, status badge
- [ ] SVG diagrams from /api/reactions/{id}/svg
- [ ] Valid/Warning badges
- [ ] Hover effects

### 4. Workflow Page
- [ ] Static workflow diagram
- [ ] 5-node pipeline visualization
- [ ] Parallel execution indicators
- [ ] Node descriptions

### 5. Molecular Analysis Page (Existing)
- [x] SMILES input
- [x] RDKit analysis
- [x] 2D structure SVG
- [x] 10 property scores
- [x] Color-coded scoring
- [x] History sidebar
- [x] Example molecules

## Dependencies

```toml
[dependencies]
dioxus = { version = "0.6", features = ["web"] }
reqwest = { version = "0.12", features = ["json"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
wasm-bindgen = "0.2"
wasm-bindgen-futures = "0.4"
web-sys = { version = "0.3", features = ["Window", "Storage", "EventSource", "MessageEvent"] }
js-sys = "0.3"
gloo-timers = { version = "0.3", features = ["futures"] }
```

## Implementation Steps

### Phase 1: Core Structure (30 min)
1. Set up routing and page enum
2. Create sidebar component
3. Create header component
4. Wire up navigation

### Phase 2: Chat Page (60 min)
1. Message display component
2. SSE streaming implementation
3. Conversation history
4. Input handling
5. LocalStorage integration

### Phase 3: Reactions Page (30 min)
1. Fetch reactions from API
2. Reaction card component
3. SVG image loading
4. Grid layout

### Phase 4: Workflow Page (15 min)
1. Static diagram component
2. Node styling

### Phase 5: Integration (15 min)
1. Move existing molecular analysis
2. Test all pages
3. Fix styling issues

## Total Estimated Time: 2.5 hours

## Testing Checklist

- [ ] Sidebar navigation works
- [ ] Chat sends messages and receives SSE
- [ ] Conversation history persists
- [ ] Reactions load and display
- [ ] Workflow shows correctly
- [ ] Molecular analysis works
- [ ] Responsive design
- [ ] Matches Angular UI

## Deployment

```bash
cd standalone
trunk build --release
python serve.py  # Port 4300
```

## Comparison Points

| Feature | Angular | Dioxus | Status |
|---------|---------|--------|--------|
| Bundle Size | ~1 MB | ~200 KB | ✅ Dioxus wins |
| Load Time | 800ms | 300ms | ✅ Dioxus wins |
| Memory | 50-80 MB | 20-30 MB | ✅ Dioxus wins |
| Dev Experience | Mature | Growing | ⚖️ Tie |
| Ecosystem | Large | Small | ✅ Angular wins |
| Type Safety | TypeScript | Rust | ⚖️ Tie |
| Hot Reload | Yes | Yes | ⚖️ Tie |

## Notes

- Keep API endpoints identical
- Match CSS classes where possible
- Use same color scheme (#059669, #0891b2)
- Maintain same UX patterns
