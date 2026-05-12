import { Injectable } from '@angular/core';
import {
  AgentChatResponse,
  Booking,
  CreateBookingRequest,
  PaginatedTours,
  Tour,
  TourFilters,
} from '@core/models/api.models';
import { MOCK_BOOKINGS, MOCK_TOURS } from '@data/mock-tours';

@Injectable({ providedIn: 'root' })
export class MockApiService {
  private readonly bookings: Booking[] = [...MOCK_BOOKINGS];

  getTours(filters: TourFilters = {}): PaginatedTours {
    const page = filters.page ?? 1;
    const size = 6;
    let items = [...MOCK_TOURS];

    if (filters.country) {
      items = items.filter((tour) => tour.country === filters.country);
    }

    if (filters.price_min !== undefined) {
      items = items.filter((tour) => tour.price_usd >= Number(filters.price_min));
    }

    if (filters.price_max !== undefined) {
      items = items.filter((tour) => tour.price_usd <= Number(filters.price_max));
    }

    if (filters.date_from) {
      items = items.filter((tour) => tour.start_date >= filters.date_from!);
    }

    if (filters.date_to) {
      items = items.filter((tour) => tour.end_date <= filters.date_to!);
    }

    items.sort((a, b) => {
      switch (filters.sort) {
        case 'price_asc':
          return a.price_usd - b.price_usd;
        case 'price_desc':
          return b.price_usd - a.price_usd;
        case 'date_asc':
          return a.start_date.localeCompare(b.start_date);
        case 'rating_desc':
        default:
          return b.rating - a.rating;
      }
    });

    return {
      items: items.slice((page - 1) * size, page * size),
      total: items.length,
      page,
      size,
    };
  }

  getTour(id: string): Tour | undefined {
    return MOCK_TOURS.find((tour) => tour.id === id);
  }

  getCountries(): string[] {
    return [...new Set(MOCK_TOURS.map((tour) => tour.country))].sort();
  }

  createBooking(body: CreateBookingRequest): Booking {
    const booking: Booking = {
      ...body,
      id: `booking-${Date.now()}`,
      status: 'confirmed',
      created_at: new Date().toISOString(),
    };

    this.bookings.unshift(booking);
    return booking;
  }

  getBookingsByEmail(email: string): Booking[] {
    const normalizedEmail = email.trim().toLowerCase();
    return this.bookings
      .filter((booking) => booking.user_email.toLowerCase() === normalizedEmail)
      .map((booking) => ({
        ...booking,
        tour: this.getTour(booking.tour_id),
      }));
  }

  chat(message: string): AgentChatResponse {
    const normalized = message.toLowerCase();
    const candidates = MOCK_TOURS.filter((tour) => {
      return (
        normalized.includes(tour.country.toLowerCase()) ||
        normalized.includes(tour.city.toLowerCase()) ||
        normalized.includes(String(tour.price_usd).slice(0, 2))
      );
    });
    const suggestions = (candidates.length ? candidates : MOCK_TOURS.slice(0, 2)).slice(0, 3);

    return {
      reply: `I would start with ${suggestions[0].title}. It matches a strong travel brief and stays within a clear booking flow. You can compare ${suggestions.length} suggested tour options below.`,
      suggested_tour_ids: suggestions.map((tour) => tour.id),
    };
  }
}
