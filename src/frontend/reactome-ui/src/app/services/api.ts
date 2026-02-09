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
  details?: { reaction_analysis?: string; design_rules_check?: string; synthesis_plan?: string };
}

export interface QueryResult {
  query: string;
  reaction_analysis: string;
  design_rules_check: string;
  synthesis_plan: string;
  final_answer: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

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

  chatStream(message: string, onStatus: (msg: string) => void, onAnswer: (msg: string) => void, onDetails: (d: any) => void, onDone: () => void) {
    fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    }).then(async (response) => {
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
          if (data === '[DONE]') { onDone(); return; }
          try {
            const parsed = JSON.parse(data);
            if (parsed.type === 'status') onStatus(parsed.message);
            else if (parsed.type === 'answer') onAnswer(parsed.content);
            else if (parsed.type === 'details') onDetails(parsed);
          } catch {}
        }
      }
      onDone();
    });
  }
}
