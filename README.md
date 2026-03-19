# SSC - Sculpt Soft Cricketers

A complete web-based player management and performance tracking system for cricket players. Built with FastAPI backend and React frontend, featuring a freemium subscription model.

## 🎯 Features

### Core Features
- **Player Registration & Authentication** - Secure JWT-based authentication
- **Player Profiles** - Manage player information and statistics
- **Performance Tracking** - Log matches, runs, wickets, and achievements
- **Premium Subscription** - ₹1000/month membership with featured status
- **Leaderboards** - Top scorers and wicket-takers rankings
- **Dashboard** - Centralized overview of all players and stats
- **Admin Panel** - System management and user administration

### Additional Features
- **Real-time Notifications** - Premium expiry alerts and achievements
- **Performance Logs** - Detailed match-by-match performance history
- **Rate Limiting** - API protection against abuse
- **Comprehensive Logging** - System activity tracking
- **CORS Support** - Cross-origin resource sharing
- **API Documentation** - Interactive Swagger/OpenAPI docs

## 📋 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Authentication**: JWT with PassLib
- **API Rate Limiting**: SlowAPI

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router v6
- **API Client**: Axios
- **Charts**: Chart.js with React wrapper

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- pip (Python package manager)
- npm (Node package manager)

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate  # Unix/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create .env file**
```bash
cp .env.example .env
```

5. **Initialize database**
```bash
python -c "from app.database import init_db; init_db()"
```

6. **Run development server**
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend API will be available at `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Run development server**
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📚 API Endpoints

### Authentication
- `POST /auth/register` - Register new player
- `POST /auth/login` - Login player

### Players
- `GET /players/me` - Get current player profile
- `PUT /players/me` - Update current player profile
- `GET /players/{player_id}` - Get player profile by ID
- `GET /players` - Get all players
- `GET /players/leaderboard/top-performers` - Top 10 scorers
- `GET /players/leaderboard/by-wickets` - Top wicket-takers

### Premium
- `POST /premium/upgrade` - Upgrade to premium
- `GET /premium/status` - Check premium status
- `POST /premium/cancel` - Cancel premium
- `GET /premium/payments` - Payment history

### Performance
- `POST /performance` - Log performance
- `GET /performance/my-logs` - Get own performance logs
- `GET /performance/player/{player_id}` - Get player's logs
- `GET /performance/stats/{player_id}` - Get player stats

### Dashboard
- `GET /dashboard/overview` - System overview
- `GET /dashboard/featured-players` - Featured premium players
- `GET /dashboard/recent-players` - Recently joined players
- `GET /dashboard/top-stats` - Top performers

### Admin
- `GET /admin/users` - List all users
- `PUT /admin/users/{user_id}/premium` - Toggle premium
- `DELETE /admin/users/{user_id}` - Deactivate user
- `GET /admin/stats` - System statistics

## 🔑 Default Admin Credentials

```
Email: admin@ssc.com
Password: admin123
```

## 📊 Database Schema

### Users Table
- id, name, email, password
- jersey_number, role, bio
- runs, matches, wickets
- is_premium, premium_expiry
- is_active, created_at, updated_at

### Payments Table
- id, user_id, amount
- payment_method, transaction_id
- status, plan_duration_days

### Performance Logs Table
- id, user_id, match_date
- runs_scored, wickets_taken
- match_type, opponent
- performance_rating, notes

### Notifications Table
- id, user_id, title, message
- notification_type, is_read, created_at

## 🎨 Premium Features

Players can upgrade to Premium (₹1000/month) to:
- ✨ Get featured on the dashboard
- 📊 Access advanced analytics
- 🔔 Get priority notifications
- 🏆 Appear in premium players list

Premium membership auto-downgrades after 30 days.

## 📝 Additional Features Implemented

### 1. **Performance Analytics**
- Track century and half-century achievements
- Calculate batting averages
- Highest score tracking
- Match-by-match performance logs

### 2. **Ranking System**
- Player rankings by total runs
- Top wicket-taker leaderboard
- Premium member spotlight

### 3. **Activity Logging**
- Comprehensive API request logging
- User action tracking
- Error tracking and reporting

### 4. **Rate Limiting**
- API rate limiting to prevent abuse
- Per-endpoint throttling
- Graceful error responses

### 5. **Notification System**
- Premium expiry notifications
- Achievement notifications
- Customizable notification types

### 6. **Admin Dashboard**
- View all users
- Toggle user premium status
- Deactivate users
- View system statistics

## 🐳 Docker Setup (Optional)

```bash
docker-compose up -d
```

This will start both backend and frontend containers.

## 📖 Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./ssc.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PREMIUM_COST=1000
PREMIUM_DURATION_DAYS=30
```

## 🧪 Testing

### Test Authentication
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com","password":"pass123"}'
```

### Test API with Token
```bash
curl -X GET "http://localhost:8000/players/me" \
  -H "Authorization: Bearer {token}"
```

## 🚀 Deployment

### Backend
The backend can be deployed on:
- Heroku
- AWS EC2
- Google Cloud Run
- DigitalOcean

### Frontend
The frontend can be deployed on:
- Vercel
- Netlify
- AWS S3
- GitHub Pages

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Rate limiting
- SQL injection prevention (via SQLAlchemy ORM)
- Admin role verification

## 📞 Support & Contribution

For issues and feature requests, please create an issue in the repository.

## 📄 License

This project is open source and available under the MIT License.

## 🎓 Learning Resources

This project demonstrates:
- Modern API design with FastAPI
- Database design with SQLAlchemy
- JWT authentication
- Frontend development with React
- Responsive UI design
- Subscription-based SaaS architecture
