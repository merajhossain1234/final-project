@echo off
REM OneNightPrep Docker Management Script for Windows

if "%1"=="start" (
    echo Starting OneNightPrep...
    docker-compose up -d
    echo Application started at http://localhost:8000
) else if "%1"=="stop" (
    echo Stopping OneNightPrep...
    docker-compose down
) else if "%1"=="restart" (
    echo Restarting OneNightPrep...
    docker-compose restart
) else if "%1"=="build" (
    echo Building OneNightPrep...
    docker-compose build
) else if "%1"=="logs" (
    echo Showing logs...
    docker-compose logs -f web
) else if "%1"=="shell" (
    echo Opening Django shell...
    docker-compose exec web python manage.py shell
) else if "%1"=="migrate" (
    echo Running migrations...
    docker-compose exec web python manage.py migrate
) else if "%1"=="superuser" (
    echo Creating superuser...
    docker-compose exec web python manage.py createsuperuser
) else if "%1"=="collectstatic" (
    echo Collecting static files...
    docker-compose exec web python manage.py collectstatic --noinput
) else if "%1"=="reset" (
    echo Resetting database ^(WARNING: This will delete all data^)...
    set /p confirm=Are you sure? ^(y/N^): 
    if /i "%confirm%"=="y" (
        docker-compose down -v
        docker-compose up -d
    )
) else (
    echo Usage: %0 {start^|stop^|restart^|build^|logs^|shell^|migrate^|superuser^|collectstatic^|reset}
    echo.
    echo Commands:
    echo   start         - Start the application
    echo   stop          - Stop the application
    echo   restart       - Restart the application
    echo   build         - Build the Docker images
    echo   logs          - Show application logs
    echo   shell         - Open Django shell
    echo   migrate       - Run database migrations
    echo   superuser     - Create superuser
    echo   collectstatic - Collect static files
    echo   reset         - Reset database ^(WARNING: deletes all data^)
)
