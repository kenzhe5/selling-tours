import { AsyncPipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Observable } from 'rxjs';
import { TourApiService } from '@core/api/tour-api.service';
import { PaginatedTours, TourFilters } from '@core/models/api.models';
import { FilterPanelComponent } from '@shared/filter-panel/filter-panel.component';
import { TourCardComponent } from '@shared/tour-card/tour-card.component';

@Component({
  selector: 'app-tour-list-page',
  imports: [AsyncPipe, FilterPanelComponent, TourCardComponent, RouterLink],
  templateUrl: './tour-list-page.component.html',
})
export class TourListPageComponent implements OnInit {
  private readonly tourApi = inject(TourApiService);

  readonly filters = signal<TourFilters>({ sort: 'rating_desc', page: 1 });
  readonly countries$ = this.tourApi.getCountries();
  tours$!: Observable<PaginatedTours>;

  ngOnInit(): void {
    this.loadTours();
  }

  applyFilters(filters: TourFilters): void {
    this.filters.set(filters);
    this.loadTours();
  }

  resetFilters(): void {
    this.filters.set({ sort: 'rating_desc', page: 1 });
    this.loadTours();
  }

  private loadTours(): void {
    this.tours$ = this.tourApi.getTours(this.filters());
  }
}
