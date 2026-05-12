import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { AgentChatRequest, AgentChatResponse } from '@core/models/api.models';

@Injectable({ providedIn: 'root' })
export class AgentApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  chat(body: AgentChatRequest): Observable<AgentChatResponse> {
    return this.http.post<AgentChatResponse>(`${this.apiUrl}/api/agent/chat`, body);
  }
}
