"""
Kochi Metro Rail Limited (KMRL) Job Card & Work Order Manager.
Handles maintenance job cards (preventive, corrective, inspection, emergency),
work-order priorities, critical job identification, overdue status tracking, and Maximo CMMS integration.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

CATEGORIES = ["PREVENTIVE_MAINTENANCE", "CORRECTIVE_MAINTENANCE", "INSPECTION", "OVERHAUL", "EMERGENCY_REPAIR"]
PRIORITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
STATUSES = ["OPEN", "IN_PROGRESS", "COMPLETED", "CANCELLED"]

class KMRLJobCardManager:
    def __init__(self):
        # Maps job_id -> job card dictionary
        self._job_cards: Dict[str, Dict[str, Any]] = {}
        self._init_default_job_cards()

    def _init_default_job_cards(self):
        now = datetime.now()
        
        # 1. Preset test case 1: KM-101 - Open critical job card
        self._create_preset(
            job_id="JC-1001",
            job_number="JOB-2026-8810",
            train_id="KM-101",
            description="Traction Motor Thermal Alert & Brake Pad Wear Inspection",
            category="EMERGENCY_REPAIR",
            priority="CRITICAL",
            status="OPEN",
            due_date=(now + timedelta(hours=12)).isoformat(),
            estimated_duration_hours=3.5,
            source="TELEMETRY_ALERT",
            created_at=(now - timedelta(hours=2)).isoformat()
        )

        # 2. Preset test case 2: KM-102 - Closed / completed job card
        self._create_preset(
            job_id="JC-1002",
            job_number="JOB-2026-8811",
            train_id="KM-102",
            description="Routine 30-Day Inspection & HVAC Filter Replacement",
            category="PREVENTIVE_MAINTENANCE",
            priority="LOW",
            status="COMPLETED",
            due_date=(now - timedelta(days=1)).isoformat(),
            estimated_duration_hours=2.0,
            source="MAXIMO_CMMS",
            created_at=(now - timedelta(days=5)).isoformat()
        )

        # 3. Preset test case 3: KM-103 - Overdue job card
        self._create_preset(
            job_id="JC-1003",
            job_number="JOB-2026-8812",
            train_id="KM-103",
            description="Door Actuator Alignment & Limit Switch Calibration",
            category="CORRECTIVE_MAINTENANCE",
            priority="HIGH",
            status="OPEN",
            due_date=(now - timedelta(days=2)).isoformat(), # Overdue by 2 days
            estimated_duration_hours=4.0,
            source="MAXIMO_CMMS",
            created_at=(now - timedelta(days=7)).isoformat()
        )

        # Generate standard routine job cards for other trains
        for i in range(4, 26):
            t_id = f"KM-{100 + i}"
            prio = "MEDIUM" if i % 3 == 0 else "LOW"
            stat = "COMPLETED" if i % 2 == 0 else "OPEN"
            due_dt = (now + timedelta(days=i % 5 + 1)).isoformat() if stat == "OPEN" else (now - timedelta(days=i % 3 + 1)).isoformat()
            
            self._create_preset(
                job_id=f"JC-{1000 + i}",
                job_number=f"JOB-2026-{8810 + i}",
                train_id=t_id,
                description=f"Scheduled IBL Operational Checkup & Pantograph Clean",
                category="INSPECTION",
                priority=prio,
                status=stat,
                due_date=due_dt,
                estimated_duration_hours=1.5,
                source="MAXIMO_CMMS",
                created_at=(now - timedelta(days=3)).isoformat()
            )

    def _create_preset(
        self,
        job_id: str,
        job_number: str,
        train_id: str,
        description: str,
        category: str,
        priority: str,
        status: str,
        due_date: str,
        estimated_duration_hours: float,
        source: str,
        created_at: str
    ):
        self._job_cards[job_id.upper()] = {
            "job_id": job_id.upper(),
            "job_number": job_number,
            "train_id": train_id.upper(),
            "description": description,
            "category": category,
            "priority": priority.upper(),
            "status": status.upper(),
            "due_date": due_date,
            "estimated_duration_hours": estimated_duration_hours,
            "source": source,
            "created_at": created_at,
            "updated_at": created_at
        }

    def evaluate_job_card(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates dynamic attributes: is_critical and is_overdue.
        """
        now = datetime.now()
        due_date_dt = datetime.fromisoformat(job["due_date"])
        
        status = job["status"].upper()
        priority = job["priority"].upper()
        
        is_open = status in ["OPEN", "IN_PROGRESS"]
        is_critical = is_open and (priority in ["CRITICAL", "HIGH"])
        is_overdue = is_open and (due_date_dt < now)

        result = dict(job)
        result["is_critical"] = is_critical
        result["is_overdue"] = is_overdue
        return result

    def get_job_cards_for_train(
        self,
        train_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        is_critical: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        train_id_upper = train_id.upper()
        jobs = [j for j in self._job_cards.values() if j["train_id"] == train_id_upper]
        
        evaluated_jobs = [self.evaluate_job_card(j) for j in jobs]
        
        if status:
            evaluated_jobs = [j for j in evaluated_jobs if j["status"] == status.upper()]
        if priority:
            evaluated_jobs = [j for j in evaluated_jobs if j["priority"] == priority.upper()]
        if category:
            evaluated_jobs = [j for j in evaluated_jobs if j["category"].upper() == category.upper()]
        if is_critical is not None:
            evaluated_jobs = [j for j in evaluated_jobs if j["is_critical"] == is_critical]

        # Return newest created first
        return sorted(evaluated_jobs, key=lambda x: x["created_at"], reverse=True)

    def get_job_card_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self._job_cards.get(job_id.upper())
        if not job:
            return None
        return self.evaluate_job_card(job)

    def create_job_card(
        self,
        train_id: str,
        description: str,
        category: str = "CORRECTIVE_MAINTENANCE",
        priority: str = "MEDIUM",
        due_date: Optional[str] = None,
        estimated_duration_hours: float = 2.0,
        source: str = "MAXIMO_CMMS"
    ) -> Dict[str, Any]:
        now = datetime.now()
        job_id = f"JC-{uuid.uuid4().hex[:6].upper()}"
        job_num = f"JOB-2026-{uuid.uuid4().hex[:4].upper()}"
        
        due_str = due_date or (now + timedelta(days=2)).isoformat()

        job = {
            "job_id": job_id,
            "job_number": job_num,
            "train_id": train_id.upper(),
            "description": description,
            "category": category.upper(),
            "priority": priority.upper(),
            "status": "OPEN",
            "due_date": due_str,
            "estimated_duration_hours": estimated_duration_hours,
            "source": source,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        self._job_cards[job_id] = job
        return self.evaluate_job_card(job)

    def update_job_card(
        self,
        job_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        job_id_upper = job_id.upper()
        if job_id_upper not in self._job_cards:
            return None

        job = self._job_cards[job_id_upper]
        now = datetime.now().isoformat()

        if status:
            job["status"] = status.upper()
        if priority:
            job["priority"] = priority.upper()
        if description:
            job["description"] = description
        if due_date:
            job["due_date"] = due_date

        job["updated_at"] = now
        return self.evaluate_job_card(job)

    def get_open_critical_jobs_count(self, train_id: str) -> int:
        jobs = self.get_job_cards_for_train(train_id)
        return sum(1 for j in jobs if j["is_critical"])

# Global Job Card Manager Singleton
job_card_manager = KMRLJobCardManager()
