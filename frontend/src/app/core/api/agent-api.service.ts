import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, delay, of } from 'rxjs';
import { environment } from '@env/environment';
import { AgentChatRequest, AgentChatResponse } from '@core/models/api.models';
import { MockApiService } from './mock-api.service';

@Injectable({ providedIn: 'root' })
export class AgentApiService {
  private readonly http = inject(HttpClient);
  private readonly mockApi = inject(MockApiService);
  private readonly apiUrl = environment.apiUrl;

  chat(body: AgentChatRequest): Observable<AgentChatResponse> {
    if (environment.useMocks) {
      return of(this.mockApi.chat(body.message)).pipe(delay(500));
    }

    return this.http.post<AgentChatResponse>(`${this.apiUrl}/api/agent/chat`, body);
  }
}
