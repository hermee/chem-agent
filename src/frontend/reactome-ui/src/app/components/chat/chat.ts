import { Component, ViewChild, ElementRef, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { marked } from 'marked';
import { ApiService, ChatMessage } from '../../services/api';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css',
})
export class Chat {
  @ViewChild('messageContainer') messageContainer!: ElementRef;

  messages: ChatMessage[] = [];
  inputText = '';
  loading = false;
  statusMessage = 'Thinking...';
  expandedDetail = -1;

  sampleQueries = [
    'Design a 3-tail ionizable lipid with amine heads',
    'Which reactions work for epoxide-based tails?',
    'What are the issues with reaction 10012?',
    'Explain the MCTS tree structure for LNP design',
  ];

  constructor(private api: ApiService, private cdr: ChangeDetectorRef) {}

  sendMessage(text: string) {
    if (!text.trim() || this.loading) return;
    this.messages.push({ role: 'user', content: text });
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
        this.cdr.markForCheck();
        this.scrollToBottom();
      },
      (details) => {
        const last = this.messages[this.messages.length - 1];
        if (last?.role === 'assistant') last.details = details;
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

  private scrollToBottom() {
    setTimeout(() => {
      const el = this.messageContainer?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    }, 50);
  }
}
