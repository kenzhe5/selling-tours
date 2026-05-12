import { Component, NgZone, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { forkJoin, map, of, switchMap } from 'rxjs';
import { AgentApiService } from '@core/api/agent-api.service';
import { TourApiService } from '@core/api/tour-api.service';
import type { AgentChatResponse, ChatMessage, SuggestedTourChip } from '@core/models/api.models';
import { SessionIdService } from '@core/services/session-id.service';

@Component({
  selector: 'app-chat-widget',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './chat-widget.component.html',
  styleUrl: './chat-widget.component.scss',
})
export class ChatWidgetComponent {
  private readonly agentApi = inject(AgentApiService);
  private readonly tourApi = inject(TourApiService);
  private readonly sessionIdService = inject(SessionIdService);
  private readonly zone = inject(NgZone);

  readonly open = signal(false);
  readonly message = signal('');
  readonly loading = signal(false);
  readonly reasoningStep = signal('');
  readonly messages = signal<ChatMessage[]>([
    {
      role: 'assistant',
      text: 'Tell me your country, budget, dates, or vibe — I will suggest real tours from our catalog.',
    },
  ]);

  toggle(): void {
    this.open.update((value) => !value);
  }

  chipDisplayLabel(chip: SuggestedTourChip, index: number): string {
    const t = chip.title.trim();
    const looksTechnical =
      !t ||
      t === chip.id ||
      t.toLowerCase() === chip.id.replace(/-/g, '').toLowerCase() ||
      this.looksLikeUuidOrHexDump(t);

    if (looksTechnical) {
      return `Suggested trip ${index}`;
    }
    return t;
  }

  chipAriaLabel(chip: SuggestedTourChip, index: number): string {
    const label = this.chipDisplayLabel(chip, index);
    return `${label}, open tour details`;
  }

  useExample(prompt: string): void {
    this.message.set(prompt);
  }

  send(): void {
    const text = this.message().trim();
    if (!text || this.loading()) {
      return;
    }

    this.messages.update((items) => [...items, { role: 'user', text }]);
    this.message.set('');
    this.loading.set(true);
    this.reasoningStep.set('Sending…');

    const payload = {
      session_id: this.sessionIdService.getSessionId(),
      message: text,
    };

    this.agentApi.chatStream(payload).subscribe({
      next: (event) =>
        this.zone.run(() => {
          if (event.kind === 'step') {
            this.reasoningStep.set(event.detail);
            return;
          }
          if (event.kind === 'error') {
            this.reasoningStep.set('Continuing without live steps…');
            this.finishWithJsonFallback(payload);
            return;
          }
          if (event.kind === 'done') {
            this.mergeChipsThenAppend(event.response);
          }
        }),
      error: () =>
        this.zone.run(() => {
          this.reasoningStep.set('Fetching reply…');
          this.finishWithJsonFallback(payload);
        }),
      complete: () => {
        /* `done` or `error` event handles terminal state */
      },
    });
  }

  private mergeChipsThenAppend(response: AgentChatResponse): void {
    const ids = response.suggested_tour_ids.slice(0, 3);
    const reply = response.reply;

    const push = (chips?: SuggestedTourChip[]) => {
      this.zone.run(() => {
        this.messages.update((items) => [
          ...items,
          {
            role: 'assistant',
            text: reply,
            ...(chips && chips.length > 0 ? { suggested_tours: chips } : {}),
          },
        ]);
        this.loading.set(false);
        this.reasoningStep.set('');
      });
    };

    if (ids.length === 0) {
      push([]);
      return;
    }

    forkJoin(ids.map((id) => this.tourApi.getTour(id))).subscribe({
      next: (tours) => {
        const chips = ids.map((id, i) => {
          const name = tours[i]?.title?.trim();
          return {
            id,
            title: name && name.length > 0 ? name : 'View tour',
          };
        });
        push(chips);
      },
      error: () => push(),
    });
  }

  private finishWithJsonFallback(body: { session_id: string; message: string }): void {
    this.agentApi
      .chat(body)
      .pipe(
        switchMap((response) => {
          const ids = response.suggested_tour_ids.slice(0, 3);
          if (ids.length === 0) {
            return of({ reply: response.reply, suggested_tours: [] as SuggestedTourChip[] });
          }
          return forkJoin(ids.map((id) => this.tourApi.getTour(id))).pipe(
            map((tours) =>
              ids.map((id, i) => {
                const name = tours[i]?.title?.trim();
                return {
                  id,
                  title: name && name.length > 0 ? name : 'View tour',
                };
              }),
            ),
            map((suggested_tours) => ({ reply: response.reply, suggested_tours })),
          );
        }),
      )
      .subscribe({
        next: ({ reply, suggested_tours }) => {
          this.zone.run(() => {
            this.messages.update((items) => [
              ...items,
              {
                role: 'assistant',
                text: reply,
                ...(suggested_tours.length > 0 ? { suggested_tours } : {}),
              },
            ]);
            this.loading.set(false);
            this.reasoningStep.set('');
          });
        },
        error: () => {
          this.zone.run(() => {
            this.messages.update((items) => [
              ...items,
              { role: 'assistant', text: 'The agent service is unavailable. Core browsing and booking still work.' },
            ]);
            this.loading.set(false);
            this.reasoningStep.set('');
          });
        },
      });
  }

  private looksLikeUuidOrHexDump(raw: string): boolean {
    const collapsed = raw.replace(/\s+/g, '').replace(/-/g, '');
    if (/^[0-9a-f]{32}$/i.test(collapsed)) {
      return true;
    }
    return /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(raw.trim());
  }
}
