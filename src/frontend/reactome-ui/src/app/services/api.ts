import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Reaction {
  id: number;
  name: string;
  reactants: string;
  smarts_reactants?: string;
  smarts_product?: string;
  warning?: string;
}

export interface SmilesResult {
  smiles: string;
  scores: Record<string, number>;
  svg: string;
  error?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'status';
  content: string;
  details?: {
    reaction_analysis?: string;
    lipid_design_analysis?: string;
    generative_analysis?: string;
    prediction_analysis?: string;
    literature_context?: string;
    web_context?: string;
  };
}

export interface QueryResult {
  query: string;
  query_type: string;
  reaction_analysis: string;
  lipid_design_analysis: string;
  generative_analysis: string;
  prediction_analysis: string;
  literature_context: string;
  web_context: string;
  final_answer: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = '/api';

  constructor(private http: HttpClient) {}

  getHealth(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }

  getReactions(): Observable<{ reactions: Reaction[] }> {
    return this.http.get<{ reactions: Reaction[] }>(`${this.baseUrl}/reactions`);
  }

  getReactionSvgUrl(id: number): string {
    return `${this.baseUrl}/reactions/${id}/svg`;
  }

  analyzeSmiles(smiles: string): Observable<SmilesResult> {
    return this.http.post<SmilesResult>(`${this.baseUrl}/analyze-smiles`, { smiles });
  }

  queryAgent(query: string): Observable<QueryResult> {
    return this.http.post<QueryResult>(`${this.baseUrl}/query`, { query });
  }

  /** Build a condensed chat history string from messages for the backend. */
  private buildHistory(messages: ChatMessage[]): string {
    return messages
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .slice(-10)
      .map(m => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content.slice(0, 500)}`)
      .join('\n');
  }

  chatStream(
    message: string,
    existingMessages: ChatMessage[],
    onStatus: (msg: string) => void,
    onAnswer: (msg: string) => void,
    onDetails: (d: any) => void,
    onError: (msg: string) => void,
    onDone: () => void,
  ) {
    this._handleSSE(
      fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, chat_history: this.buildHistory(existingMessages) }),
      }),
      onStatus, onAnswer, onDetails, onError, onDone,
    );
  }

  chatStreamWithFiles(
    message: string,
    files: File[],
    existingMessages: ChatMessage[],
    onStatus: (msg: string) => void,
    onAnswer: (msg: string) => void,
    onDetails: (d: any) => void,
    onError: (msg: string) => void,
    onDone: () => void,
  ) {
    const formData = new FormData();
    formData.append('message', message);
    formData.append('chat_history', this.buildHistory(existingMessages));
    files.forEach(f => formData.append('files', f));
    this._handleSSE(
      fetch(`${this.baseUrl}/chat-with-files`, { method: 'POST', body: formData }),
      onStatus, onAnswer, onDetails, onError, onDone,
    );
  }

  private _handleSSE(
    fetchPromise: Promise<Response>,
    onStatus: (msg: string) => void,
    onAnswer: (msg: string) => void,
    onDetails: (d: any) => void,
    onError: (msg: string) => void,
    onDone: () => void,
  ) {
    const timeout = setTimeout(() => { onError('Request timed out after 5 minutes'); onDone(); }, 300_000);

    fetchPromise
      .then(async (response) => {
        if (!response.ok) {
          clearTimeout(timeout);
          onError(`Server error: ${response.status}`);
          onDone();
          return;
        }
        const reader = response.body!.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            const data = line.slice(6);
            if (data === '[DONE]') { clearTimeout(timeout); onDone(); return; }
            try {
              const parsed = JSON.parse(data);
              if (parsed.type === 'status') onStatus(parsed.message);
              else if (parsed.type === 'answer') onAnswer(parsed.content);
              else if (parsed.type === 'details') onDetails(parsed);
              else if (parsed.type === 'error') onError(parsed.message);
            } catch { /* skip malformed SSE lines */ }
          }
        }
        clearTimeout(timeout);
        onDone();
      })
      .catch((err) => {
        clearTimeout(timeout);
        onError(`Connection failed: ${err.message || 'Network error'}`);
        onDone();
      });
  }
}
