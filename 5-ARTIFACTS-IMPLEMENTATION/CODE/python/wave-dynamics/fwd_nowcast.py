#!/usr/bin/env python3
"""
Future Wave Dynamics (FWD) Nowcast Service
MAL-FWD implementation for 0-20 minute nowcasting connected to PRO

Provides short-horizon predictive modeling for environmental conditions,
weather, traffic, and system states supporting real-time decision making.
"""

import asyncio
import logging
import time
import math
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class NowcastType(Enum):
    """Types of nowcast predictions"""
    WEATHER = "weather"
    TRAFFIC = "traffic"  
    AIRSPACE = "airspace"
    ENVIRONMENTAL = "environmental"
    SYSTEM_STATE = "system_state"
    MULTI_MODAL = "multi_modal"

class DataSource(Enum):
    """Available data sources for nowcasting"""
    SENSOR_NETWORK = "sensor_network"
    SATELLITE = "satellite"
    RADAR = "radar"
    ADS_B = "ads_b"
    METAR = "metar"
    SIMULATION = "simulation"

class PredictionConfidence(Enum):
    """Prediction confidence levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"

@dataclass
class NowcastTile:
    """Spatial-temporal nowcast tile"""
    tile_id: str
    latitude: float
    longitude: float
    altitude: Optional[float]
    resolution_m: float
    timestamp: float
    forecast_horizon_min: int
    data_type: NowcastType
    values: Dict[str, Any]
    confidence: PredictionConfidence
    data_sources: List[DataSource]
    uncertainty: Dict[str, float]

@dataclass
class NowcastRequest:
    """Nowcast request specification"""
    request_id: str
    utcs_id: str
    area_bounds: Dict[str, float]  # lat_min, lat_max, lon_min, lon_max
    forecast_horizon_min: int = 20
    resolution_m: float = 1000.0
    data_types: List[NowcastType] = field(default_factory=list)
    deadline_ms: float = 600.0
    quality_level: str = "normal"

@dataclass
class NowcastResponse:
    """Nowcast response with tiles and metadata"""
    request_id: str
    utcs_id: str
    tiles: List[NowcastTile]
    generation_time_ms: float
    coverage_percentage: float
    overall_confidence: PredictionConfidence
    data_freshness_s: float
    next_update_s: float
    status: str
    error: Optional[str] = None

class NowcastModel(ABC):
    """Abstract base class for nowcast models"""
    
    @abstractmethod
    async def predict(self, request: NowcastRequest) -> List[NowcastTile]:
        """Generate nowcast prediction"""
        pass
    
    @abstractmethod
    def get_supported_types(self) -> List[NowcastType]:
        """Get supported nowcast types"""
        pass

class WeatherNowcastModel(NowcastModel):
    """Weather nowcasting model"""
    
    def __init__(self):
        self.name = "WeatherNowcastModel"
        self.supported_types = [NowcastType.WEATHER, NowcastType.ENVIRONMENTAL]
    
    async def predict(self, request: NowcastRequest) -> List[NowcastTile]:
        """Generate weather nowcast tiles"""
        await asyncio.sleep(0.05)  # Simulate computation time
        
        tiles = []
        
        # Generate grid of tiles
        lat_range = request.area_bounds["lat_max"] - request.area_bounds["lat_min"]
        lon_range = request.area_bounds["lon_max"] - request.area_bounds["lon_min"]
        
        # Calculate number of tiles based on resolution
        lat_tiles = max(1, int(lat_range * 111000 / request.resolution_m))  # ~111km per degree
        lon_tiles = max(1, int(lon_range * 111000 / request.resolution_m))
        
        for i in range(lat_tiles):
            for j in range(lon_tiles):
                lat = request.area_bounds["lat_min"] + (i + 0.5) * lat_range / lat_tiles
                lon = request.area_bounds["lon_min"] + (j + 0.5) * lon_range / lon_tiles
                
                # Generate weather parameters
                wind_speed = np.random.uniform(5, 25)  # m/s
                wind_direction = np.random.uniform(0, 360)  # degrees
                temperature = np.random.uniform(-10, 35)  # Celsius
                pressure = np.random.uniform(980, 1030)  # hPa
                visibility = np.random.uniform(1000, 10000)  # meters
                cloud_cover = np.random.uniform(0, 100)  # percentage
                
                # Add forecast evolution over time
                forecast_data = {}
                for t in range(0, request.forecast_horizon_min + 1, 5):  # 5-minute intervals
                    # Simple time evolution
                    temp_trend = np.sin(t * np.pi / 60) * 2  # Small temperature variation
                    wind_trend = np.random.normal(0, 2)  # Wind variation
                    
                    forecast_data[f"t_plus_{t}min"] = {
                        "temperature": temperature + temp_trend,
                        "wind_speed": max(0, wind_speed + wind_trend),
                        "wind_direction": (wind_direction + np.random.normal(0, 10)) % 360,
                        "pressure": pressure + np.random.normal(0, 2),
                        "visibility": max(100, visibility + np.random.normal(0, 500)),
                        "cloud_cover": np.clip(cloud_cover + np.random.normal(0, 5), 0, 100)
                    }
                
                # Determine confidence based on data quality
                confidence = PredictionConfidence.HIGH if visibility > 5000 else PredictionConfidence.MEDIUM
                
                tile = NowcastTile(
                    tile_id=f"weather_{i}_{j}",
                    latitude=lat,
                    longitude=lon,
                    altitude=None,
                    resolution_m=request.resolution_m,
                    timestamp=time.time(),
                    forecast_horizon_min=request.forecast_horizon_min,
                    data_type=NowcastType.WEATHER,
                    values={
                        "current": {
                            "temperature": temperature,
                            "wind_speed": wind_speed,
                            "wind_direction": wind_direction,
                            "pressure": pressure,
                            "visibility": visibility,
                            "cloud_cover": cloud_cover
                        },
                        "forecast": forecast_data
                    },
                    confidence=confidence,
                    data_sources=[DataSource.RADAR, DataSource.METAR, DataSource.SATELLITE],
                    uncertainty={
                        "temperature": 1.5,
                        "wind_speed": 2.0,
                        "wind_direction": 15.0,
                        "pressure": 3.0
                    }
                )
                
                tiles.append(tile)
        
        return tiles
    
    def get_supported_types(self) -> List[NowcastType]:
        return self.supported_types

class TrafficNowcastModel(NowcastModel):
    """Traffic and airspace nowcasting model"""
    
    def __init__(self):
        self.name = "TrafficNowcastModel"
        self.supported_types = [NowcastType.TRAFFIC, NowcastType.AIRSPACE]
    
    async def predict(self, request: NowcastRequest) -> List[NowcastTile]:
        """Generate traffic nowcast tiles"""
        await asyncio.sleep(0.03)
        
        tiles = []
        
        # Generate traffic density predictions
        lat_range = request.area_bounds["lat_max"] - request.area_bounds["lat_min"]
        lon_range = request.area_bounds["lon_max"] - request.area_bounds["lon_min"]
        
        lat_tiles = max(1, int(lat_range * 111000 / request.resolution_m))
        lon_tiles = max(1, int(lon_range * 111000 / request.resolution_m))
        
        for i in range(lat_tiles):
            for j in range(lon_tiles):
                lat = request.area_bounds["lat_min"] + (i + 0.5) * lat_range / lat_tiles
                lon = request.area_bounds["lon_min"] + (j + 0.5) * lon_range / lon_tiles
                
                # Current traffic state
                aircraft_count = np.random.poisson(5)  # Aircraft in sector
                avg_speed = np.random.uniform(200, 500)  # kt
                altitude_spread = np.random.uniform(5000, 15000)  # ft
                conflict_probability = np.random.uniform(0, 0.1)
                
                # Forecast evolution
                forecast_data = {}
                for t in range(0, request.forecast_horizon_min + 1, 2):  # 2-minute intervals
                    # Traffic evolution based on time of day patterns
                    time_factor = 1.0 + 0.3 * np.sin((time.time() % 86400) / 86400 * 2 * np.pi)
                    
                    forecast_data[f"t_plus_{t}min"] = {
                        "aircraft_count": max(0, int(aircraft_count * time_factor + np.random.normal(0, 1))),
                        "avg_speed": avg_speed + np.random.normal(0, 20),
                        "conflict_probability": np.clip(conflict_probability + np.random.normal(0, 0.02), 0, 1),
                        "congestion_level": min(1.0, aircraft_count * time_factor / 10),
                        "flow_rate": np.random.uniform(10, 50)  # aircraft/hour
                    }
                
                tile = NowcastTile(
                    tile_id=f"traffic_{i}_{j}",
                    latitude=lat,
                    longitude=lon,
                    altitude=None,
                    resolution_m=request.resolution_m,
                    timestamp=time.time(),
                    forecast_horizon_min=request.forecast_horizon_min,
                    data_type=NowcastType.TRAFFIC,
                    values={
                        "current": {
                            "aircraft_count": aircraft_count,
                            "avg_speed": avg_speed,
                            "altitude_spread": altitude_spread,
                            "conflict_probability": conflict_probability
                        },
                        "forecast": forecast_data
                    },
                    confidence=PredictionConfidence.MEDIUM,
                    data_sources=[DataSource.ADS_B, DataSource.RADAR],
                    uncertainty={
                        "aircraft_count": 2.0,
                        "conflict_probability": 0.05,
                        "flow_rate": 5.0
                    }
                )
                
                tiles.append(tile)
        
        return tiles
    
    def get_supported_types(self) -> List[NowcastType]:
        return self.supported_types

class SystemStateNowcastModel(NowcastModel):
    """System state nowcasting for infrastructure and resources"""
    
    def __init__(self):
        self.name = "SystemStateNowcastModel"
        self.supported_types = [NowcastType.SYSTEM_STATE]
    
    async def predict(self, request: NowcastRequest) -> List[NowcastTile]:
        """Generate system state nowcast"""
        await asyncio.sleep(0.02)
        
        tiles = []
        
        # Generate single tile for system-wide state
        lat_center = (request.area_bounds["lat_min"] + request.area_bounds["lat_max"]) / 2
        lon_center = (request.area_bounds["lon_min"] + request.area_bounds["lon_max"]) / 2
        
        # System metrics
        cpu_utilization = np.random.uniform(20, 80)  # %
        memory_utilization = np.random.uniform(30, 90)  # %
        network_latency = np.random.uniform(10, 100)  # ms
        throughput = np.random.uniform(100, 1000)  # Mbps
        error_rate = np.random.uniform(0, 0.05)  # %
        
        # Forecast evolution
        forecast_data = {}
        for t in range(0, request.forecast_horizon_min + 1, 1):  # 1-minute intervals
            # System load patterns
            load_trend = np.sin(t * np.pi / 30) * 10  # 30-min cycle
            
            forecast_data[f"t_plus_{t}min"] = {
                "cpu_utilization": np.clip(cpu_utilization + load_trend + np.random.normal(0, 5), 0, 100),
                "memory_utilization": np.clip(memory_utilization + np.random.normal(0, 3), 0, 100),
                "network_latency": max(1, network_latency + np.random.normal(0, 10)),
                "throughput": max(0, throughput + np.random.normal(0, 50)),
                "error_rate": max(0, error_rate + np.random.normal(0, 0.01)),
                "queue_depth": np.random.poisson(10)
            }
        
        tile = NowcastTile(
            tile_id="system_state_global",
            latitude=lat_center,
            longitude=lon_center,
            altitude=None,
            resolution_m=request.resolution_m,
            timestamp=time.time(),
            forecast_horizon_min=request.forecast_horizon_min,
            data_type=NowcastType.SYSTEM_STATE,
            values={
                "current": {
                    "cpu_utilization": cpu_utilization,
                    "memory_utilization": memory_utilization,
                    "network_latency": network_latency,
                    "throughput": throughput,
                    "error_rate": error_rate,
                    "availability": 99.8
                },
                "forecast": forecast_data
            },
            confidence=PredictionConfidence.HIGH,
            data_sources=[DataSource.SENSOR_NETWORK],
            uncertainty={
                "cpu_utilization": 5.0,
                "memory_utilization": 3.0,
                "network_latency": 10.0,
                "throughput": 50.0
            }
        )
        
        tiles.append(tile)
        return tiles
    
    def get_supported_types(self) -> List[NowcastType]:
        return self.supported_types

class FWDNowcastService:
    """FWD Nowcast Service - Main orchestrator for nowcasting"""
    
    def __init__(self):
        self.models = [
            WeatherNowcastModel(),
            TrafficNowcastModel(),
            SystemStateNowcastModel()
        ]
        self.tile_cache = {}  # Simple tile caching
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_response_time_ms": 0.0,
            "cache_hit_rate": 0.0,
            "tile_generation_rate": 0.0
        }
        
        logger.info("FWD Nowcast Service initialized")
    
    async def generate_nowcast(self, request: NowcastRequest) -> NowcastResponse:
        """Generate nowcast response for request"""
        start_time = time.time()
        logger.info(f"Generating nowcast for request {request.request_id}")
        
        try:
            all_tiles = []
            
            # Determine which models to use
            models_to_use = []
            for model in self.models:
                if any(dt in model.get_supported_types() for dt in request.data_types):
                    models_to_use.append(model)
            
            if not models_to_use:
                # Default to all models if no specific types requested
                models_to_use = self.models
            
            # Generate tiles from each model
            tasks = []
            for model in models_to_use:
                task = asyncio.create_task(model.predict(request))
                tasks.append(task)
            
            # Wait for all models to complete
            model_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect tiles
            total_tiles = 0
            for result in model_results:
                if isinstance(result, Exception):
                    logger.error(f"Model error: {result}")
                    continue
                all_tiles.extend(result)
                total_tiles += len(result)
            
            # Calculate metrics
            generation_time = (time.time() - start_time) * 1000
            coverage = min(100.0, len(all_tiles) / max(1, total_tiles) * 100)
            
            # Determine overall confidence
            if all_tiles:
                confidences = [tile.confidence for tile in all_tiles]
                high_conf = sum(1 for c in confidences if c == PredictionConfidence.HIGH)
                overall_conf = PredictionConfidence.HIGH if high_conf > len(confidences) / 2 else PredictionConfidence.MEDIUM
            else:
                overall_conf = PredictionConfidence.LOW
            
            # Update performance metrics
            self._update_performance_metrics(generation_time, True, len(all_tiles))
            
            response = NowcastResponse(
                request_id=request.request_id,
                utcs_id=request.utcs_id,
                tiles=all_tiles,
                generation_time_ms=generation_time,
                coverage_percentage=coverage,
                overall_confidence=overall_conf,
                data_freshness_s=30.0,  # Mock data age
                next_update_s=300.0,  # 5-minute update cycle
                status="success"
            )
            
            logger.info(f"Generated {len(all_tiles)} tiles in {generation_time:.2f}ms")
            return response
            
        except Exception as e:
            error_time = (time.time() - start_time) * 1000
            logger.error(f"Nowcast generation failed: {e}")
            self._update_performance_metrics(error_time, False, 0)
            
            return NowcastResponse(
                request_id=request.request_id,
                utcs_id=request.utcs_id,
                tiles=[],
                generation_time_ms=error_time,
                coverage_percentage=0.0,
                overall_confidence=PredictionConfidence.UNCERTAIN,
                data_freshness_s=0.0,
                next_update_s=60.0,
                status="error",
                error=str(e)
            )
    
    def _update_performance_metrics(self, response_time_ms: float, success: bool, tile_count: int) -> None:
        """Update performance metrics"""
        self.performance_metrics["total_requests"] += 1
        
        if success:
            self.performance_metrics["successful_requests"] += 1
        
        # Update average response time
        total = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_response_time_ms"]
        new_avg = ((current_avg * (total - 1)) + response_time_ms) / total
        self.performance_metrics["average_response_time_ms"] = new_avg
        
        # Update tile generation rate
        if response_time_ms > 0:
            current_rate = tile_count / (response_time_ms / 1000)  # tiles per second
            total_rate = self.performance_metrics["tile_generation_rate"]
            new_rate = ((total_rate * (total - 1)) + current_rate) / total
            self.performance_metrics["tile_generation_rate"] = new_rate
    
    async def get_nowcast_for_area(
        self,
        utcs_id: str,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        forecast_horizon_min: int = 20,
        data_types: Optional[List[str]] = None
    ) -> NowcastResponse:
        """Simplified interface for area-based nowcasting"""
        
        # Convert string data types to enums
        nowcast_types = []
        if data_types:
            for dt in data_types:
                try:
                    nowcast_types.append(NowcastType(dt.lower()))
                except ValueError:
                    logger.warning(f"Unknown data type: {dt}")
        
        if not nowcast_types:
            nowcast_types = [NowcastType.WEATHER, NowcastType.TRAFFIC]
        
        request = NowcastRequest(
            request_id=f"fwd_{int(time.time() * 1000)}",
            utcs_id=utcs_id,
            area_bounds={
                "lat_min": lat_min,
                "lat_max": lat_max,
                "lon_min": lon_min,
                "lon_max": lon_max
            },
            forecast_horizon_min=forecast_horizon_min,
            data_types=nowcast_types
        )
        
        return await self.generate_nowcast(request)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.performance_metrics.copy()

# Global FWD nowcast service instance
fwd_service = FWDNowcastService()

async def generate_fwd_nowcast(
    utcs_id: str,
    area_bounds: Dict[str, float],
    forecast_horizon_min: int = 20,
    data_types: Optional[List[str]] = None,
    resolution_m: float = 1000.0
) -> Dict[str, Any]:
    """
    Main entry point for FWD nowcasting
    Used by MAL-FWD service and AQUA-OS PRO
    """
    try:
        response = await fwd_service.get_nowcast_for_area(
            utcs_id=utcs_id,
            lat_min=area_bounds["lat_min"],
            lat_max=area_bounds["lat_max"], 
            lon_min=area_bounds["lon_min"],
            lon_max=area_bounds["lon_max"],
            forecast_horizon_min=forecast_horizon_min,
            data_types=data_types
        )
        
        # Convert to MAL-FWD format
        return {
            "success": response.status == "success",
            "utcs_id": response.utcs_id,
            "tiles": [
                {
                    "tile_id": tile.tile_id,
                    "latitude": tile.latitude,
                    "longitude": tile.longitude,
                    "data_type": tile.data_type.value,
                    "values": tile.values,
                    "confidence": tile.confidence.value,
                    "uncertainty": tile.uncertainty
                }
                for tile in response.tiles
            ],
            "generation_time_ms": response.generation_time_ms,
            "coverage_percentage": response.coverage_percentage,
            "overall_confidence": response.overall_confidence.value,
            "next_update_s": response.next_update_s,
            "fwd_backend": "MAL-FWD",
            "error": response.error
        }
        
    except Exception as e:
        logger.error(f"FWD nowcast failed: {e}")
        return {
            "success": False,
            "utcs_id": utcs_id,
            "tiles": [],
            "error": str(e),
            "fwd_backend": "MAL-FWD"
        }

if __name__ == "__main__":
    async def main():
        # Test FWD nowcast service
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.INFO)
        
        print("Testing FWD Nowcast Service...")
        
        # Test nowcast generation
        result = await generate_fwd_nowcast(
            utcs_id="TEST/FWD/001",
            area_bounds={
                "lat_min": 40.0,
                "lat_max": 41.0,
                "lon_min": -74.0,
                "lon_max": -73.0
            },
            forecast_horizon_min=15,
            data_types=["weather", "traffic"]
        )
        
        print(f"Nowcast generated: {result['success']}")
        print(f"Tiles generated: {len(result['tiles'])}")
        print(f"Generation time: {result['generation_time_ms']:.2f}ms")
        print(f"Coverage: {result['coverage_percentage']:.1f}%")
        
        # Print sample tile
        if result['tiles']:
            sample_tile = result['tiles'][0]
            print(f"Sample tile: {sample_tile['tile_id']} ({sample_tile['data_type']})")
            print(f"Confidence: {sample_tile['confidence']}")
        
        # Performance metrics
        metrics = fwd_service.get_performance_metrics()
        print(f"Performance metrics: {metrics}")
    
    asyncio.run(main())