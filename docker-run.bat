@echo off
echo 🐳 Building and running Algonex with Docker...
echo.

echo 🔨 Building containers...
docker-compose build --no-cache

echo.
echo 🚀 Starting services...
docker-compose up -d

echo.
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak

echo.
echo 📊 Checking service status...
docker-compose ps

echo.
echo 🌐 Services should be available at:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo.
echo 📝 To view logs: docker-compose logs -f
echo 📝 To stop: docker-compose down
echo.
pause
