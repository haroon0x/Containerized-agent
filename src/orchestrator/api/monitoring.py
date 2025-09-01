from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
import logging
from .health_monitor import health_monitor
from .job_manager import job_manager
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.on_event("startup")
async def startup_monitoring():
    """Start the health monitoring system."""
    health_monitor.start_monitoring()
    logger.info("Health monitoring system started")

@router.on_event("shutdown")
async def shutdown_monitoring():
    """Stop the health monitoring system."""
    health_monitor.stop_monitoring()
    logger.info("Health monitoring system stopped")

@router.get("/health")
async def get_system_health():
    """Get overall system health status."""
    try:
        health_summary = health_monitor.get_health_summary()
        return {
            "status": "success",
            "data": health_summary
        }
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/containers")
async def get_container_health():
    """Get health status for all monitored containers."""
    try:
        container_health = health_monitor.get_all_container_health()
        
        # Convert to serializable format
        serializable_health = {}
        for container_id, health in container_health.items():
            serializable_health[container_id] = {
                "container_id": health.container_id,
                "name": health.name,
                "status": health.status,
                "cpu_percent": health.cpu_percent,
                "memory_usage": health.memory_usage,
                "memory_limit": health.memory_limit,
                "memory_percent": health.memory_percent,
                "network_rx": health.network_rx,
                "network_tx": health.network_tx,
                "disk_usage": health.disk_usage,
                "uptime": health.uptime,
                "restart_count": health.restart_count,
                "last_check": health.last_check.isoformat(),
                "health_status": health.health_status,
                "services_status": health.services_status,
                "error_message": health.error_message
            }
        
        return {
            "status": "success",
            "data": serializable_health
        }
    except Exception as e:
        logger.error(f"Error getting container health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/containers/{container_id}")
async def get_specific_container_health(container_id: str):
    """Get health status for a specific container."""
    try:
        health = health_monitor.get_container_health(container_id)
        
        if not health:
            raise HTTPException(status_code=404, detail="Container not found or not monitored")
        
        return {
            "status": "success",
            "data": {
                "container_id": health.container_id,
                "name": health.name,
                "status": health.status,
                "cpu_percent": health.cpu_percent,
                "memory_usage": health.memory_usage,
                "memory_limit": health.memory_limit,
                "memory_percent": health.memory_percent,
                "network_rx": health.network_rx,
                "network_tx": health.network_tx,
                "disk_usage": health.disk_usage,
                "uptime": health.uptime,
                "restart_count": health.restart_count,
                "last_check": health.last_check.isoformat(),
                "health_status": health.health_status,
                "services_status": health.services_status,
                "error_message": health.error_message
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting container health for {container_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/system")
async def get_system_metrics():
    """Get system-wide metrics."""
    try:
        system_health = health_monitor.get_system_health()
        
        if not system_health:
            raise HTTPException(status_code=404, detail="System health data not available")
        
        return {
            "status": "success",
            "data": {
                "cpu_percent": system_health.cpu_percent,
                "memory_percent": system_health.memory_percent,
                "disk_percent": system_health.disk_percent,
                "load_average": system_health.load_average,
                "active_containers": system_health.active_containers,
                "failed_containers": system_health.failed_containers,
                "timestamp": system_health.timestamp.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/health")
async def get_job_health_overview():
    """Get health overview of all jobs and their containers."""
    try:
        # Get all jobs from job manager
        jobs = job_manager.jobs
        
        # Get container health data
        container_health = health_monitor.get_all_container_health()
        
        job_health_data = []
        
        for job_id, job_info in jobs.items():
            container_id = job_info.get('container_id')
            health_info = None
            
            if container_id:
                # Find health data for this container
                for cid, health in container_health.items():
                    if cid == container_id:
                        health_info = {
                            "health_status": health.health_status,
                            "cpu_percent": health.cpu_percent,
                            "memory_percent": health.memory_percent,
                            "uptime": health.uptime,
                            "services_status": health.services_status
                        }
                        break
            
            job_health_data.append({
                "job_id": job_id,
                "container_id": container_id,
                "job_status": job_info.get('status'),
                "created": job_info.get('created'),
                "health_info": health_info
            })
        
        return {
            "status": "success",
            "data": job_health_data
        }
    except Exception as e:
        logger.error(f"Error getting job health overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_active_alerts():
    """Get active health alerts and warnings."""
    try:
        alerts = []
        
        # Check system health for alerts
        system_health = health_monitor.get_system_health()
        if system_health:
            if system_health.cpu_percent > 90:
                alerts.append({
                    "type": "system",
                    "severity": "critical",
                    "message": f"High CPU usage: {system_health.cpu_percent:.1f}%",
                    "timestamp": system_health.timestamp.isoformat()
                })
            elif system_health.cpu_percent > 80:
                alerts.append({
                    "type": "system",
                    "severity": "warning",
                    "message": f"Elevated CPU usage: {system_health.cpu_percent:.1f}%",
                    "timestamp": system_health.timestamp.isoformat()
                })
            
            if system_health.memory_percent > 90:
                alerts.append({
                    "type": "system",
                    "severity": "critical",
                    "message": f"High memory usage: {system_health.memory_percent:.1f}%",
                    "timestamp": system_health.timestamp.isoformat()
                })
            elif system_health.memory_percent > 80:
                alerts.append({
                    "type": "system",
                    "severity": "warning",
                    "message": f"Elevated memory usage: {system_health.memory_percent:.1f}%",
                    "timestamp": system_health.timestamp.isoformat()
                })
            
            if system_health.failed_containers > 0:
                alerts.append({
                    "type": "containers",
                    "severity": "critical",
                    "message": f"{system_health.failed_containers} failed containers detected",
                    "timestamp": system_health.timestamp.isoformat()
                })
        
        # Check container health for alerts
        container_health = health_monitor.get_all_container_health()
        for container_id, health in container_health.items():
            if health.health_status == 'critical':
                alerts.append({
                    "type": "container",
                    "severity": "critical",
                    "message": f"Container {health.name} is in critical state",
                    "container_id": container_id,
                    "timestamp": health.last_check.isoformat()
                })
            elif health.health_status == 'warning':
                alerts.append({
                    "type": "container",
                    "severity": "warning",
                    "message": f"Container {health.name} has warnings",
                    "container_id": container_id,
                    "timestamp": health.last_check.isoformat()
                })
            
            # Check for service failures
            failed_services = [name for name, status in health.services_status.items() if status == 'unhealthy']
            if failed_services:
                alerts.append({
                    "type": "services",
                    "severity": "warning",
                    "message": f"Services failed in {health.name}: {', '.join(failed_services)}",
                    "container_id": container_id,
                    "timestamp": health.last_check.isoformat()
                })
        
        return {
            "status": "success",
            "data": {
                "alerts": alerts,
                "total_alerts": len(alerts),
                "critical_count": len([a for a in alerts if a['severity'] == 'critical']),
                "warning_count": len([a for a in alerts if a['severity'] == 'warning'])
            }
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/health/check")
async def trigger_health_check():
    """Manually trigger a health check cycle."""
    try:
        # This would trigger an immediate health check
        # For now, we'll just return the current status
        health_summary = health_monitor.get_health_summary()
        return {
            "status": "success",
            "message": "Health check completed",
            "data": health_summary
        }
    except Exception as e:
        logger.error(f"Error triggering health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))