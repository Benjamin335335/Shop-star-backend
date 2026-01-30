# Login Troubleshooting Guide

## Quick Diagnostic Steps

### Step 1: Check Backend is Running
1. Open Command Prompt / PowerShell
2. Run: `python backend.py`
3. You should see output like:
```
Admin user created: username='admin', password='admin123'
Sample coupons created: SAVE10 (10%), SAVE20 (20%), WELCOME5 (5%)
Running on http://127.0.0.1:5000/
```

If backend doesn't start, you may have:
- Missing dependencies (install: `pip install flask flask-cors flask-sqlalchemy`)
- Port 5000 already in use
- Python not in PATH

### Step 2: Check Browser Console for Errors
1. Open index.html in browser
2. Press F12 to open Developer Tools
3. Go to "Console" tab
4. Try to login
5. Look for error messages

### Step 3: Verify Network Request
1. In Developer Tools, go to "Network" tab
2. Reload page
3. Try to login
4. Look for request to `http://127.0.0.1:5000/api/auth/login`
5. Check if request shows 200 status or error status

## Common Issues & Solutions

### Issue 1: Backend Not Running
**Symptoms:**
- Network error when trying to login
- "Failed to fetch" message
- Network tab shows no requests to localhost:5000

**Solution:**
1. Start backend: `python backend.py`
2. Verify it says "Running on http://127.0.0.1:5000/"
3. Try login again

### Issue 2: Database Not Initialized
**Symptoms:**
- Backend starts but login fails
- Database error in console

**Solution:**
1. Delete `shop-pro.db` file (if exists)
2. Restart backend
3. Admin account will be auto-created

### Issue 3: Wrong Credentials
**Symptoms:**
- "Invalid username or password" error

**Solution:**
Use demo admin account:
- Username: `admin`
- Password: `admin123`

Or create a new account via signup

### Issue 4: CORS Error
**Symptoms:**
- Browser console shows CORS error
- Network shows 403 or CORS-related error

**Solution:**
- This should be fixed by CORS(app) in backend
- Verify backend.py has: `CORS(app)` on line 17
- Restart backend

### Issue 5: Frontend Can't Find Form Elements
**Symptoms:**
- Console shows: "Cannot read property 'value' of null"
- Login button doesn't work

**Solution:**
1. Check browser console for exact error
2. Verify form IDs in index.html:
   - `login-username` (should exist)
   - `login-password` (should exist)
3. Verify page fully loaded before trying to login

## Testing the Backend Directly

### Using curl (Command Line)

**Test 1: Health Check**
```bash
curl http://127.0.0.1:5000/api/health
```

Expected response:
```json
{"message":"Shop Pro API is running","status":"ok"}
```

**Test 2: Login Request**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

Expected response:
```json
{"message":"Login successful","success":true,"user":{...}}
```

### Using Browser Console

**Test 1: Check API Configuration**
```javascript
console.log('API_BASE_URL:', API_BASE_URL);
```
Should show: `http://127.0.0.1:5000/api`

**Test 2: Test API Call**
```javascript
fetch('http://127.0.0.1:5000/api/health')
  .then(r => r.json())
  .then(d => console.log(d))
```

**Test 3: Test Login**
```javascript
fetch('http://127.0.0.1:5000/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'admin123'})
})
  .then(r => r.json())
  .then(d => console.log(d))
```

## Debug Checklist

- [ ] Backend is running on http://127.0.0.1:5000
- [ ] Admin account exists in database
- [ ] Browser console shows no errors
- [ ] Network tab shows request to /api/auth/login
- [ ] Network response status is 200
- [ ] Response JSON has "success": true
- [ ] Form IDs are correct (login-username, login-password)
- [ ] API_BASE_URL is correct

## Files to Check

1. **index.html** - Check form element IDs:
   - `login-username` exists
   - `login-password` exists
   - `login-form` has onsubmit="login(event)"

2. **app.js** - Check:
   - `API_BASE_URL = 'http://127.0.0.1:5000/api'`
   - `login(event)` function exists
   - `apiCall()` function exists

3. **backend.py** - Check:
   - Line 17: `CORS(app)`
   - Line 237: `def login()` endpoint exists
   - Database initialized with admin user

## Manual Reset

If everything fails, do a complete reset:

1. **Delete database:**
   ```bash
   del shop-pro.db
   ```

2. **Restart backend:**
   ```bash
   python backend.py
   ```

3. **Reload frontend:**
   - Close browser tab
   - Open index.html again

4. **Login with admin:**
   - Username: admin
   - Password: admin123

## Still Not Working?

Check for these specific issues:

1. **Port 5000 in use:**
   ```bash
   netstat -ano | findstr :5000
   ```

2. **Python dependencies missing:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Firewall blocking:**
   - Ensure localhost:5000 is accessible
   - Check Windows Firewall settings

4. **Database corruption:**
   - Delete shop-pro.db
   - Restart backend

## Getting Help

When reporting the issue, provide:
1. Error message from browser console
2. Network request details (status, response)
3. Backend console output
4. What steps you've already tried

