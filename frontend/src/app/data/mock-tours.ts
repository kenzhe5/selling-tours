import { Booking, Tour } from '@core/models/api.models';

export const MOCK_TOURS: Tour[] = [
  {
    id: 'tour-kyoto-spring',
    title: 'Kyoto spring ryokan escape',
    country: 'Japan',
    city: 'Kyoto',
    price_usd: 1850,
    start_date: '2026-04-12',
    end_date: '2026-04-19',
    duration_days: 7,
    description:
      'A quiet week of temple gardens, tea houses, bamboo walks, and a traditional ryokan stay in the old capital.',
    images: [
      'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?auto=format&fit=crop&w=900&q=80',
    ],
    included: ['Boutique ryokan', 'Daily breakfast', 'Tea ceremony', 'Local guide'],
    hotel_name: 'Kamo River Ryokan',
    rating: 4.9,
  },
  {
    id: 'tour-morocco-atlas',
    title: 'Atlas mountains and Marrakech',
    country: 'Morocco',
    city: 'Marrakech',
    price_usd: 1240,
    start_date: '2026-03-03',
    end_date: '2026-03-10',
    duration_days: 7,
    description:
      'Markets, riads, desert edges, and a guided climb into the High Atlas with slow evenings on tiled courtyards.',
    images: [
      'https://images.unsplash.com/photo-1539020140153-e479b8c22e70?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1548018560-c7196548e84d?auto=format&fit=crop&w=900&q=80',
    ],
    included: ['Riad stay', 'Airport transfer', 'Atlas day trek', 'Cooking class'],
    hotel_name: 'Riad Amina',
    rating: 4.7,
  },
  {
    id: 'tour-iceland-ring',
    title: 'Iceland south coast road trip',
    country: 'Iceland',
    city: 'Reykjavik',
    price_usd: 2390,
    start_date: '2026-06-04',
    end_date: '2026-06-12',
    duration_days: 8,
    description:
      'Black sand beaches, glacier lagoons, waterfalls, and compact lodges designed for long northern light.',
    images: [
      'https://images.unsplash.com/photo-1504829857797-ddff29c27927?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1529963183134-61a90db47eaf?auto=format&fit=crop&w=900&q=80',
    ],
    included: ['Car rental', 'Lodge stays', 'Glacier hike', 'Breakfast'],
    hotel_name: 'Holt Coastal Lodge',
    rating: 4.8,
  },
  {
    id: 'tour-italy-amalfi',
    title: 'Amalfi coast slow summer',
    country: 'Italy',
    city: 'Positano',
    price_usd: 2120,
    start_date: '2026-05-18',
    end_date: '2026-05-25',
    duration_days: 7,
    description:
      'A sea-facing base for coastal hikes, lemon groves, ferry days, and long dinners above the Tyrrhenian.',
    images: [
      'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=80',
    ],
    included: ['Sea-view hotel', 'Ferry pass', 'Path of Gods hike', 'Breakfast'],
    hotel_name: 'Casa Mare Alta',
    rating: 4.8,
  },
  {
    id: 'tour-peru-sacred-valley',
    title: 'Sacred Valley and Machu Picchu',
    country: 'Peru',
    city: 'Cusco',
    price_usd: 1680,
    start_date: '2026-08-08',
    end_date: '2026-08-16',
    duration_days: 8,
    description:
      'Acclimatize in Cusco, travel through the Sacred Valley, and arrive at Machu Picchu with a private guide.',
    images: [
      'https://images.unsplash.com/photo-1526392060635-9d6019884377?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1587595431973-160d0d94add1?auto=format&fit=crop&w=900&q=80',
    ],
    included: ['Train tickets', 'Guided ruins', 'Boutique hotels', 'Breakfast'],
    hotel_name: 'Valle Verde Inn',
    rating: 4.6,
  },
  {
    id: 'tour-greece-cyclades',
    title: 'Cyclades island design trail',
    country: 'Greece',
    city: 'Naxos',
    price_usd: 1490,
    start_date: '2026-09-02',
    end_date: '2026-09-09',
    duration_days: 7,
    description:
      'A calmer island route through Naxos and Paros with whitewashed villages, swims, and family tavernas.',
    images: [
      'https://images.unsplash.com/photo-1533104816931-20fa691ff6ca?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1601581875039-e899893d520c?auto=format&fit=crop&w=900&q=80',
    ],
    included: ['Ferry tickets', 'Design hotel', 'Beach picnic', 'Breakfast'],
    hotel_name: 'Naxos Courtyard House',
    rating: 4.7,
  },
];

export const MOCK_BOOKINGS: Booking[] = [
  {
    id: 'booking-demo-001',
    tour_id: 'tour-italy-amalfi',
    user_name: 'Demo Traveler',
    user_email: 'demo@example.com',
    start_date: '2026-05-18',
    num_people: 2,
    status: 'confirmed',
    created_at: '2026-05-12T12:00:00.000Z',
  },
];
