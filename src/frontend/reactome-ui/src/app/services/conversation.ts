import { Injectable, signal, computed } from '@angular/core';
import { ChatMessage } from './api';

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  timestamp: number;
}

@Injectable({ providedIn: 'root' })
export class ConversationService {
  conversations = signal<Conversation[]>([]);
  currentId = signal<string | null>(null);
  current = computed(() => this.conversations().find(c => c.id === this.currentId()) ?? null);

  constructor() {
    const stored = localStorage.getItem('lnp_conversations');
    if (stored) this.conversations.set(JSON.parse(stored).slice(0, 20));
    // Always start fresh on page load
    this.newConversation();
  }

  newConversation() {
    const id = Date.now().toString();
    const conv: Conversation = { id, title: 'New Conversation', messages: [], timestamp: Date.now() };
    this.conversations.update(list => [conv, ...list]);
    this.currentId.set(id);
    this.save();
  }

  select(id: string) { this.currentId.set(id); }

  delete(id: string) {
    this.conversations.update(list => list.filter(c => c.id !== id));
    if (this.currentId() === id) {
      const list = this.conversations();
      list.length > 0 ? this.currentId.set(list[0].id) : this.newConversation();
    }
    this.save();
  }

  updateCurrent(messages: ChatMessage[]) {
    this.conversations.update(list => list.map(c => {
      if (c.id !== this.currentId()) return c;
      const firstUser = messages.find(m => m.role === 'user');
      return { ...c, messages, timestamp: Date.now(), title: firstUser ? firstUser.content.slice(0, 50) + (firstUser.content.length > 50 ? '...' : '') : c.title };
    }));
    this.save();
  }

  private save() {
    localStorage.setItem('lnp_conversations', JSON.stringify(this.conversations().slice(0, 20)));
  }

  formatDate(ts: number): string {
    const days = Math.floor((Date.now() - ts) / 86400000);
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    return new Date(ts).toLocaleDateString();
  }
}
