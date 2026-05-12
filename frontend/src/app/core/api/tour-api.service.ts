import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, delay, of } from 'rxjs';
import { environment } from '@env/environment';
import { MockApiService } from './mock-api.service';
import { PaginatedTours, Tour, TourFilters } from '@core/models/api.models';

@Injectable({ providedIn: 'root' })
export class TourApiService {
  private readonly http = inject(HttpClient);
  private readonly mockApi = inject(MockApiService);
  private readonly apiUrl = environment.apiUrl;

  getTours(filters: TourFilters = {}): Observable<PaginatedTours> {
    if (environment.useMocks) {
      return of(this.mockApi.getTours(filters)).pipe(delay(250));
    }

    return this.http.get<PaginatedTours>(`${this.apiUrl}/api/tours`, {
      params: this.toParams(filters),
    });
  }

  getTour(id: string): Observable<Tour | undefined> {
    if (environment.useMocks) {
      return of(this.mockApi.getTour(id)).pipe(delay(180));
    }

    return this.http.get<Tour>(`${this.apiUrl}/api/tours/${id}`);
  }

  getCountries(): Observable<string[]> {
    if (environment.useMocks) {
      return of(this.mockApi.getCountries()).pipe(delay(120));
    }

    return this.http.get<string[]>(`${this.apiUrl}/api/countries`);
  }

  private toParams(filters: TourFilters): HttpParams {
    let params = new HttpParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, String(value));
      }
    });

    return params;
  }
}
