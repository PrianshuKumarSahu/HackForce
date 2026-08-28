"""
Kochi Metro Rail Limited (KMRL) Fitness Certificate Manager.
Handles mandatory department safety fitness certificates (Rolling Stock, Signalling, Telecom),
certificate expiration tracking, approach-to-expiry alerts, and overall service eligibility checks.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

DEPARTMENTS = ["Rolling Stock", "Signalling", "Telecom"]

class KMRLFitnessManager:
    def __init__(self):
        # Maps train_id -> department -> certificate dict
        self._fitness_records: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._init_default_certificates()

    def _init_default_certificates(self):
        now = datetime.now()
        for i in range(25):
            t_id = f"KM-{101 + i}"
            self._fitness_records[t_id] = {}
            
            # Default: Valid certificates expiring in 60-120 days
            for dept in DEPARTMENTS:
                issued = now - timedelta(days=30)
                expires = now + timedelta(days=60 + i * 2)
                
                self._fitness_records[t_id][dept] = {
                    "department": dept,
                    "status": "APPROVED",
                    "issued_at": issued.isoformat(),
                    "expires_at": expires.isoformat(),
                    "last_verified_at": now.isoformat(),
                    "source": "KMRL_SAFETY_BOARD"
                }

        # Preset specific test cases:
        # KM-104: Expired Signalling certificate
        km104_expired = now - timedelta(days=2)
        self._fitness_records["KM-104"]["Signalling"]["status"] = "APPROVED"
        self._fitness_records["KM-104"]["Signalling"]["expires_at"] = km104_expired.isoformat()

        # KM-105: Rolling Stock approaching expiry in 3 days
        km105_approaching = now + timedelta(days=3)
        self._fitness_records["KM-105"]["Rolling Stock"]["expires_at"] = km105_approaching.isoformat()

    def _normalize_dept(self, department: str) -> Optional[str]:
        dept_clean = department.strip().lower()
        for d in DEPARTMENTS:
            if d.lower() == dept_clean or d.lower().replace(" ", "") == dept_clean.replace(" ", ""):
                return d
        return None

    def evaluate_certificate(self, cert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates dynamic validity, days until expiry, and approaching-expiry flags.
        """
        now = datetime.now()
        expires_at_dt = datetime.fromisoformat(cert["expires_at"])
        
        is_expired = now >= expires_at_dt
        status = cert.get("status", "APPROVED").upper()
        
        is_valid_now = (status == "APPROVED") and (not is_expired)
        
        delta = expires_at_dt - now
        days_until_expiry = round(delta.total_seconds() / 86400.0, 1)
        approaching_expiry = is_valid_now and (days_until_expiry <= 7.0)

        return {
            "department": cert["department"],
            "status": "EXPIRED" if (status == "APPROVED" and is_expired) else status,
            "issued_at": cert["issued_at"],
            "expires_at": cert["expires_at"],
            "last_verified_at": cert["last_verified_at"],
            "source": cert["source"],
            "is_valid_now": is_valid_now,
            "days_until_expiry": days_until_expiry,
            "approaching_expiry": approaching_expiry
        }

    def get_train_fitness(self, train_id: str) -> Optional[Dict[str, Any]]:
        train_id_upper = train_id.upper()
        if train_id_upper not in self._fitness_records:
            return None

        dept_certs = self._fitness_records[train_id_upper]
        evaluated_depts = []
        all_valid = True
        has_approaching = False
        reasons = []

        for dept in DEPARTMENTS:
            cert = dept_certs.get(dept)
            if not cert:
                all_valid = False
                evaluated_depts.append({
                    "department": dept,
                    "status": "MISSING",
                    "issued_at": None,
                    "expires_at": None,
                    "last_verified_at": None,
                    "source": "UNKNOWN",
                    "is_valid_now": False,
                    "days_until_expiry": 0.0,
                    "approaching_expiry": False
                })
                reasons.append(f"Missing mandatory fitness certificate for department '{dept}'.")
            else:
                eval_cert = self.evaluate_certificate(cert)
                evaluated_depts.append(eval_cert)
                if not eval_cert["is_valid_now"]:
                    all_valid = False
                    reasons.append(f"Department '{dept}' certificate is {eval_cert['status']} (Expired at {eval_cert['expires_at']}).")
                elif eval_cert["approaching_expiry"]:
                    has_approaching = True
                    reasons.append(f"Department '{dept}' certificate approaching expiry in {eval_cert['days_until_expiry']} days.")

        overall_status = "FIT_FOR_SERVICE" if all_valid else "UNFIT_SAFETY_CERTIFICATE_EXPIRED"
        
        return {
            "train_id": train_id_upper,
            "overall_fitness_status": overall_status,
            "is_fit_for_service": all_valid,
            "has_approaching_expiry": has_approaching,
            "evaluation_reasons": reasons if reasons else ["All mandatory department fitness certificates (Rolling Stock, Signalling, Telecom) are valid."],
            "department_certificates": evaluated_depts
        }

    def get_department_fitness(self, train_id: str, department: str) -> Optional[Dict[str, Any]]:
        train_id_upper = train_id.upper()
        if train_id_upper not in self._fitness_records:
            return None

        dept_canonical = self._normalize_dept(department)
        if not dept_canonical:
            return None

        cert = self._fitness_records[train_id_upper].get(dept_canonical)
        if not cert:
            return {
                "department": dept_canonical,
                "status": "MISSING",
                "issued_at": None,
                "expires_at": None,
                "last_verified_at": None,
                "source": "UNKNOWN",
                "is_valid_now": False,
                "days_until_expiry": 0.0,
                "approaching_expiry": False
            }

        return self.evaluate_certificate(cert)

    def update_certificate(
        self,
        train_id: str,
        department: str,
        status: str = "APPROVED",
        days_valid: int = 60,
        source: str = "KMRL_SAFETY_BOARD"
    ) -> Optional[Dict[str, Any]]:
        train_id_upper = train_id.upper()
        dept_canonical = self._normalize_dept(department)
        if not dept_canonical:
            return None

        if train_id_upper not in self._fitness_records:
            self._fitness_records[train_id_upper] = {}

        now = datetime.now()
        expires = now + timedelta(days=days_valid)

        cert = {
            "department": dept_canonical,
            "status": status.upper(),
            "issued_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "last_verified_at": now.isoformat(),
            "source": source
        }
        self._fitness_records[train_id_upper][dept_canonical] = cert
        return self.evaluate_certificate(cert)

# Global Fitness Manager Singleton
fitness_manager = KMRLFitnessManager()
