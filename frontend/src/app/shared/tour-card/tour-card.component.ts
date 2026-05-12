import { CurrencyPipe, DatePipe } from '@angular/common';
import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Tour } from '@core/models/api.models';

@Component({
  selector: 'app-tour-card',
  imports: [CurrencyPipe, DatePipe, RouterLink],
  templateUrl: './tour-card.component.html',
  styleUrl: './tour-card.component.scss',
})
export class TourCardComponent {
  readonly tour = input.required<Tour>();
}
