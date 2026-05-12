import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ingestSseChunks } from './agent-stream.utils';
import { environment } from '@env/environment';
import {
  AgentChatRequest,
  AgentChatResponse,
  AgentChatStreamEvent,
} from '@core/models/api.models';

@Injectable({ providedIn: 'root' })
export class AgentApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  chat(body: AgentChatRequest): Observable<AgentChatResponse> {
    return this.http.post<AgentChatResponse>(`${this.apiUrl}/api/agent/chat`, body);
  }

  /** POST SSE stream: step messages then final `{ event: done, reply, suggested_tour_ids }`. */
  chatStream(body: AgentChatRequest): Observable<AgentChatStreamEvent> {
    return new Observable<AgentChatStreamEvent>((subscriber) => {
      const url = `${this.apiUrl}/api/agent/chat/stream`;
      const ctrl = new AbortController();
      let cancelled = false;

      void (async () => {
        try {
          const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
            body: JSON.stringify(body),
            signal: ctrl.signal,
          });
          if (!resp.ok || !resp.body) {
            subscriber.error(new Error(`stream_http_${resp.status}`));
            return;
          }

          const reader = resp.body.getReader();
          const decoder = new TextDecoder();
          let carry = '';

          while (!cancelled) {
            const { value, done } = await reader.read();
            if (done) {
              break;
            }
            const text = decoder.decode(value, { stream: true });
            const { lines, remainder } = ingestSseChunks(carry, text);
            carry = remainder;

            for (const payload of lines) {
              const event = typeof payload['event'] === 'string' ? payload['event'] : '';
              if (event === 'step' && typeof payload['detail'] === 'string') {
                subscriber.next({ kind: 'step', detail: payload['detail'] });
              } else if (event === 'done') {
                const reply = typeof payload['reply'] === 'string' ? payload['reply'] : '';
                const ids = payload['suggested_tour_ids'];
                const suggested_ids = Array.isArray(ids)
                  ? (ids.filter((id) => typeof id === 'string') as string[])
                  : [];
                const response: AgentChatResponse = { reply, suggested_tour_ids: suggested_ids };
                subscriber.next({ kind: 'done', response });
                subscriber.complete();
                return;
              } else if (event === 'error') {
                const message =
                  typeof payload['message'] === 'string' ? payload['message'] : 'Stream failed';
                subscriber.next({ kind: 'error', message });
                subscriber.complete();
                return;
              }
            }
          }

          subscriber.error(new Error('stream_incomplete'));
        } catch (e) {
          if (!cancelled) {
            subscriber.error(e instanceof Error ? e : new Error('stream_unknown'));
          }
        }
      })();

      return () => {
        cancelled = true;
        ctrl.abort();
      };
    });
  }
}
