#!/bin/bash

# OneNightPrep Docker Setup Script

echo "🐳 OneNightPrep Docker Setup"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
    echo "⚠️  Don't forget to add your Google API key!"
else
    echo "✅ .env file already exists"
fi

# Make scripts executable
chmod +x entrypoint.sh
chmod +x docker-dev.sh

echo "🏗️  Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🎉 OneNightPrep is now running!"
    echo "================================"
    echo "🌐 Application: http://localhost:8000"
    echo "⚙️  Admin Panel: http://localhost:8000/admin"
    echo "❤️  Health Check: http://localhost:8000/health"
    echo "📊 Database: localhost:5432"
    echo ""
    echo "Default Admin Credentials:"
    echo "Username: admin"
    echo "Password: admin"
    echo ""
    echo "Useful Commands:"
    echo "  ./docker-dev.sh logs    - View application logs"
    echo "  ./docker-dev.sh shell   - Open Django shell"
    echo "  ./docker-dev.sh stop    - Stop the application"
    echo "  ./docker-dev.sh start   - Start the application"
    echo ""
    echo "View logs with: docker-compose logs -f web"
else
    echo "❌ Services failed to start. Check logs with: docker-compose logs"
    exit 1
fi
