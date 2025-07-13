from django.http import JsonResponse
from django.views import View
import os

class HealthCheckView(View):
    """
    Simple health check endpoint for Docker containers
    """
    def get(self, request):
        return JsonResponse({
            'status': 'healthy',
            'message': 'OneNightPrep is running',
            'debug': os.getenv('DEBUG', 'False'),
            'database': 'connected' if self._check_database() else 'disconnected'
        })
    
    def _check_database(self):
        """Check if database connection is working"""
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            return True
        except Exception:
            return False
