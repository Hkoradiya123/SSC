# SSC API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer {token}
```

## Request/Response Format

All APIs use JSON request and response format.

---

## 1. Authentication Endpoints

### Register
**POST** `/auth/register`

Request:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "runs": 0,
    "matches": 0,
    "is_premium": false,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

### Login
**POST** `/auth/login`

Request:
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

Response: Same as Register

---

## 2. Player Endpoints

### Get Current Player
**GET** `/players/me`

Headers: `Authorization: Bearer {token}`

Response:
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "runs": 150,
  "matches": 5,
  "wickets": 0
}
```

### Update Player Profile
**PUT** `/players/me`

Headers: `Authorization: Bearer {token}`

Request:
```json
{
  "name": "John Doe",
  "bio": "Professional cricket player",
  "jersey_number": 7
}
```

### Get Player by ID
**GET** `/players/{player_id}`

Response: Player object

### List All Players
**GET** `/players?skip=0&limit=50`

Response: Array of players

### Get Premium Players
**GET** `/players`

Response: Array of premium players

### Top Performers
**GET** `/players/leaderboard/top-performers?limit=10`

Response: Array of top scorers

### Top Wicket Takers
**GET** `/players/leaderboard/by-wickets?limit=10`

Response: Array of top wicket-takers

---

## 3. Premium Endpoints

### Upgrade to Premium
**POST** `/premium/upgrade`

Headers: `Authorization: Bearer {token}`

Request:
```json
{
  "plan_days": 30
}
```

Response:
```json
{
  "is_premium": true,
  "premium_expiry": "2024-02-15T10:30:00",
  "message": "Successfully upgraded to premium for 30 days!"
}
```

### Check Premium Status
**GET** `/premium/status`

Headers: `Authorization: Bearer {token}`

Response:
```json
{
  "is_premium": true,
  "premium_expiry": "2024-02-15T10:30:00",
  "message": "Premium active until 2024-02-15"
}
```

### Cancel Premium
**POST** `/premium/cancel`

Headers: `Authorization: Bearer {token}`

Response:
```json
{
  "message": "Premium membership cancelled"
}
```

### Payment History
**GET** `/premium/payments`

Headers: `Authorization: Bearer {token}`

Response: Array of payment records

---

## 4. Performance Endpoints

### Log Performance
**POST** `/performance`

Headers: `Authorization: Bearer {token}`

Request:
```json
{
  "match_date": "2024-01-15T14:00:00",
  "runs_scored": 45,
  "wickets_taken": 2,
  "match_type": "league",
  "opponent": "Team A",
  "performance_rating": 8.5,
  "notes": "Great performance"
}
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "match_date": "2024-01-15T14:00:00",
  "runs_scored": 45,
  "wickets_taken": 2,
  "created_at": "2024-01-15T15:00:00"
}
```

### Get Own Performance Logs
**GET** `/performance/my-logs?skip=0&limit=20`

Headers: `Authorization: Bearer {token}`

Response: Array of performance logs

### Get Player Performance Logs
**GET** `/performance/player/{player_id}?skip=0&limit=20`

Response: Array of performance logs for the player

### Get Player Statistics
**GET** `/performance/stats/{player_id}`

Response:
```json
{
  "id": 1,
  "name": "John Doe",
  "runs": 150,
  "matches": 5,
  "wickets": 2,
  "centuries": 0,
  "half_centuries": 1,
  "average_runs": 30.0,
  "highest_score": 65
}
```

---

## 5. Dashboard Endpoints

### Dashboard Overview
**GET** `/dashboard/overview`

Response:
```json
{
  "total_players": 25,
  "premium_players": 5,
  "total_matches": 120,
  "total_runs": 3500
}
```

### Featured Premium Players
**GET** `/dashboard/featured-players`

Response: Array of premium players

### Recent Players
**GET** `/dashboard/recent-players`

Response: Array of recently joined players

### Top Statistics
**GET** `/dashboard/top-stats`

Response:
```json
{
  "top_scorer": {
    "name": "John Doe",
    "runs": 500
  },
  "top_wicket_taker": {
    "name": "Jane Smith",
    "wickets": 20
  }
}
```

---

## 6. Admin Endpoints

### List All Users
**GET** `/admin/users?skip=0&limit=100`

Headers: `Authorization: Bearer {token}` (Admin token required)

Response: Array of all users

### Toggle User Premium
**PUT** `/admin/users/{user_id}/premium?days=30`

Headers: `Authorization: Bearer {token}` (Admin token required)

Response:
```json
{
  "message": "User premium status updated"
}
```

### Deactivate User
**DELETE** `/admin/users/{user_id}`

Headers: `Authorization: Bearer {token}` (Admin token required)

Response:
```json
{
  "message": "User deactivated successfully"
}
```

### System Statistics
**GET** `/admin/stats`

Headers: `Authorization: Bearer {token}` (Admin token required)

Response:
```json
{
  "total_users": 25,
  "active_users": 23,
  "premium_users": 5,
  "total_matches": 120
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Only admins can access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Player not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Too many requests. Please try again later."
}
```

---

## Rate Limiting

- Register: 5 requests per minute
- Login: 10 requests per minute
- Other endpoints: 30 requests per minute

---

## Pagination

Use `skip` and `limit` parameters for pagination:
```
GET /players?skip=0&limit=50
```

---

## Timestamps

All timestamps are in UTC ISO 8601 format:
```
2024-01-15T10:30:00
```
