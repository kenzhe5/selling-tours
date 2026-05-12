import { Component, computed, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TourFilters, TourSort } from '@core/models/api.models';

@Component({
  selector: 'app-filter-panel',
  imports: [FormsModule],
  templateUrl: './filter-panel.component.html',
})
export class FilterPanelComponent {
  readonly countries = input<string[]>([]);
  readonly filtersChange = output<TourFilters>();
  readonly resetFilters = output<void>();

  readonly country = signal('');
  readonly priceMin = signal<number | undefined>(undefined);
  readonly priceMax = signal<number | undefined>(undefined);
  readonly dateFrom = signal('');
  readonly dateTo = signal('');
  readonly sort = signal<TourSort>('rating_desc');

  readonly activeCount = computed(() => {
    return [this.country(), this.priceMin(), this.priceMax(), this.dateFrom(), this.dateTo()].filter(Boolean).length;
  });

  apply(): void {
    this.filtersChange.emit({
      country: this.country() || undefined,
      price_min: this.priceMin(),
      price_max: this.priceMax(),
      date_from: this.dateFrom() || undefined,
      date_to: this.dateTo() || undefined,
      sort: this.sort(),
      page: 1,
    });
  }

  reset(): void {
    this.country.set('');
    this.priceMin.set(undefined);
    this.priceMax.set(undefined);
    this.dateFrom.set('');
    this.dateTo.set('');
    this.sort.set('rating_desc');
    this.resetFilters.emit();
  }
}
