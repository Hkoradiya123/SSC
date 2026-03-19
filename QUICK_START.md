# SSC Quick Start Guide

## 🚀 Getting Started (5 Minutes)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Load test data (optional)
python load_test_data.py

# Start server
python -m uvicorn main:app --reload
```

✅ Backend running at: http://localhost:8000
📚 API Docs: http://localhost:8000/docs

### 2. Frontend Setup

In a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend running at: http://localhost:3000

---

## 📝 Test Accounts

Use these credentials to test the application:

### Regular Player
- **Email**: virat@ssc.com
- **Password**: password123

### Premium Player
- **Email**: rohit@ssc.com
- **Password**: password123

### Admin User
- **Email**: admin@ssc.com
- **Password**: admin123

---

## 🧪 Testing the API

### 1. Register a New Player

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Player",
    "email": "test@ssc.com",
    "password": "testpass123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ssc.com",
    "password": "testpass123"
  }'
```

Copy the `access_token` from the response.

### 3. Get Player Profile

```bash
curl -X GET "http://localhost:8000/players/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Log Performance

```bash
curl -X POST "http://localhost:8000/performance" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "match_date": "2024-01-15T14:00:00",
    "runs_scored": 50,
    "wickets_taken": 0,
    "match_type": "league",
    "opponent": "Team A",
    "performance_rating": 8.0,
    "notes": "Great batting"
  }'
```

### 5. Upgrade to Premium

```bash
curl -X POST "http://localhost:8000/premium/upgrade" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_days": 30
  }'
```

---

## 🎯 Key Features to Try

### On Dashboard
1. View all players
2. Check featured premium players
3. See top scorers and wicket-takers
4. View system statistics

### In Player Profile
1. View personal statistics
2. See performance history
3. Upgrade to premium membership
4. Track achievements

### In Admin Panel
1. View all registered users
2. Toggle user premium status
3. Deactivate users
4. Check system statistics

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Clear any cached Python files
find . -type d -name __pycache__ -exec rm -r {} +

# Ensure all dependencies are installed
pip install -r requirements.txt

# Check if port 8000 is already in use
# Change port: uvicorn main:app --reload --port 8001
```

### Frontend won't start
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Try different port
npm run dev -- --port 3001
```

### Database errors
```bash
# Reinitialize database
rm ssc.db
python load_test_data.py
```

### Token issues
- Ensure token is copied correctly (no extra spaces)
- Token expires after 30 minutes
- Re-login to get a new token

---

## 📚 API Usage Examples

### JavaScript/React Example

```javascript
// Login
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'virat@ssc.com',
    password: 'password123'
  })
});

const data = await response.json();
localStorage.setItem('token', data.access_token);

// Get profile
const profileRes = await fetch('http://localhost:8000/players/me', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
});

const profile = await profileRes.json();
console.log(profile);
```

---

## 🚀 Next Steps

1. **Explore API Documentation**: Visit http://localhost:8000/docs
2. **Test all endpoints**: Use the Swagger UI
3. **Build custom features**: Extend the frontend
4. **Integrate payments**: Add Razorpay integration
5. **Deploy**: Use Docker or cloud services

---

## 📖 Documentation

- [Full README](./README.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Backend Code](./backend/)
- [Frontend Code](./frontend/)

---

## ❓ Need Help?

Check the logs:

```bash
# Backend logs
tail -f logs/ssc.log

# Frontend console errors
# Open browser DevTools (F12)
```

For errors, check:
1. Correct .env variables
2. Database initialization
3. Port availability
4. CORS configuration
5. Token validity

---

Happy Testing! 🏏⭐
