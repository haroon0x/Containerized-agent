import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import docker
import psutil
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

@dataclass
class MetricPoint:
    """A single metric data point."""
    timestamp: float
    value: float
    labels: Dict[str, str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}

@dataclass
class ContainerMetrics:
    """Container-specific metrics."""
    container_id: str
    container_name: str
    cpu_percent: float
    memory_usage_mb: float
    memory_limit_mb: float
    memory_percent: float
    network_rx_bytes: int
    network_tx_bytes: int
    disk_read_bytes: int
    disk_write_bytes: int
    uptime_seconds: float
    restart_count: int
    status: str
    timestamp: float

@dataclass
class SystemMetrics:
    """System-wide metrics."""
    cpu_percent: float
    memory_usage_mb: float
    memory_total_mb: float
    memory_percent: float
    disk_usage_gb: float
    disk_total_gb: float
    disk_percent: float
    load_average: List[float]
    active_containers: int
    timestamp: float

class MetricsCollector:
    """Collects and stores metrics from containers and system."""
    
    def __init__(self, retention_hours: int = 24, collection_interval: int = 30):
        self.docker_client = docker.from_env()
        self.retention_hours = retention_hours
        self.collection_interval = collection_interval
        self.logger = logging.getLogger(__name__)
        
        # In-memory storage for metrics (in production, use a proper time-series DB)
        self.container_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=2880))  # 24h at 30s intervals
        self.system_metrics: deque = deque(maxlen=2880)
        
        # Track network stats for rate calculation
        self.previous_network_stats: Dict[str, Dict] = {}
        self.previous_disk_stats: Dict[str, Dict] = {}
        
        self._running = False
        self._task = None
    
    async def start(self):
        """Start the metrics collection task."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._collection_loop())
        self.logger.info(f"Started metrics collection with {self.collection_interval}s interval")
    
    async def stop(self):
        """Stop the metrics collection task."""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped metrics collection")
    
    async def _collection_loop(self):
        """Main collection loop."""
        while self._running:
            try:
                await self._collect_metrics()
                await self._cleanup_old_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying
    
    async def _collect_metrics(self):
        """Collect metrics from all containers and system."""
        timestamp = time.time()
        
        # Collect system metrics
        system_metrics = await self._collect_system_metrics(timestamp)
        self.system_metrics.append(system_metrics)
        
        # Collect container metrics
        containers = self.docker_client.containers.list(all=True)
        for container in containers:
            try:
                container_metrics = await self._collect_container_metrics(container, timestamp)
                if container_metrics:
                    self.container_metrics[container.id].append(container_metrics)
            except Exception as e:
                self.logger.warning(f"Failed to collect metrics for container {container.id}: {e}")
    
    async def _collect_system_metrics(self, timestamp: float) -> SystemMetrics:
        """Collect system-wide metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage_mb = (memory.total - memory.available) / 1024 / 1024
        memory_total_mb = memory.total / 1024 / 1024
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage_gb = (disk.total - disk.free) / 1024 / 1024 / 1024
        disk_total_gb = disk.total / 1024 / 1024 / 1024
        
        # Load average
        load_avg = list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0.0, 0.0, 0.0]
        
        # Active containers
        active_containers = len([c for c in self.docker_client.containers.list() if c.status == 'running'])
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_usage_mb=memory_usage_mb,
            memory_total_mb=memory_total_mb,
            memory_percent=memory.percent,
            disk_usage_gb=disk_usage_gb,
            disk_total_gb=disk_total_gb,
            disk_percent=disk.percent,
            load_average=load_avg,
            active_containers=active_containers,
            timestamp=timestamp
        )
    
    async def _collect_container_metrics(self, container, timestamp: float) -> Optional[ContainerMetrics]:
        """Collect metrics for a specific container."""
        try:
            # Get container stats
            stats = container.stats(stream=False)
            
            # Calculate CPU percentage
            cpu_percent = self._calculate_cpu_percent(stats)
            
            # Memory metrics
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 0)
            memory_usage_mb = memory_usage / 1024 / 1024
            memory_limit_mb = memory_limit / 1024 / 1024
            memory_percent = (memory_usage / memory_limit * 100) if memory_limit > 0 else 0
            
            # Network metrics
            network_rx, network_tx = self._calculate_network_stats(container.id, stats)
            
            # Disk I/O metrics
            disk_read, disk_write = self._calculate_disk_stats(container.id, stats)
            
            # Container info
            container.reload()
            uptime_seconds = (datetime.now() - datetime.fromisoformat(container.attrs['State']['StartedAt'].replace('Z', '+00:00'))).total_seconds()
            restart_count = container.attrs['RestartCount']
            
            return ContainerMetrics(
                container_id=container.id,
                container_name=container.name,
                cpu_percent=cpu_percent,
                memory_usage_mb=memory_usage_mb,
                memory_limit_mb=memory_limit_mb,
                memory_percent=memory_percent,
                network_rx_bytes=network_rx,
                network_tx_bytes=network_tx,
                disk_read_bytes=disk_read,
                disk_write_bytes=disk_write,
                uptime_seconds=uptime_seconds,
                restart_count=restart_count,
                status=container.status,
                timestamp=timestamp
            )
        
        except Exception as e:
            self.logger.warning(f"Failed to collect metrics for container {container.id}: {e}")
            return None
    
    def _calculate_cpu_percent(self, stats: Dict) -> float:
        """Calculate CPU percentage from Docker stats."""
        try:
            cpu_stats = stats['cpu_stats']
            precpu_stats = stats['precpu_stats']
            
            cpu_delta = cpu_stats['cpu_usage']['total_usage'] - precpu_stats['cpu_usage']['total_usage']
            system_delta = cpu_stats['system_cpu_usage'] - precpu_stats['system_cpu_usage']
            
            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * len(cpu_stats['cpu_usage']['percpu_usage']) * 100.0
                return round(cpu_percent, 2)
        except (KeyError, ZeroDivisionError):
            pass
        
        return 0.0
    
    def _calculate_network_stats(self, container_id: str, stats: Dict) -> tuple:
        """Calculate network RX/TX bytes."""
        try:
            networks = stats.get('networks', {})
            rx_bytes = sum(net.get('rx_bytes', 0) for net in networks.values())
            tx_bytes = sum(net.get('tx_bytes', 0) for net in networks.values())
            return rx_bytes, tx_bytes
        except (KeyError, TypeError):
            return 0, 0
    
    def _calculate_disk_stats(self, container_id: str, stats: Dict) -> tuple:
        """Calculate disk read/write bytes."""
        try:
            blkio_stats = stats.get('blkio_stats', {})
            io_service_bytes = blkio_stats.get('io_service_bytes_recursive', [])
            
            read_bytes = sum(entry.get('value', 0) for entry in io_service_bytes if entry.get('op') == 'Read')
            write_bytes = sum(entry.get('value', 0) for entry in io_service_bytes if entry.get('op') == 'Write')
            
            return read_bytes, write_bytes
        except (KeyError, TypeError):
            return 0, 0
    
    async def _cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff_time = time.time() - (self.retention_hours * 3600)
        
        # Clean system metrics
        while self.system_metrics and self.system_metrics[0].timestamp < cutoff_time:
            self.system_metrics.popleft()
        
        # Clean container metrics
        for container_id in list(self.container_metrics.keys()):
            metrics_queue = self.container_metrics[container_id]
            while metrics_queue and metrics_queue[0].timestamp < cutoff_time:
                metrics_queue.popleft()
            
            # Remove empty queues
            if not metrics_queue:
                del self.container_metrics[container_id]
    
    def get_latest_system_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent system metrics."""
        return self.system_metrics[-1] if self.system_metrics else None
    
    def get_latest_container_metrics(self, container_id: str = None) -> Dict[str, ContainerMetrics]:
        """Get the most recent metrics for all containers or a specific container."""
        if container_id:
            metrics_queue = self.container_metrics.get(container_id)
            return {container_id: metrics_queue[-1]} if metrics_queue else {}
        
        return {
            cid: metrics_queue[-1] 
            for cid, metrics_queue in self.container_metrics.items() 
            if metrics_queue
        }
    
    def get_metrics_history(self, container_id: str = None, hours: int = 1) -> Dict:
        """Get historical metrics for analysis."""
        cutoff_time = time.time() - (hours * 3600)
        
        result = {
            'system': [],
            'containers': {}
        }
        
        # System metrics history
        result['system'] = [
            asdict(metric) for metric in self.system_metrics 
            if metric.timestamp >= cutoff_time
        ]
        
        # Container metrics history
        if container_id:
            metrics_queue = self.container_metrics.get(container_id, deque())
            result['containers'][container_id] = [
                asdict(metric) for metric in metrics_queue 
                if metric.timestamp >= cutoff_time
            ]
        else:
            for cid, metrics_queue in self.container_metrics.items():
                result['containers'][cid] = [
                    asdict(metric) for metric in metrics_queue 
                    if metric.timestamp >= cutoff_time
                ]
        
        return result
    
    def get_aggregated_metrics(self, container_id: str = None, hours: int = 1) -> Dict:
        """Get aggregated metrics (avg, min, max) for the specified time period."""
        history = self.get_metrics_history(container_id, hours)
        
        result = {
            'system': {},
            'containers': {}
        }
        
        # Aggregate system metrics
        if history['system']:
            system_data = history['system']
            result['system'] = {
                'cpu_percent': {
                    'avg': sum(m['cpu_percent'] for m in system_data) / len(system_data),
                    'min': min(m['cpu_percent'] for m in system_data),
                    'max': max(m['cpu_percent'] for m in system_data)
                },
                'memory_percent': {
                    'avg': sum(m['memory_percent'] for m in system_data) / len(system_data),
                    'min': min(m['memory_percent'] for m in system_data),
                    'max': max(m['memory_percent'] for m in system_data)
                },
                'disk_percent': {
                    'avg': sum(m['disk_percent'] for m in system_data) / len(system_data),
                    'min': min(m['disk_percent'] for m in system_data),
                    'max': max(m['disk_percent'] for m in system_data)
                }
            }
        
        # Aggregate container metrics
        for cid, container_data in history['containers'].items():
            if container_data:
                result['containers'][cid] = {
                    'cpu_percent': {
                        'avg': sum(m['cpu_percent'] for m in container_data) / len(container_data),
                        'min': min(m['cpu_percent'] for m in container_data),
                        'max': max(m['cpu_percent'] for m in container_data)
                    },
                    'memory_percent': {
                        'avg': sum(m['memory_percent'] for m in container_data) / len(container_data),
                        'min': min(m['memory_percent'] for m in container_data),
                        'max': max(m['memory_percent'] for m in container_data)
                    }
                }
        
        return result

# Global metrics collector instance
metrics_collector = MetricsCollector()