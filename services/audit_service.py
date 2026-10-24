"""
Audit service for logging all mutating actions in APAAR Nexus.
Ensures accountability, transparency, and non-repudiation.
"""
from typing import Optional, Any, Dict
import logging
from flask import current_app

logger = logging.getLogger("audit")


def log(
    actor: str,
    action: str,
    entity_type: str,
    entity_id: str,
    details: Optional[Dict[str, Any]] = None,
    institution_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log an audit event.

    Args:
        actor: Username or system actor performing the action.
        action: Specific action performed (e.g. ADMISSION_ACCEPTED, CREDENTIAL_ISSUED).
        entity_type: Target entity type (e.g. STUDENT, CREDENTIAL, RISK_CASE).
        entity_id: Primary identifier of the affected entity.
        details: Optional dictionary containing event details and context.
        institution_id: Optional UUID of the scoped institution.

    Returns:
        Dict containing recorded audit event payload.
    """
    details = details or {}
    record = {
        "actor": actor,
        "action": action,
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "institution_id": str(institution_id) if institution_id else None,
        "details": details,
    }

    # Log to application logger; will be persisted to AuditLog model once DB models land in A1
    if current_app:
        current_app.logger.info(
            "AUDIT: actor=%s action=%s entity=%s:%s inst=%s details=%s",
            actor,
            action,
            entity_type,
            entity_id,
            institution_id,
            details,
        )
    else:
        logger.info("AUDIT: %s", record)

    return record
