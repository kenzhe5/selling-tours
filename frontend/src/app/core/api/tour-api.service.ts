import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, catchError, map, of } from 'rxjs';
import { environment } from '@env/environment';
import { PaginatedTours, Tour, TourFilters } from '@core/models/api.models';

@Injectable({ providedIn: 'root' })
export class TourApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  getTours(filters: TourFilters = {}): Observable<PaginatedTours> {
    return this.http.get<PaginatedTours>(`${this.apiUrl}/api/tours`, {
      params: this.toParams(filters),
    });
  }

  getTour(id: string): Observable<Tour | undefined> {
    if (!id) {
      return of(undefined);
    }
    return this.http.get<Tour>(`${this.apiUrl}/api/tours/${id}`).pipe(
      catchError(() => of(undefined)),
    );
  }

  getCountries(): Observable<string[]> {
    return this.http
      .get<{ items: string[] }>(`${this.apiUrl}/api/countries`)
      .pipe(map((body) => body.items));
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
