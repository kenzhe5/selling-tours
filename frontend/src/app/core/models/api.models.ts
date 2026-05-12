export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

export interface Tour {
  id: string;
  title: string;
  country: string;
  city: string;
  price: number;
  start_date: string;
  end_date: string;
  duration_days: number;
  description: string;
  image_url: string;
  rating: number;
  available_slots: number;
}

export interface TourFilters {
  country?: string;
  price_min?: number;
  price_max?: number;
  date_from?: string;
  date_to?: string;
  sort?: TourSort;
  page?: number;
  size?: number;
}

export type TourSort = 'price_asc' | 'price_desc' | 'rating_desc' | 'date_asc';

export interface PaginatedTours {
  items: Tour[];
  total: number;
  page: number;
  size: number;
}

export type BookingStatus = 'pending' | 'confirmed' | 'cancelled';

export interface Booking {
  id: string;
  tour_id: string;
  user_name: string;
  user_email: string;
  start_date: string;
  num_people: number;
  status: BookingStatus;
  created_at: string;
  tour?: Tour;
}

export interface CreateBookingRequest {
  tour_id: string;
  user_name: string;
  user_email: string;
  start_date: string;
  num_people: number;
}

export interface AgentChatRequest {
  session_id: string;
  message: string;
}

export interface AgentChatResponse {
  reply: string;
  suggested_tour_ids: string[];
}

export interface ChatMessage {
  role: 'assistant' | 'user';
  text: string;
  suggested_tour_ids?: string[];
}
