# Admin Panel Setup Guide

## 🚨 Issue: Schemes Not Accessible

The schemes aren't accessible because the **gov-schemes-project server** needs to be running to provide the API endpoints that the admin panel uses.

## 🔧 Solution

### Step 1: Start the Gov-Schemes-Project Server

You have two options to start the server:

#### Option A: Use the Helper Script (Recommended)
```bash
cd buildthon/Ctrl-A
python start_gov_schemes_server.py
```

#### Option B: Manual Start
```bash
cd buildthon/gov-schemes-project
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Verify Server is Running

Open your browser and go to:
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

You should see a JSON response with server status.

### Step 3: Access Admin Panel

1. Go to the **Welfare Schemes** page in your Ctrl-A app
2. Click the **"Admin Panel"** button
3. Login with:
   - **Username**: `admin`
   - **Password**: `password`
4. Click **"Manage Schemes"** to see all schemes

## 🔍 What Was Fixed

### 1. **Authentication Handling**
- Added automatic admin token retrieval
- Implemented token refresh on expiration
- Added fallback to mock data when server is unavailable

### 2. **Error Handling**
- Better error messages for API failures
- Graceful fallback to demo data
- Clear indication when using mock data

### 3. **API Integration**
- Proper Bearer token authentication
- Retry logic for failed requests
- Support for all CRUD operations (Create, Read, Update, Delete)

## 📋 Available Admin Features

### ✅ **Scheme Management**
- **View All Schemes**: Table view with all scheme details
- **Add New Scheme**: Complete form with all required fields
- **Edit Scheme**: Update existing scheme information
- **Delete Scheme**: Remove schemes with confirmation

### ✅ **Statistics Dashboard**
- Total schemes count
- Active schemes count
- States covered
- Disability types supported

### ✅ **Form Fields**
- Scheme Name
- Description
- State
- Disability Type (dropdown)
- Support Type (dropdown)
- Apply Link
- Eligibility Criteria
- Benefits
- Contact Information
- Validity Period

## 🛠️ Technical Details

### API Endpoints Used
- `GET /api/v1/admin/schemes` - List all schemes
- `POST /api/v1/admin/schemes` - Create new scheme
- `PUT /api/v1/admin/schemes/{id}` - Update scheme
- `DELETE /api/v1/admin/schemes/{id}` - Delete scheme
- `POST /api/v1/admin/login` - Admin authentication

### Authentication Flow
1. Admin panel attempts to get admin token
2. If no token exists, automatically logs in with default credentials
3. Token is stored in localStorage for future requests
4. Token is refreshed automatically on expiration

### Fallback System
- If API server is not running, shows mock data
- Clear error messages indicate when using demo data
- All functionality works with mock data for testing

## 🚀 Quick Start Commands

```bash
# Start the server
cd buildthon/Ctrl-A
python start_gov_schemes_server.py

# In another terminal, start the main Ctrl-A app
cd buildthon/Ctrl-A
python auth_server.py
```

## 🔧 Troubleshooting

### Server Won't Start
1. Check if port 8000 is already in use
2. Ensure you're in the correct directory
3. Install dependencies: `pip install -r requirements.txt`

### Admin Login Fails
1. Check if the server is running at http://localhost:8000
2. Verify the health endpoint: http://localhost:8000/health
3. Check browser console for error messages

### Schemes Not Loading
1. Ensure the gov-schemes-project server is running
2. Check browser network tab for API call failures
3. Look for error messages in the admin panel

## 📝 Notes

- The admin panel will work with mock data even if the server is not running
- All CRUD operations are fully functional when the server is available
- The system gracefully handles both online and offline scenarios
- Admin credentials are: `admin` / `password` (can be changed in the server config)

## 🎯 Next Steps

1. **Start the server** using the helper script
2. **Test the admin panel** by adding/editing/deleting schemes
3. **Verify API integration** by checking the network requests
4. **Customize admin credentials** in the gov-schemes-project configuration

The admin panel is now fully functional and matches the gov-schemes-project interface! 🎉
