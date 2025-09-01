import logging
import time
import psutil
import docker
import requests
from typing import Dict, List, Any, Optional
from threading import Thread, Lock
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContainerHealth:
    """Container health status data structure."""
    container_id: str
    name: str
    status: str
    cpu_percent: float
    memory_usage: int
    memory_limit: int
    memory_percent: float
    network_rx: int
    network_tx: int
    disk_usage: int
    uptime: float
    restart_count: int
    last_check: datetime
    health_status: str  # healthy, warning, critical, unknown
    services_status: Dict[str, str]  # service_name -> status
    error_message: Optional[str] = None

@dataclass
class SystemHealth:
    """System-wide health metrics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    load_average: List[float]
    active_containers: int
    failed_containers: int
    timestamp: datetime

class HealthMonitor:
    """Comprehensive health monitoring system for agent containers."""
    
    def __init__(self, check_interval: int = 30):
        """Initialize the health monitor.
        
        Args:
            check_interval: Seconds between health checks
        """
        self.docker_client = docker.from_env()
        self.check_interval = check_interval
        self.container_health: Dict[str, ContainerHealth] = {}
        self.system_health: Optional[SystemHealth] = None
        self.lock = Lock()
        self.monitoring = False
        self.monitor_thread: Optional[Thread] = None
        
        # Health thresholds
        self.cpu_warning_threshold = 80.0
        self.cpu_critical_threshold = 95.0
        self.memory_warning_threshold = 80.0
        self.memory_critical_threshold = 95.0
        self.disk_warning_threshold = 85.0
        self.disk_critical_threshold = 95.0
    
    def start_monitoring(self):
        """Start the health monitoring background thread."""
        if self.monitoring:
            logger.warning("Health monitoring is already running")
            return
        
        self.monitoring = True
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop the health monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                self._check_system_health()
                self._check_container_health()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def _check_system_health(self):
        """Check overall system health metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            # Count container statuses
            containers = self.docker_client.containers.list(all=True)
            active_containers = len([c for c in containers if c.status == 'running'])
            failed_containers = len([c for c in containers if c.status in ['exited', 'dead']])
            
            with self.lock:
                self.system_health = SystemHealth(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_percent=(disk.used / disk.total) * 100,
                    load_average=list(load_avg),
                    active_containers=active_containers,
                    failed_containers=failed_containers,
                    timestamp=datetime.now()
                )
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
    
    def _check_container_health(self):
        """Check health of all agent containers."""
        try:
            containers = self.docker_client.containers.list(all=True)
            agent_containers = [c for c in containers if 'agent' in c.name.lower()]
            
            current_health = {}
            
            for container in agent_containers:
                try:
                    health = self._get_container_health(container)
                    current_health[container.id] = health
                except Exception as e:
                    logger.error(f"Error checking health for container {container.name}: {e}")
            
            with self.lock:
                self.container_health = current_health
                
        except Exception as e:
            logger.error(f"Error checking container health: {e}")
    
    def _get_container_health(self, container) -> ContainerHealth:
        """Get detailed health information for a specific container."""
        container.reload()
        
        # Get container stats
        stats = container.stats(stream=False)
        
        # Calculate CPU percentage
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                   stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                      stats['precpu_stats']['system_cpu_usage']
        cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0 if system_delta > 0 else 0.0
        
        # Memory usage
        memory_usage = stats['memory_stats']['usage']
        memory_limit = stats['memory_stats']['limit']
        memory_percent = (memory_usage / memory_limit) * 100.0
        
        # Network I/O
        network_rx = sum(net['rx_bytes'] for net in stats['networks'].values()) if 'networks' in stats else 0
        network_tx = sum(net['tx_bytes'] for net in stats['networks'].values()) if 'networks' in stats else 0
        
        # Disk usage (approximate)
        disk_usage = stats.get('blkio_stats', {}).get('io_service_bytes_recursive', [{}])[0].get('value', 0)
        
        # Container uptime
        started_at = datetime.fromisoformat(container.attrs['State']['StartedAt'].replace('Z', '+00:00'))
        uptime = (datetime.now(started_at.tzinfo) - started_at).total_seconds()
        
        # Restart count
        restart_count = container.attrs['RestartCount']
        
        # Check service health within container
        services_status = self._check_container_services(container)
        
        # Determine overall health status
        health_status = self._determine_health_status(cpu_percent, memory_percent, services_status)
        
        return ContainerHealth(
            container_id=container.id,
            name=container.name,
            status=container.status,
            cpu_percent=cpu_percent,
            memory_usage=memory_usage,
            memory_limit=memory_limit,
            memory_percent=memory_percent,
            network_rx=network_rx,
            network_tx=network_tx,
            disk_usage=disk_usage,
            uptime=uptime,
            restart_count=restart_count,
            last_check=datetime.now(),
            health_status=health_status,
            services_status=services_status
        )
    
    def _check_container_services(self, container) -> Dict[str, str]:
        """Check the status of services running inside the container."""
        services_status = {}
        
        try:
            # Check VNC service
            try:
                vnc_check = container.exec_run("nc -z localhost 5901", timeout=5)
                services_status['vnc'] = 'healthy' if vnc_check.exit_code == 0 else 'unhealthy'
            except:
                services_status['vnc'] = 'unknown'
            
            # Check X server
            try:
                x_check = container.exec_run("pgrep Xvfb", timeout=5)
                services_status['xserver'] = 'healthy' if x_check.exit_code == 0 else 'unhealthy'
            except:
                services_status['xserver'] = 'unknown'
            
            # Check noVNC
            try:
                novnc_check = container.exec_run("nc -z localhost 6080", timeout=5)
                services_status['novnc'] = 'healthy' if novnc_check.exit_code == 0 else 'unhealthy'
            except:
                services_status['novnc'] = 'unknown'
            
            # Check Jupyter (if applicable)
            try:
                jupyter_check = container.exec_run("nc -z localhost 8888", timeout=5)
                services_status['jupyter'] = 'healthy' if jupyter_check.exit_code == 0 else 'unhealthy'
            except:
                services_status['jupyter'] = 'unknown'
                
        except Exception as e:
            logger.error(f"Error checking services for container {container.name}: {e}")
        
        return services_status
    
    def _determine_health_status(self, cpu_percent: float, memory_percent: float, 
                               services_status: Dict[str, str]) -> str:
        """Determine overall health status based on metrics."""
        # Check for critical conditions
        if cpu_percent > self.cpu_critical_threshold or memory_percent > self.memory_critical_threshold:
            return 'critical'
        
        # Check for service failures
        unhealthy_services = [name for name, status in services_status.items() if status == 'unhealthy']
        if len(unhealthy_services) > 1:  # Multiple service failures
            return 'critical'
        elif len(unhealthy_services) == 1:
            return 'warning'
        
        # Check for warning conditions
        if cpu_percent > self.cpu_warning_threshold or memory_percent > self.memory_warning_threshold:
            return 'warning'
        
        return 'healthy'
    
    def get_container_health(self, container_id: str) -> Optional[ContainerHealth]:
        """Get health information for a specific container."""
        with self.lock:
            return self.container_health.get(container_id)
    
    def get_all_container_health(self) -> Dict[str, ContainerHealth]:
        """Get health information for all monitored containers."""
        with self.lock:
            return self.container_health.copy()
    
    def get_system_health(self) -> Optional[SystemHealth]:
        """Get system-wide health metrics."""
        with self.lock:
            return self.system_health
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of overall system and container health."""
        with self.lock:
            containers = self.container_health.copy()
            system = self.system_health
        
        if not system:
            return {'error': 'System health data not available'}
        
        # Count containers by health status
        health_counts = {'healthy': 0, 'warning': 0, 'critical': 0, 'unknown': 0}
        for container in containers.values():
            health_counts[container.health_status] += 1
        
        # Determine overall system status
        overall_status = 'healthy'
        if health_counts['critical'] > 0 or system.cpu_percent > self.cpu_critical_threshold or \
           system.memory_percent > self.memory_critical_threshold:
            overall_status = 'critical'
        elif health_counts['warning'] > 0 or system.cpu_percent > self.cpu_warning_threshold or \
             system.memory_percent > self.memory_warning_threshold:
            overall_status = 'warning'
        
        return {
            'overall_status': overall_status,
            'system_health': asdict(system) if system else None,
            'container_counts': health_counts,
            'total_containers': len(containers),
            'last_updated': datetime.now().isoformat()
        }

# Global health monitor instance
health_monitor = HealthMonitor()