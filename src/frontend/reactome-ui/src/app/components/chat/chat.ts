import { Component, ViewChild, ElementRef, ChangeDetectorRef, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { marked } from 'marked';
import { ApiService, ChatMessage } from '../../services/api';

interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  timestamp: number;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css',
})
export class Chat implements OnInit {
  @ViewChild('messageContainer') messageContainer!: ElementRef;

  conversations: Conversation[] = [];
  currentConversationId: string | null = null;
  messages: ChatMessage[] = [];
  inputText = '';
  loading = false;
  statusMessage = 'Thinking...';
  expandedDetail = -1;
  showHistory = false;

  sampleQueries = [
    'Design a 3-tail ionizable lipid with amine heads',
    'Which reactions work for epoxide-based tails?',
    'What are the issues with reaction 10012?',
    'Explain the MCTS tree structure for LNP design',
  ];

  constructor(private api: ApiService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.loadConversations();
    if (this.conversations.length === 0) {
      this.newConversation();
    } else {
      this.loadConversation(this.conversations[0].id);
    }
  }

  newConversation() {
    const id = Date.now().toString();
    const conv: Conversation = {
      id,
      title: 'New Conversation',
      messages: [],
      timestamp: Date.now(),
    };
    this.conversations.unshift(conv);
    this.currentConversationId = id;
    this.messages = [];
    this.saveConversations();
  }

  loadConversation(id: string) {
    const conv = this.conversations.find(c => c.id === id);
    if (conv) {
      this.currentConversationId = id;
      this.messages = conv.messages;
      this.scrollToBottom();
    }
  }

  deleteConversation(id: string, event: Event) {
    event.stopPropagation();
    this.conversations = this.conversations.filter(c => c.id !== id);
    if (this.currentConversationId === id) {
      if (this.conversations.length > 0) {
        this.loadConversation(this.conversations[0].id);
      } else {
        this.newConversation();
      }
    }
    this.saveConversations();
  }

  private loadConversations() {
    const stored = localStorage.getItem('lnp_conversations');
    if (stored) {
      this.conversations = JSON.parse(stored);
      // Keep only last 10
      this.conversations = this.conversations.slice(0, 10);
    }
  }

  private saveConversations() {
    // Keep only last 10 conversations
    this.conversations = this.conversations.slice(0, 10);
    localStorage.setItem('lnp_conversations', JSON.stringify(this.conversations));
  }

  private updateCurrentConversation() {
    const conv = this.conversations.find(c => c.id === this.currentConversationId);
    if (conv) {
      conv.messages = this.messages;
      conv.timestamp = Date.now();
      // Update title from first user message
      const firstUser = this.messages.find(m => m.role === 'user');
      if (firstUser) {
        conv.title = firstUser.content.slice(0, 50) + (firstUser.content.length > 50 ? '...' : '');
      }
      this.saveConversations();
    }
  }

  sendMessage(text: string) {
    if (!text.trim() || this.loading) return;
    this.messages.push({ role: 'user', content: text });
    this.updateCurrentConversation();
    this.inputText = '';
    this.loading = true;
    this.statusMessage = 'Thinking...';

    this.api.chatStream(
      text,
      (status) => {
        this.statusMessage = status;
        this.cdr.markForCheck();
      },
      (answer) => {
        this.messages.push({ role: 'assistant', content: answer });
        this.updateCurrentConversation();
        this.cdr.markForCheck();
        this.scrollToBottom();
      },
      (details) => {
        const last = this.messages[this.messages.length - 1];
        if (last?.role === 'assistant') last.details = details;
        this.updateCurrentConversation();
        this.cdr.markForCheck();
      },
      () => {
        this.loading = false;
        this.cdr.markForCheck();
        this.scrollToBottom();
      }
    );
    this.scrollToBottom();
  }

  getDetail(msg: ChatMessage, key: string): string {
    return (msg.details as any)?.[key] ?? '';
  }

  renderMd(text: string): string {
    return marked.parse(text, { async: false }) as string;
  }

  formatDate(timestamp: number): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  }

  private scrollToBottom() {
    setTimeout(() => {
      const el = this.messageContainer?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    }, 50);
  }
}
