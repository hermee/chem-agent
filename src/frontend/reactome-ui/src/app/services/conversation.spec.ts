/**
 * Tests for conversation service logic.
 * Tests the pure state management logic without Angular signals.
 */
import { describe, it, expect, beforeEach } from 'vitest';

interface Conversation {
  id: string;
  title: string;
  messages: { role: string; content: string }[];
  timestamp: number;
}

/** Extracted conversation management logic (mirrors ConversationService) */
class ConversationStore {
  conversations: Conversation[] = [];
  currentId: string | null = null;

  constructor() {
    const stored = localStorage.getItem('lnp_conversations');
    if (stored) {
      try {
        this.conversations = JSON.parse(stored).slice(0, 20);
      } catch {
        this.conversations = [];
      }
    }
    this.newConversation();
  }

  get current(): Conversation | null {
    return this.conversations.find((c) => c.id === this.currentId) ?? null;
  }

  newConversation() {
    const id = Date.now().toString() + Math.random().toString(36).slice(2, 6);
    const conv: Conversation = { id, title: 'New Conversation', messages: [], timestamp: Date.now() };
    this.conversations.unshift(conv);
    this.currentId = id;
    this.save();
  }

  select(id: string) {
    this.currentId = id;
  }

  delete(id: string) {
    this.conversations = this.conversations.filter((c) => c.id !== id);
    if (this.currentId === id) {
      this.conversations.length > 0
        ? (this.currentId = this.conversations[0].id)
        : this.newConversation();
    }
    this.save();
  }

  updateCurrent(messages: { role: string; content: string }[]) {
    this.conversations = this.conversations.map((c) => {
      if (c.id !== this.currentId) return c;
      const firstUser = messages.find((m) => m.role === 'user');
      return {
        ...c,
        messages,
        timestamp: Date.now(),
        title: firstUser
          ? firstUser.content.slice(0, 50) + (firstUser.content.length > 50 ? '...' : '')
          : c.title,
      };
    });
    this.save();
  }

  private save() {
    localStorage.setItem('lnp_conversations', JSON.stringify(this.conversations.slice(0, 20)));
  }

  static formatDate(ts: number): string {
    const days = Math.floor((Date.now() - ts) / 86400000);
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    return new Date(ts).toLocaleDateString();
  }
}

describe('ConversationStore', () => {
  beforeEach(() => localStorage.clear());

  it('should create initial conversation', () => {
    const store = new ConversationStore();
    expect(store.conversations.length).toBe(1);
    expect(store.currentId).toBeTruthy();
    expect(store.current).toBeTruthy();
    expect(store.current!.title).toBe('New Conversation');
  });

  it('should create additional conversations', () => {
    const store = new ConversationStore();
    store.newConversation();
    expect(store.conversations.length).toBe(2);
  });

  it('should update current conversation messages', () => {
    const store = new ConversationStore();
    store.updateCurrent([{ role: 'user', content: 'hello' }]);
    expect(store.current!.messages).toEqual([{ role: 'user', content: 'hello' }]);
  });

  it('should set title from first user message', () => {
    const store = new ConversationStore();
    store.updateCurrent([{ role: 'user', content: 'Design a 3-tail lipid with amine heads' }]);
    expect(store.current!.title).toContain('Design a 3-tail lipid');
  });

  it('should truncate long titles', () => {
    const store = new ConversationStore();
    store.updateCurrent([{ role: 'user', content: 'x'.repeat(100) }]);
    expect(store.current!.title.length).toBeLessThanOrEqual(53); // 50 + "..."
  });

  it('should delete a conversation', () => {
    const store = new ConversationStore();
    store.newConversation();
    const id = store.currentId!;
    store.delete(id);
    expect(store.conversations.find((c) => c.id === id)).toBeUndefined();
  });

  it('should switch current after deleting active', () => {
    const store = new ConversationStore();
    store.newConversation();
    const toDelete = store.currentId!;
    const otherId = store.conversations.find((c) => c.id !== toDelete)!.id;
    store.delete(toDelete);
    expect(store.currentId).toBe(otherId);
  });

  it('should select a conversation', () => {
    const store = new ConversationStore();
    store.newConversation();
    const first = store.conversations[1].id;
    store.select(first);
    expect(store.currentId).toBe(first);
  });

  it('should persist to localStorage', () => {
    const store = new ConversationStore();
    store.updateCurrent([{ role: 'user', content: 'test' }]);
    const stored = JSON.parse(localStorage.getItem('lnp_conversations')!);
    expect(stored.length).toBeGreaterThan(0);
    expect(stored[0].messages[0].content).toBe('test');
  });

  it('should limit stored conversations to 20', () => {
    const store = new ConversationStore();
    for (let i = 0; i < 25; i++) store.newConversation();
    const stored = JSON.parse(localStorage.getItem('lnp_conversations')!);
    expect(stored.length).toBeLessThanOrEqual(20);
  });

  it('should handle corrupted localStorage gracefully', () => {
    localStorage.setItem('lnp_conversations', '{broken json');
    const store = new ConversationStore();
    expect(store.conversations.length).toBe(1); // fresh start
  });
});

describe('formatDate', () => {
  it('should return Today for current time', () => {
    expect(ConversationStore.formatDate(Date.now())).toBe('Today');
  });

  it('should return Yesterday', () => {
    expect(ConversationStore.formatDate(Date.now() - 86400000)).toBe('Yesterday');
  });

  it('should return Xd ago for recent dates', () => {
    expect(ConversationStore.formatDate(Date.now() - 3 * 86400000)).toBe('3d ago');
  });

  it('should return formatted date for old dates', () => {
    const old = Date.now() - 30 * 86400000;
    const result = ConversationStore.formatDate(old);
    expect(result).not.toBe('Today');
    expect(result).toMatch(/\d/); // contains a number (date)
  });
});
