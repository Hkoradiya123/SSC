# Project Structure

```
SSC/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database setup
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── payment.py
│   │   │   ├── performance_log.py
│   │   │   └── notification.py
│   │   ├── routes/            # API endpoints
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── players.py     # Player management
│   │   │   ├── premium.py     # Premium subscriptions
│   │   │   ├── performance.py # Performance tracking
│   │   │   ├── dashboard.py   # Dashboard
│   │   │   └── admin.py       # Admin functions
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── payment.py
│   │   │   ├── performance.py
│   │   │   └── notification.py
│   │   ├── utils/             # Utility functions
│   │   │   ├── auth.py        # Auth helpers
│   │   │   ├── premium.py     # Premium logic
│   │   │   └── logger.py      # Logging
│   │   └── middleware/        # Middleware
│   │       ├── __init__.py    # Rate limiting, logging
│   │       └── auth.py        # Authentication middleware
│   ├── main.py                # FastAPI app entry
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── .env.example           # Example env file
│   ├── Dockerfile             # Docker configuration
│   ├── load_test_data.py      # Test data loader
│   └── logs/                  # Log files (created at runtime)
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Navbar.jsx
│   │   │   └── navbar.module.css
│   │   ├── pages/             # Page components
│   │   │   ├── Home.jsx
│   │   │   ├── Auth.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Players.jsx
│   │   │   ├── Profile.jsx
│   │   │   ├── home.module.css
│   │   │   ├── auth.module.css
│   │   │   ├── dashboard.module.css
│   │   │   ├── players.module.css
│   │   │   └── profile.module.css
│   │   ├── utils/             # Utility functions
│   │   │   └── api.js         # API service
│   │   ├── styles/            # Global styles
│   │   │   ├── global.css
│   │   │   └── theme.js
│   │   ├── App.jsx            # Main app component
│   │   └── main.jsx           # React entry point
│   ├── index.html             # HTML template
│   ├── vite.config.js         # Vite configuration
│   ├── package.json           # Node dependencies
│   ├── .env                   # Environment variables
│   ├── .env.example           # Example env file
│   ├── .eslintrc.json         # ESLint config
│   ├── Dockerfile             # Docker configuration
│   └── node_modules/          # Dependencies (created after npm install)
│
├── docker-compose.yml         # Docker compose setup
├── .gitignore                # Git ignore patterns
├── README.md                 # Project documentation
├── QUICK_START.md            # Quick start guide
├── API_DOCUMENTATION.md      # API documentation
└── PROJECT_STRUCTURE.md      # This file

```

## Key Directories

### Backend (`backend/`)
- **app/models**: SQLAlchemy ORM models for database tables
- **app/routes**: FastAPI route handlers for all endpoints
- **app/schemas**: Pydantic models for request/response validation
- **app/utils**: Helper functions for auth, premium logic, logging
- **app/middleware**: Custom middleware for auth, rate limiting, logging
- **main.py**: FastAPI application entrypoint

### Frontend (`frontend/`)
- **src/components**: Reusable React components
- **src/pages**: Full-page components (Home, Dashboard, etc.)
- **src/utils/api.js**: Axios-based API client
- **src/styles**: CSS modules and theme configuration

## Database Schema

### Users Table
```
id (PK)
name, email, password
jersey_number, role (player/admin), bio
runs, matches, wickets, centuries, half_centuries
average_runs, highest_score
is_premium, premium_expiry, premium_start_date
is_active
created_at, updated_at, last_login
```

### Payments Table
```
id (PK)
user_id (FK)
amount, payment_method, transaction_id
status, plan_duration_days
created_at, updated_at
```

### Performance Logs Table
```
id (PK)
user_id (FK)
match_date
runs_scored, wickets_taken
match_type, opponent
performance_rating, notes
created_at
```

### Notifications Table
```
id (PK)
user_id (FK)
title, message
notification_type, is_read
created_at
```

## API Route Structure

```
Authentication
├── POST /auth/register
└── POST /auth/login

Players
├── GET /players/me
├── PUT /players/me
├── GET /players/{id}
├── GET /players
├── GET /players/leaderboard/top-performers
└── GET /players/leaderboard/by-wickets

Premium
├── POST /premium/upgrade
├── GET /premium/status
├── POST /premium/cancel
└── GET /premium/payments

Performance
├── POST /performance
├── GET /performance/my-logs
├── GET /performance/player/{id}
└── GET /performance/stats/{id}

Dashboard
├── GET /dashboard/overview
├── GET /dashboard/featured-players
├── GET /dashboard/recent-players
└── GET /dashboard/top-stats

Admin
├── GET /admin/users
├── PUT /admin/users/{id}/premium
├── DELETE /admin/users/{id}
└── GET /admin/stats
```

## Technology Stack

**Backend:**
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- Pydantic 2.5.0
- PassLib + bcrypt (authentication)
- JWT (token management)
- SlowAPI (rate limiting)
- SQLite

**Frontend:**
- React 18.2.0
- React Router 6.20.0
- Axios 1.6.0
- Chart.js (data visualization)
- Vite (build tool)
- CSS Modules (styling)

## Configuration Files

- `.env`: Runtime environment variables
- `vite.config.js`: Frontend build configuration
- `package.json`: Node dependencies and scripts
- `requirements.txt`: Python dependencies
- `docker-compose.yml`: Multi-container setup

## Getting Started

1. See [QUICK_START.md](./QUICK_START.md) for immediate setup
2. See [README.md](./README.md) for full documentation
3. See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for API details
