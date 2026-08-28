"""
Kochi Metro Rail Limited (KMRL) Job Card & Work Order Manager.

Handles:
- Maintenance job cards
- Preventive/corrective/inspection/overhaul/emergency work
- Work-order priorities
- Critical job identification
- High-priority warnings
- Overdue status tracking
- Maximo-compatible source information
- Reusable eligibility checks

NOTE:
This is a prototype/demo data manager.
It does NOT represent a live IBM Maximo connection.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid


# ============================================================
# CONSTANTS
# ============================================================

CATEGORIES = [
    "PREVENTIVE_MAINTENANCE",
    "CORRECTIVE_MAINTENANCE",
    "INSPECTION",
    "OVERHAUL",
    "EMERGENCY_REPAIR",
]

PRIORITIES = [
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW",
]

STATUSES = [
    "OPEN",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELLED",
]


# ============================================================
# JOB CARD MANAGER
# ============================================================

class KMRLJobCardManager:
    """
    In-memory manager for KMRL train maintenance job cards.

    The manager is intentionally lightweight for the SIH prototype.
    A future implementation can replace the internal dictionary
    with PostgreSQL / Maximo integration without changing the API
    contract significantly.
    """

    def __init__(self):
        # Maps job_id -> job card
        self._job_cards: Dict[str, Dict[str, Any]] = {}

        # Initialize simulated/demo job cards.
        self._init_default_job_cards()

    # ========================================================
    # TRAIN VALIDATION
    # ========================================================

    def _train_exists(self, train_id: str) -> bool:
        """
        Validate that a train exists in the current KMRL fleet.

        Current prototype fleet:
            KM-101 ... KM-125

        This is intentionally kept in one function so that it can
        later be replaced by the project's actual train registry.
        """

        if not train_id:
            return False

        train_id = train_id.upper().strip()

        try:
            number = int(train_id.split("-")[1])
        except (IndexError, ValueError):
            return False

        return 101 <= number <= 125

    # ========================================================
    # VALIDATION HELPERS
    # ========================================================

    @staticmethod
    def _validate_category(category: str) -> str:
        """Validate and normalize job category."""

        value = category.upper().strip()

        if value not in CATEGORIES:
            raise ValueError(
                f"Invalid job category '{category}'. "
                f"Allowed values: {', '.join(CATEGORIES)}"
            )

        return value

    @staticmethod
    def _validate_priority(priority: str) -> str:
        """Validate and normalize job priority."""

        value = priority.upper().strip()

        if value not in PRIORITIES:
            raise ValueError(
                f"Invalid job priority '{priority}'. "
                f"Allowed values: {', '.join(PRIORITIES)}"
            )

        return value

    @staticmethod
    def _validate_status(status: str) -> str:
        """Validate and normalize job status."""

        value = status.upper().strip()

        if value not in STATUSES:
            raise ValueError(
                f"Invalid job status '{status}'. "
                f"Allowed values: {', '.join(STATUSES)}"
            )

        return value

    @staticmethod
    def _validate_due_date(due_date: str) -> str:
        """Validate ISO-format due date."""

        try:
            datetime.fromisoformat(due_date)
        except (ValueError, TypeError):
            raise ValueError(
                "due_date must be a valid ISO-8601 datetime."
            )

        return due_date

    # ========================================================
    # DEFAULT / DEMO DATA
    # ========================================================

    def _init_default_job_cards(self):
        """
        Create simulated job cards for the 25-train prototype fleet.

        These records represent the kind of data that could later
        originate from IBM Maximo.
        """

        now = datetime.now()

        # ----------------------------------------------------
        # KM-101
        # Critical open maintenance job
        # ----------------------------------------------------

        self._create_preset(
            job_id="JC-1001",
            job_number="JOB-2026-8810",
            train_id="KM-101",
            description=(
                "Traction Motor Thermal Alert & "
                "Brake Pad Wear Inspection"
            ),
            category="EMERGENCY_REPAIR",
            priority="CRITICAL",
            status="OPEN",
            due_date=(
                now + timedelta(hours=12)
            ).isoformat(),
            estimated_duration_hours=3.5,
            source="TELEMETRY_ALERT",
            created_at=(
                now - timedelta(hours=2)
            ).isoformat(),
        )

        # ----------------------------------------------------
        # KM-102
        # Completed job
        # ----------------------------------------------------

        self._create_preset(
            job_id="JC-1002",
            job_number="JOB-2026-8811",
            train_id="KM-102",
            description=(
                "Routine 30-Day Inspection & "
                "HVAC Filter Replacement"
            ),
            category="PREVENTIVE_MAINTENANCE",
            priority="LOW",
            status="COMPLETED",
            due_date=(
                now - timedelta(days=1)
            ).isoformat(),
            estimated_duration_hours=2.0,
            source="MAXIMO_CMMS",
            created_at=(
                now - timedelta(days=5)
            ).isoformat(),
        )

        # ----------------------------------------------------
        # KM-103
        # High-priority overdue job
        # ----------------------------------------------------

        self._create_preset(
            job_id="JC-1003",
            job_number="JOB-2026-8812",
            train_id="KM-103",
            description=(
                "Door Actuator Alignment & "
                "Limit Switch Calibration"
            ),
            category="CORRECTIVE_MAINTENANCE",
            priority="HIGH",
            status="OPEN",
            due_date=(
                now - timedelta(days=2)
            ).isoformat(),
            estimated_duration_hours=4.0,
            source="MAXIMO_CMMS",
            created_at=(
                now - timedelta(days=7)
            ).isoformat(),
        )

        # ----------------------------------------------------
        # KM-104 ... KM-125
        # Routine simulated job cards
        # ----------------------------------------------------

        for i in range(4, 26):

            train_id = f"KM-{100 + i}"

            priority = (
                "MEDIUM"
                if i % 3 == 0
                else "LOW"
            )

            status = (
                "COMPLETED"
                if i % 2 == 0
                else "OPEN"
            )

            if status == "OPEN":
                due_date = (
                    now + timedelta(days=(i % 5) + 1)
                ).isoformat()
            else:
                due_date = (
                    now - timedelta(days=(i % 3) + 1)
                ).isoformat()

            self._create_preset(
                job_id=f"JC-{1000 + i}",
                job_number=f"JOB-2026-{8810 + i}",
                train_id=train_id,
                description=(
                    "Scheduled IBL Operational Checkup "
                    "& Pantograph Clean"
                ),
                category="INSPECTION",
                priority=priority,
                status=status,
                due_date=due_date,
                estimated_duration_hours=1.5,
                source="MAXIMO_CMMS",
                created_at=(
                    now - timedelta(days=3)
                ).isoformat(),
            )

    # ========================================================
    # INTERNAL PRESET CREATION
    # ========================================================

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
        created_at: str,
    ):
        """
        Create a predefined job card.

        Internal/demo use only.
        """

        train_id = train_id.upper().strip()

        if not self._train_exists(train_id):
            raise ValueError(
                f"Cannot create job card for unknown train '{train_id}'."
            )

        category = self._validate_category(category)
        priority = self._validate_priority(priority)
        status = self._validate_status(status)
        due_date = self._validate_due_date(due_date)

        self._job_cards[job_id.upper()] = {
            "job_id": job_id.upper(),
            "job_number": job_number,
            "train_id": train_id,
            "description": description,
            "category": category,
            "priority": priority,
            "status": status,
            "due_date": due_date,
            "estimated_duration_hours": estimated_duration_hours,
            "source": source,
            "created_at": created_at,
            "updated_at": created_at,
        }

    # ========================================================
    # JOB EVALUATION
    # ========================================================

    def evaluate_job_card(
        self,
        job: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Dynamically calculate operational attributes.

        Important distinction:

        CRITICAL + OPEN/IN_PROGRESS
            -> is_critical = True
            -> blocking condition

        HIGH + OPEN/IN_PROGRESS
            -> is_high_priority = True
            -> warning, NOT automatically blocking

        MEDIUM/LOW
            -> normal maintenance condition

        COMPLETED/CANCELLED
            -> not active
        """

        now = datetime.now()

        due_date_dt = datetime.fromisoformat(
            job["due_date"]
        )

        status = job["status"].upper()
        priority = job["priority"].upper()

        # ----------------------------------------------------
        # Active job
        # ----------------------------------------------------

        is_open = status in {
            "OPEN",
            "IN_PROGRESS",
        }

        # ----------------------------------------------------
        # CRITICAL = actual blocking maintenance condition
        # ----------------------------------------------------

        is_critical = (
            is_open
            and priority == "CRITICAL"
        )

        # ----------------------------------------------------
        # HIGH = warning, not automatically blocking
        # ----------------------------------------------------

        is_high_priority = (
            is_open
            and priority == "HIGH"
        )

        # ----------------------------------------------------
        # Overdue
        # ----------------------------------------------------

        is_overdue = (
            is_open
            and due_date_dt < now
        )

        # ----------------------------------------------------
        # Calculate overdue duration
        # ----------------------------------------------------

        overdue_hours = 0.0

        if is_overdue:
            overdue_hours = round(
                (now - due_date_dt).total_seconds()
                / 3600,
                2,
            )

        # ----------------------------------------------------
        # Determine operational classification
        # ----------------------------------------------------

        if is_critical:
            operational_status = "BLOCKING"

        elif is_high_priority:
            operational_status = "WARNING"

        elif is_overdue:
            operational_status = "OVERDUE_WARNING"

        elif is_open:
            operational_status = "OPEN_NORMAL"

        else:
            operational_status = "CLOSED_OR_INACTIVE"

        result = dict(job)

        result["is_open"] = is_open
        result["is_critical"] = is_critical
        result["is_high_priority"] = is_high_priority
        result["is_overdue"] = is_overdue
        result["overdue_hours"] = overdue_hours
        result["operational_status"] = operational_status

        return result

    # ========================================================
    # GET JOB CARDS FOR TRAIN
    # ========================================================

    def get_job_cards_for_train(
        self,
        train_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        is_critical: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return evaluated job cards belonging to a train.
        """

        train_id_upper = train_id.upper().strip()

        if not self._train_exists(train_id_upper):
            return []

        jobs = [
            job
            for job in self._job_cards.values()
            if job["train_id"] == train_id_upper
        ]

        evaluated_jobs = [
            self.evaluate_job_card(job)
            for job in jobs
        ]

        # ----------------------------------------------------
        # Filters
        # ----------------------------------------------------

        if status:
            status = self._validate_status(status)

            evaluated_jobs = [
                job
                for job in evaluated_jobs
                if job["status"] == status
            ]

        if priority:
            priority = self._validate_priority(priority)

            evaluated_jobs = [
                job
                for job in evaluated_jobs
                if job["priority"] == priority
            ]

        if category:
            category = self._validate_category(category)

            evaluated_jobs = [
                job
                for job in evaluated_jobs
                if job["category"] == category
            ]

        if is_critical is not None:
            evaluated_jobs = [
                job
                for job in evaluated_jobs
                if job["is_critical"] == is_critical
            ]

        # Newest first
        return sorted(
            evaluated_jobs,
            key=lambda job: job["created_at"],
            reverse=True,
        )

    # ========================================================
    # GET JOB BY ID
    # ========================================================

    def get_job_card_by_id(
        self,
        job_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Return a single evaluated job card.
        """

        job = self._job_cards.get(
            job_id.upper().strip()
        )

        if not job:
            return None

        return self.evaluate_job_card(job)

    # ========================================================
    # CREATE JOB CARD
    # ========================================================

    def create_job_card(
        self,
        train_id: str,
        description: str,
        category: str = "CORRECTIVE_MAINTENANCE",
        priority: str = "MEDIUM",
        due_date: Optional[str] = None,
        estimated_duration_hours: float = 2.0,
        source: str = "MAXIMO_CMMS",
    ) -> Dict[str, Any]:
        """
        Create a new OPEN job card.
        """

        train_id = train_id.upper().strip()

        # ----------------------------------------------------
        # Validate train
        # ----------------------------------------------------

        if not self._train_exists(train_id):
            raise ValueError(
                f"Train '{train_id}' does not exist in the KMRL fleet."
            )

        # ----------------------------------------------------
        # Validate fields
        # ----------------------------------------------------

        category = self._validate_category(category)
        priority = self._validate_priority(priority)

        if not description or not description.strip():
            raise ValueError(
                "Job description cannot be empty."
            )

        if estimated_duration_hours <= 0:
            raise ValueError(
                "estimated_duration_hours must be greater than zero."
            )

        # ----------------------------------------------------
        # Due date
        # ----------------------------------------------------

        now = datetime.now()

        if due_date is None:
            due_date = (
                now + timedelta(days=2)
            ).isoformat()
        else:
            due_date = self._validate_due_date(
                due_date
            )

        # ----------------------------------------------------
        # IDs
        # ----------------------------------------------------

        job_id = (
            f"JC-{uuid.uuid4().hex[:6].upper()}"
        )

        job_number = (
            f"JOB-2026-{uuid.uuid4().hex[:4].upper()}"
        )

        # ----------------------------------------------------
        # Create
        # ----------------------------------------------------

        job = {
            "job_id": job_id,
            "job_number": job_number,
            "train_id": train_id,
            "description": description.strip(),
            "category": category,
            "priority": priority,
            "status": "OPEN",
            "due_date": due_date,
            "estimated_duration_hours": estimated_duration_hours,
            "source": source,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        self._job_cards[job_id] = job

        return self.evaluate_job_card(job)

    # ========================================================
    # UPDATE JOB CARD
    # ========================================================

    def update_job_card(
        self,
        job_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing job card.
        """

        job_id_upper = job_id.upper().strip()

        if job_id_upper not in self._job_cards:
            return None

        job = self._job_cards[job_id_upper]

        # ----------------------------------------------------
        # Validate updates before modifying state
        # ----------------------------------------------------

        if status is not None:
            status = self._validate_status(status)

        if priority is not None:
            priority = self._validate_priority(priority)

        if due_date is not None:
            due_date = self._validate_due_date(due_date)

        if description is not None:
            if not description.strip():
                raise ValueError(
                    "Job description cannot be empty."
                )

        # ----------------------------------------------------
        # Apply updates
        # ----------------------------------------------------

        if status is not None:
            job["status"] = status

        if priority is not None:
            job["priority"] = priority

        if description is not None:
            job["description"] = description.strip()

        if due_date is not None:
            job["due_date"] = due_date

        job["updated_at"] = datetime.now().isoformat()

        return self.evaluate_job_card(job)

    # ========================================================
    # JOB COUNTS
    # ========================================================

    def get_open_jobs_count(
        self,
        train_id: str,
    ) -> int:
        """Return number of active/open jobs."""

        jobs = self.get_job_cards_for_train(
            train_id
        )

        return sum(
            1
            for job in jobs
            if job["is_open"]
        )

    def get_open_critical_jobs_count(
        self,
        train_id: str,
    ) -> int:
        """
        Return number of CRITICAL + active jobs.

        These are the jobs that should act as blocking
        conditions for service eligibility.
        """

        jobs = self.get_job_cards_for_train(
            train_id
        )

        return sum(
            1
            for job in jobs
            if job["is_critical"]
        )

    def get_high_priority_jobs_count(
        self,
        train_id: str,
    ) -> int:
        """Return number of active HIGH-priority jobs."""

        jobs = self.get_job_cards_for_train(
            train_id
        )

        return sum(
            1
            for job in jobs
            if job["is_high_priority"]
        )

    def get_overdue_jobs_count(
        self,
        train_id: str,
    ) -> int:
        """Return number of active overdue jobs."""

        jobs = self.get_job_cards_for_train(
            train_id
        )

        return sum(
            1
            for job in jobs
            if job["is_overdue"]
        )

    # ========================================================
    # TRAIN JOB SUMMARY
    # ========================================================

    def get_job_summary_for_train(
        self,
        train_id: str,
    ) -> Dict[str, Any]:
        """
        Return a compact maintenance summary for a train.
        """

        jobs = self.get_job_cards_for_train(
            train_id
        )

        total = len(jobs)

        open_count = sum(
            1
            for job in jobs
            if job["is_open"]
        )

        critical_open = sum(
            1
            for job in jobs
            if job["is_critical"]
        )

        high_priority = sum(
            1
            for job in jobs
            if job["is_high_priority"]
        )

        overdue = sum(
            1
            for job in jobs
            if job["is_overdue"]
        )

        in_progress = sum(
            1
            for job in jobs
            if job["status"] == "IN_PROGRESS"
        )

        completed = sum(
            1
            for job in jobs
            if job["status"] == "COMPLETED"
        )

        return {
            "train_id": train_id.upper(),
            "total": total,
            "open": open_count,
            "critical_open": critical_open,
            "high_priority_open": high_priority,
            "overdue": overdue,
            "in_progress": in_progress,
            "completed": completed,
        }

    # ========================================================
    # ELIGIBILITY CHECK
    # ========================================================

    def check_job_card_eligibility(
        self,
        train_id: str,
    ) -> Dict[str, Any]:
        """
        Determine whether job cards create a blocking
        condition for revenue-service eligibility.

        IMPORTANT:
        This function does NOT decide overall train eligibility.

        It only evaluates the JOB-CARD portion.

        CRITICAL + OPEN/IN_PROGRESS
            -> BLOCKED

        HIGH + OPEN/IN_PROGRESS
            -> WARNING

        MEDIUM/LOW
            -> WARNING/NORMAL depending on overdue state

        COMPLETED/CANCELLED
            -> PASS
        """

        train_id = train_id.upper().strip()

        if not self._train_exists(train_id):
            raise ValueError(
                f"Train '{train_id}' does not exist."
            )

        jobs = self.get_job_cards_for_train(
            train_id
        )

        blocking_reasons: List[str] = []
        warnings: List[str] = []

        # ----------------------------------------------------
        # Evaluate every active job
        # ----------------------------------------------------

        for job in jobs:

            # Critical job
            if job["is_critical"]:

                blocking_reasons.append(
                    f"Critical open job card "
                    f"{job['job_number']} requires maintenance."
                )

            # High priority
            elif job["is_high_priority"]:

                warnings.append(
                    f"High-priority job card "
                    f"{job['job_number']} is "
                    f"{job['status']}."
                )

            # Overdue
            if job["is_overdue"]:

                warnings.append(
                    f"Job card {job['job_number']} "
                    f"is overdue by approximately "
                    f"{job['overdue_hours']} hours."
                )

        passed = len(blocking_reasons) == 0

        return {
            "train_id": train_id,
            "passed": passed,
            "status": (
                "BLOCKED"
                if not passed
                else (
                    "WARNING"
                    if warnings
                    else "PASS"
                )
            ),
            "blocking_reasons": blocking_reasons,
            "warnings": warnings,
            "summary": self.get_job_summary_for_train(
                train_id
            ),
        }


# ============================================================
# GLOBAL SINGLETON
# ============================================================

job_card_manager = KMRLJobCardManager()
