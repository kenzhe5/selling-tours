import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/tours/tour-list-page.component').then((m) => m.TourListPageComponent),
  },
  {
    path: 'tours/:id',
    loadComponent: () =>
      import('./features/tour-detail/tour-detail-page.component').then((m) => m.TourDetailPageComponent),
  },
  {
    path: 'my-bookings',
    loadComponent: () =>
      import('./features/my-bookings/my-bookings-page.component').then((m) => m.MyBookingsPageComponent),
  },
  {
    path: '**',
    loadComponent: () =>
      import('./features/not-found/not-found-page.component').then((m) => m.NotFoundPageComponent),
  },
];
