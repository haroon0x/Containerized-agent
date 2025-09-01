#!/usr/bin/env python3
"""
Health check server for webdev agent container.
Provides HTTP endpoints for health monitoring.
"""

import json
import time
import subprocess
import psutil
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health check endpoints."""
    
    def do_GET(self):
        """Handle GET requests for health checks."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/health':
            self._handle_health_check()
        elif path == '/health/detailed':
            self._handle_detailed_health()
        elif path == '/health/services':
            self._handle_services_health()
        elif path == '/metrics':
            self._handle_metrics()
        else:
            self._send_response(404, {'error': 'Not found'})
    
    def _handle_health_check(self):
        """Basic health check endpoint."""
        try:
            health_status = self._get_basic_health()
            status_code = 200 if health_status['status'] == 'healthy' else 503
            self._send_response(status_code, health_status)
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            self._send_response(500, {'status': 'error', 'message': str(e)})
    
    def _handle_detailed_health(self):
        """Detailed health check with all metrics."""
        try:
            health_data = self._get_detailed_health()
            status_code = 200 if health_data['overall_status'] == 'healthy' else 503
            self._send_response(status_code, health_data)
        except Exception as e:
            logger.error(f"Error in detailed health check: {e}")
            self._send_response(500, {'status': 'error', 'message': str(e)})
    
    def _handle_services_health(self):
        """Service-specific health checks."""
        try:
            services_status = self._check_services()
            all_healthy = all(status == 'healthy' for status in services_status.values())
            status_code = 200 if all_healthy else 503
            self._send_response(status_code, {'services': services_status})
        except Exception as e:
            logger.error(f"Error in services health check: {e}")
            self._send_response(500, {'status': 'error', 'message': str(e)})
    
    def _handle_metrics(self):
        """System metrics endpoint."""
        try:
            metrics = self._get_system_metrics()
            self._send_response(200, metrics)
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            self._send_response(500, {'status': 'error', 'message': str(e)})
    
    def _get_basic_health(self) -> Dict[str, Any]:
        """Get basic health status."""
        # Check critical services
        services = self._check_services()
        critical_services = ['xserver', 'vnc', 'novnc']
        
        failed_critical = [name for name in critical_services 
                          if services.get(name) != 'healthy']
        
        if failed_critical:
            return {
                'status': 'unhealthy',
                'message': f'Critical services failed: {failed_critical}',
                'timestamp': time.time()
            }
        
        return {
            'status': 'healthy',
            'message': 'All critical services running',
            'timestamp': time.time()
        }
    
    def _get_detailed_health(self) -> Dict[str, Any]:
        """Get comprehensive health information."""
        services = self._check_services()
        metrics = self._get_system_metrics()
        
        # Determine overall status
        service_issues = [name for name, status in services.items() if status != 'healthy']
        resource_issues = []
        
        if metrics['cpu_percent'] > 90:
            resource_issues.append('high_cpu')
        if metrics['memory_percent'] > 90:
            resource_issues.append('high_memory')
        if metrics['disk_percent'] > 95:
            resource_issues.append('high_disk')
        
        if service_issues or resource_issues:
            overall_status = 'unhealthy'
        elif metrics['cpu_percent'] > 80 or metrics['memory_percent'] > 80:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'
        
        return {
            'overall_status': overall_status,
            'services': services,
            'metrics': metrics,
            'issues': {
                'service_issues': service_issues,
                'resource_issues': resource_issues
            },
            'timestamp': time.time()
        }
    
    def _check_services(self) -> Dict[str, str]:
        """Check the status of all services."""
        services = {}
        
        # Check X server
        try:
            result = subprocess.run(['pgrep', 'Xvfb'], capture_output=True, timeout=5)
            services['xserver'] = 'healthy' if result.returncode == 0 else 'unhealthy'
        except:
            services['xserver'] = 'unknown'
        
        # Check VNC server
        try:
            result = subprocess.run(['pgrep', 'Xtigervnc'], capture_output=True, timeout=5)
            vnc_running = result.returncode == 0
            
            # Also check if VNC port is listening
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            vnc_port_open = sock.connect_ex(('localhost', 5901)) == 0
            sock.close()
            
            services['vnc'] = 'healthy' if vnc_running and vnc_port_open else 'unhealthy'
        except:
            services['vnc'] = 'unknown'
        
        # Check noVNC
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            novnc_running = sock.connect_ex(('localhost', 6080)) == 0
            sock.close()
            services['novnc'] = 'healthy' if novnc_running else 'unhealthy'
        except:
            services['novnc'] = 'unknown'
        
        # Check supervisord
        try:
            result = subprocess.run(['pgrep', 'supervisord'], capture_output=True, timeout=5)
            services['supervisord'] = 'healthy' if result.returncode == 0 else 'unhealthy'
        except:
            services['supervisord'] = 'unknown'
        
        # Check agent process
        try:
            result = subprocess.run(['pgrep', '-f', 'gemini'], capture_output=True, timeout=5)
            services['agent'] = 'healthy' if result.returncode == 0 else 'unhealthy'
        except:
            services['agent'] = 'unknown'
        
        return services
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Load average (if available)
        try:
            load_avg = psutil.getloadavg()
        except:
            load_avg = [0, 0, 0]
        
        # Process count
        process_count = len(psutil.pids())
        
        # Network stats
        try:
            net_io = psutil.net_io_counters()
            network = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except:
            network = {}
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used': memory.used,
            'memory_total': memory.total,
            'disk_percent': (disk.used / disk.total) * 100,
            'disk_used': disk.used,
            'disk_total': disk.total,
            'load_average': list(load_avg),
            'process_count': process_count,
            'network': network,
            'uptime': time.time() - psutil.boot_time()
        }
    
    def _send_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = json.dumps(data, indent=2)
        self.wfile.write(response_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")

def run_health_server(port: int = 9090):
    """Run the health check server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    
    logger.info(f"Health check server starting on port {port}")
    logger.info(f"Available endpoints:")
    logger.info(f"  GET /health - Basic health check")
    logger.info(f"  GET /health/detailed - Detailed health information")
    logger.info(f"  GET /health/services - Service status")
    logger.info(f"  GET /metrics - System metrics")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Health check server shutting down")
        httpd.shutdown()

if __name__ == '__main__':
    run_health_server()