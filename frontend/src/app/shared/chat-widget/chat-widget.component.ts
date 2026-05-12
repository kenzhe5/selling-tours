import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AgentApiService } from '@core/api/agent-api.service';
import { ChatMessage } from '@core/models/api.models';
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
  private readonly sessionIdService = inject(SessionIdService);

  readonly open = signal(false);
  readonly message = signal('');
  readonly loading = signal(false);
  readonly messages = signal<ChatMessage[]>([
    {
      role: 'assistant',
      text: 'Tell me your country, budget, dates, or vibe. I will suggest tours using the same /api/agent/chat contract.',
    },
  ]);

  toggle(): void {
    this.open.update((value) => !value);
  }

  send(): void {
    const text = this.message().trim();
    if (!text || this.loading()) {
      return;
    }

    this.messages.update((items) => [...items, { role: 'user', text }]);
    this.message.set('');
    this.loading.set(true);

    this.agentApi
      .chat({
        session_id: this.sessionIdService.getSessionId(),
        message: text,
      })
      .subscribe({
        next: (response) => {
          this.messages.update((items) => [
            ...items,
            {
              role: 'assistant',
              text: response.reply,
              suggested_tour_ids: response.suggested_tour_ids,
            },
          ]);
          this.loading.set(false);
        },
        error: () => {
          this.messages.update((items) => [
            ...items,
            { role: 'assistant', text: 'The agent service is unavailable. Core browsing and booking still work.' },
          ]);
          this.loading.set(false);
        },
      });
  }
}
