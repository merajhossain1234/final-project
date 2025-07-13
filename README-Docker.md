# OneNightPrep - Docker Setup

This Django project is fully dockerized and ready to run with Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd onenightprep
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file and add your API keys and configuration.

3. **Build and run the application**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Main application: http://localhost:8000
   - Admin panel: http://localhost:8000/admin (username: admin, password: admin)

## Docker Commands

### Development

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs web

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: This will delete your database)
docker-compose down -v
```

### Production

```bash
# Run production setup
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

### Useful Commands

```bash
# Execute commands in running container
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py migrate

# View database
docker-compose exec db psql -U postgres -d onenightprep

# Rebuild specific service
docker-compose build web
```

## Project Structure

```
onenightprep/
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Main compose file
├── docker-compose.override.yml  # Development overrides
├── docker-compose.prod.yml # Production configuration
├── entrypoint.sh           # Container startup script
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .dockerignore          # Docker ignore file
└── manage.py              # Django management script
```

## Environment Variables

Key environment variables (set in `.env` file):

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (1 for True, 0 for False)
- `DATABASE_URL`: Database connection URL
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `GOOGLE_API_KEY`: Google API key for AI features

## Services

- **web**: Django application server
- **db**: PostgreSQL database
- **nginx**: Reverse proxy (production only)

## Volumes

- `postgres_data`: Database data persistence
- `media_volume`: User uploaded files
- `static_volume`: Static files (CSS, JS, images)

## Troubleshooting

1. **Permission errors**: Make sure entrypoint.sh is executable
2. **Database connection errors**: Wait for database to be ready
3. **Static files not loading**: Run `docker-compose exec web python manage.py collectstatic`
4. **Port conflicts**: Change port mapping in docker-compose.yml

## Development Tips

1. **Live reloading**: Code changes are automatically reflected (development mode)
2. **Database access**: Use `docker-compose exec db psql -U postgres -d onenightprep`
3. **Logs**: Use `docker-compose logs -f web` to follow application logs
4. **Shell access**: Use `docker-compose exec web bash` for container shell access

## Production Deployment

For production deployment:

1. Set proper environment variables
2. Use production compose file
3. Configure SSL/TLS certificates
4. Set up proper backup strategies
5. Monitor resource usage

```bash
# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
