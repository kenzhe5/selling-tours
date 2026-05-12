import { AsyncPipe, DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Observable, of } from 'rxjs';
import { BookingApiService } from '@core/api/booking-api.service';
import { Booking } from '@core/models/api.models';

@Component({
  selector: 'app-my-bookings-page',
  imports: [AsyncPipe, DatePipe, ReactiveFormsModule, RouterLink],
  templateUrl: './my-bookings-page.component.html',
})
export class MyBookingsPageComponent {
  private readonly bookingApi = inject(BookingApiService);
  private readonly fb = inject(FormBuilder);

  readonly searched = signal(false);
  bookings$: Observable<Booking[]> = of([]);

  readonly form = this.fb.nonNullable.group({
    email: ['demo@example.com', [Validators.required, Validators.email]],
  });

  search(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.searched.set(true);
    this.bookings$ = this.bookingApi.getBookingsByEmail(this.form.controls.email.value);
  }
}
