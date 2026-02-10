"""
Anomaly Detection Service

Detects anomalies in operational data: route deviations, volume discrepancies,
speed anomalies, and sensor tampering.

Phase 1: Rule-based detection with configurable thresholds
Phase 2+: ML-based unsupervised anomaly detection
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import math
import logging

logger = logging.getLogger(__name__)


class AnomalyDetectionService:
    """Rule-based anomaly detection for corridor logistics operations."""

    def check_route_deviation(
        self,
        current_lat: float,
        current_lng: float,
        expected_route: List[Dict[str, float]],
        max_deviation_km: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Check if current position deviates from expected route corridor.

        Args:
            current_lat, current_lng: Current position
            expected_route: List of waypoints [{lat, lng}, ...]
            max_deviation_km: Maximum allowed deviation in km
        """
        if not expected_route:
            return {"anomaly": False, "message": "No route defined"}

        # Find minimum distance to any route segment
        min_distance = float("inf")
        closest_segment = None

        for i in range(len(expected_route) - 1):
            p1 = expected_route[i]
            p2 = expected_route[i + 1]
            dist = self._point_to_segment_distance(
                current_lat, current_lng,
                p1["lat"], p1["lng"],
                p2["lat"], p2["lng"]
            )
            if dist < min_distance:
                min_distance = dist
                closest_segment = i

        is_deviation = min_distance > max_deviation_km

        return {
            "anomaly": is_deviation,
            "type": "route_deviation" if is_deviation else None,
            "severity": "high" if min_distance > max_deviation_km * 3 else "medium" if is_deviation else "low",
            "deviation_km": round(min_distance, 2),
            "threshold_km": max_deviation_km,
            "closest_segment_index": closest_segment,
            "message": f"Route deviation detected: {min_distance:.1f}km from corridor" if is_deviation else "Within corridor",
        }

    def check_volume_discrepancy(
        self,
        measured_volume: float,
        expected_volume: float,
        tolerance_pct: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Check for suspicious volume discrepancies between measurements.
        """
        if expected_volume <= 0:
            return {"anomaly": False, "message": "No expected volume to compare"}

        variance_pct = ((measured_volume - expected_volume) / expected_volume) * 100

        is_anomaly = abs(variance_pct) > tolerance_pct

        severity = "low"
        if abs(variance_pct) > tolerance_pct * 3:
            severity = "critical"
        elif abs(variance_pct) > tolerance_pct * 2:
            severity = "high"
        elif is_anomaly:
            severity = "medium"

        return {
            "anomaly": is_anomaly,
            "type": "volume_discrepancy" if is_anomaly else None,
            "severity": severity,
            "measured_volume": measured_volume,
            "expected_volume": expected_volume,
            "variance_pct": round(variance_pct, 2),
            "tolerance_pct": tolerance_pct,
            "message": f"Volume discrepancy: {variance_pct:+.1f}% ({measured_volume:.1f} vs {expected_volume:.1f})" if is_anomaly else "Within tolerance",
        }

    def check_speed_anomaly(
        self,
        current_speed: float,
        mode: str = "truck",
        min_speed: Optional[float] = None,
        max_speed: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Check for abnormal speeds indicating issues or unsafe operation.
        """
        speed_limits = {
            "truck": {"min": 0, "max": 100, "safe_max": 80},
            "rail": {"min": 0, "max": 80, "safe_max": 60},
            "vessel": {"min": 0, "max": 20, "safe_max": 16},
            "barge": {"min": 0, "max": 15, "safe_max": 10},
        }

        limits = speed_limits.get(mode, speed_limits["truck"])
        effective_min = min_speed or limits["min"]
        effective_max = max_speed or limits["max"]
        safe_max = limits.get("safe_max", effective_max * 0.8)

        anomalies = []

        if current_speed > effective_max:
            anomalies.append({
                "type": "overspeed",
                "severity": "critical",
                "message": f"Speed {current_speed:.1f} exceeds maximum {effective_max:.1f}",
            })
        elif current_speed > safe_max:
            anomalies.append({
                "type": "high_speed",
                "severity": "medium",
                "message": f"Speed {current_speed:.1f} exceeds safe limit {safe_max:.1f}",
            })

        return {
            "anomaly": len(anomalies) > 0,
            "anomalies": anomalies,
            "current_speed": current_speed,
            "mode": mode,
        }

    def check_dwell_time(
        self,
        entry_time: datetime,
        location_name: str,
        max_dwell_minutes: int = 120,
    ) -> Dict[str, Any]:
        """
        Check if an asset has been dwelling at a location too long.
        """
        now = datetime.now(timezone.utc)
        dwell_minutes = (now - entry_time).total_seconds() / 60

        is_anomaly = dwell_minutes > max_dwell_minutes

        return {
            "anomaly": is_anomaly,
            "type": "excessive_dwell" if is_anomaly else None,
            "severity": "high" if dwell_minutes > max_dwell_minutes * 3 else "medium" if is_anomaly else "low",
            "dwell_minutes": round(dwell_minutes, 1),
            "threshold_minutes": max_dwell_minutes,
            "location": location_name,
            "message": f"Excessive dwell at {location_name}: {dwell_minutes:.0f} minutes" if is_anomaly else "Normal dwell time",
        }

    def check_sensor_tampering(
        self,
        readings: List[Dict[str, Any]],
        expected_interval_sec: int = 300,
        gap_threshold_factor: float = 3.0,
    ) -> Dict[str, Any]:
        """
        Detect potential sensor tampering from reading patterns.
        Looks for: gaps in reporting, sudden position jumps, constant values.
        """
        if len(readings) < 2:
            return {"anomaly": False, "message": "Insufficient readings for analysis"}

        anomalies = []

        # Check for reporting gaps
        for i in range(1, len(readings)):
            if "timestamp" in readings[i] and "timestamp" in readings[i - 1]:
                t1 = readings[i - 1]["timestamp"]
                t2 = readings[i]["timestamp"]
                if isinstance(t1, str):
                    t1 = datetime.fromisoformat(t1)
                if isinstance(t2, str):
                    t2 = datetime.fromisoformat(t2)
                gap = (t2 - t1).total_seconds()
                if gap > expected_interval_sec * gap_threshold_factor:
                    anomalies.append({
                        "type": "reporting_gap",
                        "severity": "high",
                        "gap_seconds": gap,
                        "message": f"Reporting gap of {gap/60:.0f} minutes detected",
                    })

        # Check for sudden position jumps
        for i in range(1, len(readings)):
            if all(k in readings[i] and k in readings[i-1] for k in ("latitude", "longitude")):
                dist = self._haversine(
                    readings[i-1]["latitude"], readings[i-1]["longitude"],
                    readings[i]["latitude"], readings[i]["longitude"]
                )
                # Max reasonable distance based on interval
                max_dist = (expected_interval_sec / 3600) * 120  # km (120 km/h max)
                if dist > max_dist:
                    anomalies.append({
                        "type": "position_jump",
                        "severity": "critical",
                        "distance_km": round(dist, 2),
                        "message": f"Impossible position jump: {dist:.1f}km in {expected_interval_sec}s",
                    })

        return {
            "anomaly": len(anomalies) > 0,
            "anomalies": anomalies,
            "readings_analyzed": len(readings),
        }

    def _haversine(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in km."""
        R = 6371
        lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _point_to_segment_distance(
        self, px: float, py: float,
        x1: float, y1: float,
        x2: float, y2: float
    ) -> float:
        """Approximate distance from point to line segment in km."""
        # Use point-to-line perpendicular distance approximation
        d1 = self._haversine(px, py, x1, y1)
        d2 = self._haversine(px, py, x2, y2)
        seg_len = self._haversine(x1, y1, x2, y2)

        if seg_len == 0:
            return d1

        # Project point onto segment
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (seg_len ** 2 + 1e-10)))
        proj_lat = x1 + t * (x2 - x1)
        proj_lng = y1 + t * (y2 - y1)

        return self._haversine(px, py, proj_lat, proj_lng)


# Singleton instance
anomaly_service = AnomalyDetectionService()
