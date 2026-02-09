# Conversation History Feature

## Changes Made

### Frontend (Angular)

**File:** `src/frontend/reactome-ui/src/app/components/chat/chat.ts`

Added conversation history management:
- Store up to 10 conversations in localStorage
- Each conversation has: id, title, messages, timestamp
- Auto-generate title from first user message
- New conversation button
- Delete conversation button
- Load/switch between conversations
- Persist on every message

**File:** `src/frontend/reactome-ui/src/app/components/chat/chat.html`

Added UI elements:
- Collapsible history sidebar (256px width)
- "New Conversation" button
- Conversation list with titles and dates
- Delete button for each conversation
- "History ▶" toggle button in header
- Active conversation highlighting

### Features

1. **Auto-save**: Every message automatically saves to localStorage
2. **Limit**: Only keeps last 10 conversations
3. **Smart titles**: Uses first 50 chars of first user message
4. **Date formatting**: Shows "Today", "Yesterday", "X days ago", or date
5. **Persistence**: Survives page refresh
6. **Delete**: Click ✕ to remove conversation

### Storage

- **Key**: `lnp_conversations`
- **Format**: JSON array of Conversation objects
- **Size**: ~1-5 KB per conversation (depends on message length)
- **Max**: 10 conversations (~10-50 KB total)

## Usage

1. **Start new conversation**: Click "+ New Conversation"
2. **Switch conversation**: Click on any conversation in history
3. **Delete conversation**: Click ✕ button
4. **Toggle history**: Click "History ▶" button

## Reactions Page Fix

The reactions page should work correctly. If it's not showing:
1. Check browser console for errors
2. Verify backend is running: `curl http://localhost:8000/api/reactions`
3. Check Angular dev server is running on port 4200
4. Clear browser cache and reload

## Testing

```bash
# Start backend and frontend
./run.sh

# Access at http://localhost:4200
# Try creating multiple conversations
# Check localStorage in browser DevTools
```

## Next Steps

To add conversation history to Dioxus standalone:
- Use `web_sys::window().local_storage()` for persistence
- Similar structure with signals for reactive updates
