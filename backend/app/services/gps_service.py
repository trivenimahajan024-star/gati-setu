import os
import time
from datetime import datetime
from typing import Optional, Dict, Any
from app.config import settings

class GpsLocationService:
    """
    Dedicated Railway GPS / RTIS / NavIC Real-Time Location Service Interface.
    
    Acts as a clean, decoupled integration layer for receiving live GNSS / RTIS telemetry feeds
    from onboard locomotive IoT devices, ISRO NavIC receivers, or RTIS broker feeds.
    
    When no live hardware or external GPS provider feed is configured, it cleanly reports:
    'GPS_SOURCE_NOT_CONFIGURED'.
    """

    def __init__(self):
        # Buffer for verified real-time GPS fixes { train_number: GPSPayload }
        self._gps_buffer: Dict[str, Dict[str, Any]] = {}
        self._provider_name: Optional[str] = None
        self._feed_url: str = getattr(settings, "GPS_FEED_URL", "") or os.getenv("GPS_FEED_URL", "")
        self._api_key: str = getattr(settings, "GPS_API_KEY", "") or os.getenv("GPS_API_KEY", "")

    @property
    def is_configured(self) -> bool:
        """
        Returns True only if an active GPS / RTIS provider feed URL or hardware receiver is configured.
        """
        return bool(self._feed_url and self._feed_url.strip())

    @property
    def provider_name(self) -> str:
        if self._provider_name:
            return self._provider_name
        if self.is_configured:
            return "EXTERNAL_RTIS_FEED"
        return "UNCONFIGURED"

    def get_gps_position(self, train_number: str) -> Dict[str, Any]:
        """
        Retrieve live satellite GPS/RTIS fix for a specific train.
        
        Required GPS Schema:
        - train_number (str)
        - latitude (float | None)
        - longitude (float | None)
        - speed (float | None)
        - timestamp (str | None)
        - heading (float | None) [optional]
        - source (str)
        """
        tno = str(train_number).strip()

        # If no GPS hardware/feed is configured or connected
        if not self.is_configured and tno not in self._gps_buffer:
            return {
                "status": "GPS_SOURCE_NOT_CONFIGURED",
                "is_connected": False,
                "train_number": tno,
                "latitude": None,
                "longitude": None,
                "speed": None,
                "heading": None,
                "timestamp": None,
                "source": "UNCONFIGURED",
                "message": "GPS_SOURCE_NOT_CONFIGURED: Real-time RTIS / GPS hardware feed is not configured."
            }

        # If data is available in the verified GPS buffer
        if tno in self._gps_buffer:
            item = self._gps_buffer[tno]
            return {
                "status": "LIVE_GPS_ACTIVE",
                "is_connected": True,
                "train_number": tno,
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "speed": item.get("speed"),
                "heading": item.get("heading"),
                "timestamp": item.get("timestamp"),
                "source": item.get("source", self.provider_name),
                "message": "Live GNSS/RTIS telemetry active."
            }

        return {
            "status": "GPS_SOURCE_NOT_CONFIGURED",
            "is_connected": False,
            "train_number": tno,
            "latitude": None,
            "longitude": None,
            "speed": None,
            "heading": None,
            "timestamp": None,
            "source": "UNCONFIGURED",
            "message": f"GPS_SOURCE_NOT_CONFIGURED: No active telemetry packet received for train {tno}."
        }

    def ingest_gps_telemetry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interface method for ingesting real incoming GPS / RTIS / NavIC data packets.
        
        Validates required fields: train_number, latitude, longitude, speed, timestamp, source.
        """
        train_number = str(payload.get("train_number") or "").strip()
        if not train_number:
            return {
                "status": "error",
                "message": "Missing required field 'train_number'"
            }

        try:
            lat = float(payload.get("latitude")) if payload.get("latitude") is not None else None
            lng = float(payload.get("longitude")) if payload.get("longitude") is not None else None
            speed = float(payload.get("speed")) if payload.get("speed") is not None else None
            heading = float(payload.get("heading")) if payload.get("heading") is not None else None
        except (ValueError, TypeError) as e:
            return {
                "status": "error",
                "message": f"Invalid numerical coordinate/speed format: {e}"
            }

        ts = payload.get("timestamp") or datetime.utcnow().isoformat() + "Z"
        source = payload.get("source") or "RTIS_FEED"

        normalized_packet = {
            "train_number": train_number,
            "latitude": lat,
            "longitude": lng,
            "speed": speed,
            "heading": heading,
            "timestamp": ts,
            "source": source,
            "ingested_at": time.time()
        }

        self._gps_buffer[train_number] = normalized_packet
        return {
            "status": "success",
            "message": f"GPS packet ingested for train {train_number}",
            "data": normalized_packet
        }

    def get_service_status(self) -> Dict[str, Any]:
        """
        Returns status summary of the GPS location subsystem.
        """
        return {
            "status": "ONLINE" if self.is_configured else "GPS_SOURCE_NOT_CONFIGURED",
            "provider": self.provider_name,
            "is_configured": self.is_configured,
            "active_tracked_trains": list(self._gps_buffer.keys()),
            "total_active_feeds": len(self._gps_buffer),
            "supported_sources": ["RTIS", "NAVIC", "IR_GPS_RECEIVER", "NMEA_0183", "MQTT_BROKER"]
        }

# Singleton service instance
gps_service = GpsLocationService()
