#!/bin/bash

# OneNightPrep Docker Management Script

case "$1" in
    start)
        echo "Starting OneNightPrep..."
        docker-compose up -d
        echo "Application started at http://localhost:8000"
        ;;
    stop)
        echo "Stopping OneNightPrep..."
        docker-compose down
        ;;
    restart)
        echo "Restarting OneNightPrep..."
        docker-compose restart
        ;;
    build)
        echo "Building OneNightPrep..."
        docker-compose build
        ;;
    logs)
        echo "Showing logs..."
        docker-compose logs -f web
        ;;
    shell)
        echo "Opening Django shell..."
        docker-compose exec web python manage.py shell
        ;;
    migrate)
        echo "Running migrations..."
        docker-compose exec web python manage.py migrate
        ;;
    superuser)
        echo "Creating superuser..."
        docker-compose exec web python manage.py createsuperuser
        ;;
    collectstatic)
        echo "Collecting static files..."
        docker-compose exec web python manage.py collectstatic --noinput
        ;;
    reset)
        echo "Resetting database (WARNING: This will delete all data)..."
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker-compose up -d
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|build|logs|shell|migrate|superuser|collectstatic|reset}"
        echo ""
        echo "Commands:"
        echo "  start         - Start the application"
        echo "  stop          - Stop the application"
        echo "  restart       - Restart the application"
        echo "  build         - Build the Docker images"
        echo "  logs          - Show application logs"
        echo "  shell         - Open Django shell"
        echo "  migrate       - Run database migrations"
        echo "  superuser     - Create superuser"
        echo "  collectstatic - Collect static files"
        echo "  reset         - Reset database (WARNING: deletes all data)"
        exit 1
        ;;
esac
