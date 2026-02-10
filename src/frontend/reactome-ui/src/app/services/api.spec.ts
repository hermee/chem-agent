/**
 * Tests for API service logic.
 * We test the pure functions and SSE parsing logic without Angular DI.
 */
import { describe, it, expect, vi } from 'vitest';

/** Extracted buildHistory logic (mirrors ApiService.buildHistory) */
function buildHistory(messages: { role: string; content: string }[]): string {
  return messages
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .slice(-10)
    .map((m) => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content.slice(0, 500)}`)
    .join('\n');
}

/** Extracted SSE line parser (mirrors _handleSSE inner logic) */
function parseSSELine(line: string): { type: string; [key: string]: any } | null {
  if (!line.startsWith('data: ')) return null;
  const data = line.slice(6);
  if (data === '[DONE]') return { type: 'done' };
  try {
    return JSON.parse(data);
  } catch {
    return null;
  }
}

describe('buildHistory', () => {
  it('should format user and assistant messages', () => {
    const history = buildHistory([
      { role: 'user', content: 'hello' },
      { role: 'assistant', content: 'hi there' },
    ]);
    expect(history).toBe('User: hello\nAssistant: hi there');
  });

  it('should filter out status messages', () => {
    const history = buildHistory([
      { role: 'user', content: 'hello' },
      { role: 'status', content: 'thinking...' },
      { role: 'assistant', content: 'response' },
    ]);
    expect(history).not.toContain('thinking');
    expect(history).toContain('User: hello');
    expect(history).toContain('Assistant: response');
  });

  it('should keep only last 10 messages', () => {
    const messages = Array.from({ length: 20 }, (_, i) => ({
      role: 'user',
      content: `msg ${i}`,
    }));
    const history = buildHistory(messages);
    expect(history).not.toContain('msg 0');
    expect(history).not.toContain('msg 9');
    expect(history).toContain('msg 10');
    expect(history).toContain('msg 19');
  });

  it('should truncate long messages to 500 chars', () => {
    const longMsg = 'x'.repeat(1000);
    const history = buildHistory([{ role: 'user', content: longMsg }]);
    expect(history.length).toBeLessThan(600);
  });

  it('should return empty string for empty messages', () => {
    expect(buildHistory([])).toBe('');
  });
});

describe('parseSSELine', () => {
  it('should parse status events', () => {
    const result = parseSSELine('data: {"type":"status","step":"retrieve","message":"Searching..."}');
    expect(result).toEqual({ type: 'status', step: 'retrieve', message: 'Searching...' });
  });

  it('should parse answer events', () => {
    const result = parseSSELine('data: {"type":"answer","content":"Here is the answer"}');
    expect(result).toEqual({ type: 'answer', content: 'Here is the answer' });
  });

  it('should parse details events', () => {
    const result = parseSSELine('data: {"type":"details","reaction_analysis":"a","design_rules_check":"b","synthesis_plan":"c"}');
    expect(result!.type).toBe('details');
    expect(result!['reaction_analysis']).toBe('a');
  });

  it('should parse error events', () => {
    const result = parseSSELine('data: {"type":"error","message":"Bedrock timeout"}');
    expect(result).toEqual({ type: 'error', message: 'Bedrock timeout' });
  });

  it('should handle [DONE] marker', () => {
    expect(parseSSELine('data: [DONE]')).toEqual({ type: 'done' });
  });

  it('should return null for non-data lines', () => {
    expect(parseSSELine('')).toBeNull();
    expect(parseSSELine('event: message')).toBeNull();
    expect(parseSSELine(': comment')).toBeNull();
  });

  it('should return null for malformed JSON', () => {
    expect(parseSSELine('data: {broken')).toBeNull();
  });
});
