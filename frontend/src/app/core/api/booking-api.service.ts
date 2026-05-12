import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { Booking, CreateBookingRequest } from '@core/models/api.models';

@Injectable({ providedIn: 'root' })
export class BookingApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  createBooking(body: CreateBookingRequest): Observable<Booking> {
    return this.http.post<Booking>(`${this.apiUrl}/api/bookings`, body);
  }

  getBookingsByEmail(email: string): Observable<Booking[]> {
    const params = new HttpParams().set('email', email);
    return this.http.get<Booking[]>(`${this.apiUrl}/api/bookings`, { params });
  }
}
