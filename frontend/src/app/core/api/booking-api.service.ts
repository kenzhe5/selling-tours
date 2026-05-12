import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, delay, of } from 'rxjs';
import { environment } from '@env/environment';
import { Booking, CreateBookingRequest } from '@core/models/api.models';
import { MockApiService } from './mock-api.service';

@Injectable({ providedIn: 'root' })
export class BookingApiService {
  private readonly http = inject(HttpClient);
  private readonly mockApi = inject(MockApiService);
  private readonly apiUrl = environment.apiUrl;

  createBooking(body: CreateBookingRequest): Observable<Booking> {
    if (environment.useMocks) {
      return of(this.mockApi.createBooking(body)).pipe(delay(350));
    }

    return this.http.post<Booking>(`${this.apiUrl}/api/bookings`, body);
  }

  getBookingsByEmail(email: string): Observable<Booking[]> {
    if (environment.useMocks) {
      return of(this.mockApi.getBookingsByEmail(email)).pipe(delay(250));
    }

    const params = new HttpParams().set('email', email);
    return this.http.get<Booking[]>(`${this.apiUrl}/api/bookings`, { params });
  }
}
