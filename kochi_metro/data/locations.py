"""
Kochi Metro Rail Limited (KMRL) Location, Depot, and Track Geometry Model.
Defines stations, depot stabling lines, inspection bays, track connections,
distance matrices, movement time/cost indices, and train location assignments.
"""

from typing import Dict, List, Any, Optional
from kochi_metro.data.generator import KOCHI_STATIONS

# -----------------------------------------------------------------------------
# 1. Depots Master Registry
# -----------------------------------------------------------------------------
KMRL_DEPOTS = [
    {
        "depot_id": "DEPOT-MUTTOM",
        "name": "Muttom Main Depot & Maintenance Workshop",
        "total_stabling_lines": 8,
        "total_inspection_bays": 4,
        "total_capacity": 20,
        "location_ids": [101, 102, 103, 104, 105, 106, 107, 108]
    },
    {
        "depot_id": "DEPOT-KAKKANAD",
        "name": "Kakkanad Pink Line Depot",
        "total_stabling_lines": 4,
        "total_inspection_bays": 2,
        "total_capacity": 10,
        "location_ids": [201, 202, 203, 204]
    }
]

# -----------------------------------------------------------------------------
# 2. Locations Master Registry (Stations + Depot Lines)
# -----------------------------------------------------------------------------
# Mainline Stations (IDs 1 to 24)
KMRL_LOCATIONS: Dict[int, Dict[str, Any]] = {}

for idx, station_name in enumerate(KOCHI_STATIONS, start=1):
    KMRL_LOCATIONS[idx] = {
        "location_id": idx,
        "name": f"{station_name} Station",
        "depot": "Blue Line Mainline",
        "type": "MAINLINE_STATION",
        "capacity": 2,
        "is_depot_track": False
    }

# Muttom Depot Tracks (IDs 101 to 108)
muttom_tracks = [
    (101, "Muttom Depot Stabling Line 1", "STABLING_LINE", 2),
    (102, "Muttom Depot Stabling Line 2", "STABLING_LINE", 2),
    (103, "Muttom Depot Stabling Line 3", "STABLING_LINE", 2),
    (104, "Muttom Depot Stabling Line 4", "STABLING_LINE", 2),
    (105, "Muttom Depot Inspection Bay 1", "INSPECTION_BAY", 1),
    (106, "Muttom Depot Inspection Bay 2", "INSPECTION_BAY", 1),
    (107, "Muttom Depot Heavy Maintenance Line", "HEAVY_MAINTENANCE", 1),
    (108, "Muttom Depot Automatic Wash Plant", "WASH_PLANT", 1),
]

for loc_id, name, loc_type, cap in muttom_tracks:
    KMRL_LOCATIONS[loc_id] = {
        "location_id": loc_id,
        "name": name,
        "depot": "Muttom Depot",
        "type": loc_type,
        "capacity": cap,
        "is_depot_track": True
    }

# Kakkanad Depot Tracks (IDs 201 to 204)
kakkanad_tracks = [
    (201, "Kakkanad Depot Stabling Line 1", "STABLING_LINE", 2),
    (202, "Kakkanad Depot Stabling Line 2", "STABLING_LINE", 2),
    (203, "Kakkanad Depot Inspection Bay 1", "INSPECTION_BAY", 1),
    (204, "Kakkanad Depot Wash Siding", "WASH_PLANT", 1),
]

for loc_id, name, loc_type, cap in kakkanad_tracks:
    KMRL_LOCATIONS[loc_id] = {
        "location_id": loc_id,
        "name": name,
        "depot": "Kakkanad Depot",
        "type": loc_type,
        "capacity": cap,
        "is_depot_track": True
    }

# -----------------------------------------------------------------------------
# 3. Track Connections & Distance/Cost Topology Graph
# -----------------------------------------------------------------------------
KMRL_CONNECTIONS: List[Dict[str, Any]] = []

# Mainline Station-to-Station Sequential Connections (IDs 1 to 24)
for i in range(1, len(KOCHI_STATIONS)):
    from_id = i
    to_id = i + 1
    dist = 1100.0 + (i % 5) * 150.0  # Approx 1.1km to 1.7km per inter-station hop
    time_min = round(dist / 600.0, 1) # ~35 km/h average commercial speed including dwell
    cost = round(dist * 0.05, 2)

    # Downstream (1 -> 2)
    KMRL_CONNECTIONS.append({
        "from_location_id": from_id,
        "from_location_name": KMRL_LOCATIONS[from_id]["name"],
        "to_location_id": to_id,
        "to_location_name": KMRL_LOCATIONS[to_id]["name"],
        "distance_meters": dist,
        "movement_time_minutes": time_min,
        "movement_cost": cost,
        "track_type": "MAINLINE"
    })
    # Upstream (2 -> 1)
    KMRL_CONNECTIONS.append({
        "from_location_id": to_id,
        "from_location_name": KMRL_LOCATIONS[to_id]["name"],
        "to_location_id": from_id,
        "to_location_name": KMRL_LOCATIONS[from_id]["name"],
        "distance_meters": dist,
        "movement_time_minutes": time_min,
        "movement_cost": cost,
        "track_type": "MAINLINE"
    })

# Muttom Station (ID 5) <-> Muttom Depot Tracks (IDs 101 to 108) Shunting Connections
for loc_id in range(101, 109):
    shunting_dist = 400.0 + (loc_id - 100) * 50.0
    shunting_time = round(shunting_dist / 150.0, 1) # Low shunting speed ~9 km/h
    shunting_cost = round(shunting_dist * 0.1, 2)

    KMRL_CONNECTIONS.append({
        "from_location_id": 5, # Muttom Station
        "from_location_name": KMRL_LOCATIONS[5]["name"],
        "to_location_id": loc_id,
        "to_location_name": KMRL_LOCATIONS[loc_id]["name"],
        "distance_meters": shunting_dist,
        "movement_time_minutes": shunting_time,
        "movement_cost": shunting_cost,
        "track_type": "DEPOT_SHUNTING"
    })
    KMRL_CONNECTIONS.append({
        "from_location_id": loc_id,
        "from_location_name": KMRL_LOCATIONS[loc_id]["name"],
        "to_location_id": 5,
        "to_location_name": KMRL_LOCATIONS[5]["name"],
        "distance_meters": shunting_dist,
        "movement_time_minutes": shunting_time,
        "movement_cost": shunting_cost,
        "track_type": "DEPOT_SHUNTING"
    })

# -----------------------------------------------------------------------------
# 4. Train Location Tracking Manager
# -----------------------------------------------------------------------------
class KMRLTrainLocationManager:
    def __init__(self):
        # Initial default placement of 25 trains across Muttom Depot & Mainline stations
        self._train_locations: Dict[str, int] = {}
        for i in range(25):
            t_id = f"KM-{101 + i}"
            if i < 8:
                # Park first 8 trains in Muttom Depot Stabling Lines
                self._train_locations[t_id] = 101 + i
            elif i < 12:
                # Park next 4 trains in Kakkanad Depot
                self._train_locations[t_id] = 201 + (i - 8)
            else:
                # Distribute remaining 13 trains across mainline stations
                self._train_locations[t_id] = (i - 12) * 2 + 1

    def is_valid_location_id(self, location_id: int) -> bool:
        return location_id in KMRL_LOCATIONS

    def get_train_location_id(self, train_id: str) -> Optional[int]:
        return self._train_locations.get(train_id.upper())

    def update_train_location(self, train_id: str, location_id: int) -> bool:
        if not self.is_valid_location_id(location_id):
            return False
        self._train_locations[train_id.upper()] = location_id
        return True

    def get_stabled_trains_for_location(self, location_id: int) -> List[str]:
        return [t_id for t_id, loc_id in self._train_locations.items() if loc_id == location_id]

    def get_location_details(self, location_id: int) -> Optional[Dict[str, Any]]:
        loc = KMRL_LOCATIONS.get(location_id)
        if not loc:
            return None
        
        stabled_trains = self.get_stabled_trains_for_location(location_id)
        occupied_count = len(stabled_trains)
        available_capacity = max(0, loc["capacity"] - occupied_count)

        return {
            "location_id": loc["location_id"],
            "name": loc["name"],
            "depot": loc["depot"],
            "type": loc["type"],
            "capacity": loc["capacity"],
            "occupied_count": occupied_count,
            "available_capacity": available_capacity,
            "stabled_train_ids": stabled_trains,
            "is_depot_track": loc["is_depot_track"]
        }

    def get_all_locations_with_occupancy(self) -> List[Dict[str, Any]]:
        results = []
        for loc_id in sorted(KMRL_LOCATIONS.keys()):
            details = self.get_location_details(loc_id)
            if details:
                results.append(details)
        return results

    def get_depot_summaries(self) -> List[Dict[str, Any]]:
        depots_summary = []
        for depot in KMRL_DEPOTS:
            loc_ids = depot["location_ids"]
            stabled_trains = []
            current_occ = 0
            for lid in loc_ids:
                trains = self.get_stabled_trains_for_location(lid)
                stabled_trains.extend(trains)
                current_occ += len(trains)

            avail = max(0, depot["total_capacity"] - current_occ)
            depots_summary.append({
                "depot_id": depot["depot_id"],
                "name": depot["name"],
                "total_stabling_lines": depot["total_stabling_lines"],
                "total_inspection_bays": depot["total_inspection_bays"],
                "total_capacity": depot["total_capacity"],
                "current_occupancy": current_occ,
                "available_capacity": avail,
                "stabled_train_ids": stabled_trains,
                "location_ids": loc_ids
            })
        return depots_summary

    def get_connections_for_location(self, location_id: int) -> List[Dict[str, Any]]:
        return [c for c in KMRL_CONNECTIONS if c["from_location_id"] == location_id]

# Global Location Manager Singleton
location_manager = KMRLTrainLocationManager()
