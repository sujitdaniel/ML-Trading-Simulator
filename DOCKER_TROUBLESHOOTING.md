# 🐳 Docker Troubleshooting Guide for Algonex

## Quick Start
```bash
# Build and run
docker-compose up --build

# Or use the batch script
docker-run.bat
```

## Common Issues & Solutions

### 1. "Failed to fetch" Error
**Problem**: Frontend can't connect to backend
**Solution**: 
- Ensure both containers are running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`
- Check frontend logs: `docker-compose logs frontend`

### 2. Port Already in Use
**Problem**: Ports 3000 or 8000 are already occupied
**Solution**:
```bash
# Stop existing containers
docker-compose down

# Kill processes using the ports
netstat -ano | findstr :3000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### 3. CORS Issues
**Problem**: Browser blocks requests due to CORS
**Solution**: 
- Backend CORS is configured for Docker networking
- Frontend uses `http://backend:8000` in Docker
- Check browser console for specific errors

### 4. Container Build Failures
**Problem**: Docker build fails
**Solution**:
```bash
# Clean build
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -f Dockerfile.backend .
docker build -f frontend/Dockerfile ./frontend
```

## Network Configuration
- **Frontend**: `http://localhost:3000` (external access)
- **Backend**: `http://localhost:8000` (external access)
- **Internal**: Frontend → Backend via `http://backend:8000`

## Environment Variables
- `NEXT_PUBLIC_API_URL=http://backend:8000` (Docker)
- `NEXT_PUBLIC_API_URL=http://localhost:8000` (Local dev)

## Useful Commands
```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Remove all containers and rebuild
docker-compose down --rmi all
docker-compose up --build
```

## Testing the Connection
1. Open http://localhost:3000 in browser
2. Use the "Test API Connection" button
3. Check browser console for any errors
4. Check Docker logs for backend errors

## If Still Having Issues
1. Check Docker Desktop is running
2. Ensure no other services use ports 3000/8000
3. Try different ports in docker-compose.yml
4. Check firewall/antivirus settings
