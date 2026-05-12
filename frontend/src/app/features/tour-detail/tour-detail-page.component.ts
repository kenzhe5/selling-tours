import { AsyncPipe, CurrencyPipe, DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Observable, map, switchMap } from 'rxjs';
import { BookingApiService } from '@core/api/booking-api.service';
import { TourApiService } from '@core/api/tour-api.service';
import { Booking, Tour } from '@core/models/api.models';

@Component({
  selector: 'app-tour-detail-page',
  imports: [AsyncPipe, CurrencyPipe, DatePipe, ReactiveFormsModule, RouterLink],
  templateUrl: './tour-detail-page.component.html',
})
export class TourDetailPageComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly tourApi = inject(TourApiService);
  private readonly bookingApi = inject(BookingApiService);
  private readonly fb = inject(FormBuilder);

  readonly submitting = signal(false);
  readonly submittedBooking = signal<Booking | null>(null);
  readonly submitError = signal('');
  tour$!: Observable<Tour | undefined>;

  readonly form = this.fb.nonNullable.group({
    user_name: ['', [Validators.required, Validators.minLength(2)]],
    user_email: ['', [Validators.required, Validators.email]],
    start_date: ['', Validators.required],
    num_people: [2, [Validators.required, Validators.min(1), Validators.max(12)]],
  });

  ngOnInit(): void {
    this.tour$ = this.route.paramMap.pipe(
      map((params) => params.get('id') ?? ''),
      switchMap((id) => this.tourApi.getTour(id)),
    );
  }

  submit(tour: Tour): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.submitting.set(true);
    this.submitError.set('');
    this.bookingApi
      .createBooking({
        tour_id: tour.id,
        user_name: this.form.controls.user_name.value,
        user_email: this.form.controls.user_email.value,
        start_date: this.form.controls.start_date.value,
        num_people: this.form.controls.num_people.value,
      })
      .subscribe({
        next: (booking) => {
          this.submittedBooking.set(booking);
          this.submitting.set(false);
        },
        error: () => {
          this.submitError.set('Booking could not be created. Please check the data and try again.');
          this.submitting.set(false);
        },
      });
  }
}
