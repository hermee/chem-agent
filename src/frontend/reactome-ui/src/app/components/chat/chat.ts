import { Component, ViewChild, ElementRef, ChangeDetectorRef, effect } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { marked } from 'marked';
import { ApiService, ChatMessage } from '../../services/api';
import { ConversationService } from '../../services/conversation';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css',
})
export class Chat {
  @ViewChild('messageContainer') messageContainer!: ElementRef;
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  messages: ChatMessage[] = [];
  inputText = '';
  loading = false;
  statusMessage = 'Thinking...';
  expandedDetail = -1;
  attachedFiles: File[] = [];

  sampleQueries = [
    'Design a 3-tail ionizable lipid with amine heads',
    'Which reactions work for epoxide-based tails?',
    'What are the issues with reaction 10012?',
    'Explain the MCTS tree structure for LNP design',
  ];

  constructor(private api: ApiService, private cdr: ChangeDetectorRef, public convService: ConversationService) {
    effect(() => {
      const conv = this.convService.current();
      this.messages = conv ? [...conv.messages] : [];
      this.scrollToBottom();
    });
  }

  onFilesSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.attachedFiles = [...this.attachedFiles, ...Array.from(input.files)];
      input.value = '';
    }
  }

  removeFile(index: number) { this.attachedFiles.splice(index, 1); }

  formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + 'B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + 'KB';
    return (bytes / 1048576).toFixed(1) + 'MB';
  }

  sendMessage(text: string) {
    if ((!text.trim() && this.attachedFiles.length === 0) || this.loading) return;
    this.messages.push({ role: 'user', content: text });
    this.convService.updateCurrent(this.messages);
    this.inputText = '';
    this.loading = true;
    this.statusMessage = 'Thinking...';

    const files = [...this.attachedFiles];
    this.attachedFiles = [];

    const callbacks = {
      onStatus: (status: string) => { this.statusMessage = status; this.cdr.markForCheck(); },
      onAnswer: (answer: string) => {
        this.messages.push({ role: 'assistant', content: answer });
        this.convService.updateCurrent(this.messages);
        this.cdr.markForCheck();
        this.scrollToBottom();
      },
      onDetails: (details: any) => {
        const last = this.messages[this.messages.length - 1];
        if (last?.role === 'assistant') last.details = details;
        this.convService.updateCurrent(this.messages);
        this.cdr.markForCheck();
      },
      onError: (err: string) => {
        this.messages.push({ role: 'assistant', content: `⚠️ ${err}` });
        this.convService.updateCurrent(this.messages);
        this.cdr.markForCheck();
        this.scrollToBottom();
      },
      onDone: () => { this.loading = false; this.cdr.markForCheck(); this.scrollToBottom(); },
    };

    // Pass existing messages so the backend gets conversation history
    if (files.length > 0) {
      this.api.chatStreamWithFiles(text, files, this.messages, callbacks.onStatus, callbacks.onAnswer, callbacks.onDetails, callbacks.onError, callbacks.onDone);
    } else {
      this.api.chatStream(text, this.messages, callbacks.onStatus, callbacks.onAnswer, callbacks.onDetails, callbacks.onError, callbacks.onDone);
    }
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
