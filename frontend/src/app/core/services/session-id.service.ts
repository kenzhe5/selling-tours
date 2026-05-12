import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class SessionIdService {
  private readonly key = 'selling-tours-session-id';

  getSessionId(): string {
    const existing = sessionStorage.getItem(this.key);
    if (existing) {
      return existing;
    }

    const sessionId = crypto.randomUUID();
    sessionStorage.setItem(this.key, sessionId);
    return sessionId;
  }
}
