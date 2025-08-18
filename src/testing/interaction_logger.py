"""
Interaction Logger for Automated Testing.

Logs all user-agent interactions with detailed metadata for analysis and reporting.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class InteractionLogger:
    """Logs and manages all test interactions with detailed metadata."""
    
    def __init__(self, logs_dir: str = "testing/logs"):
        """Initialize interaction logger."""
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.interactions: List[Dict] = []
        self.session_metadata: Dict = {}
    
    def start_session(
        self,
        session_id: str,
        test_type: str,
        business_case: str,
        persona: Dict
    ) -> None:
        """Start a new testing session."""
        self.session_metadata = {
            "session_id": session_id,
            "test_type": test_type,
            "business_case": business_case,
            "persona": persona,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_interactions": 0,
            "phases_tested": [],
            "test_status": "IN_PROGRESS"
        }
        
        logger.info(f"📝 Started logging session: {session_id}")
    
    def log_interaction(
        self,
        interaction_id: int,
        user_message: str,
        agent_response: str,
        phase: str,
        methodology_stage: str = "",
        response_time_ms: int = 0,
        screenshot_path: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Log a single user-agent interaction."""
        
        interaction_data = {
            "interaction_id": interaction_id,
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "methodology_stage": methodology_stage,
            "user_message": user_message,
            "agent_response": agent_response,
            "response_time_ms": response_time_ms,
            "screenshot_path": screenshot_path,
            "metadata": metadata or {},
            "message_lengths": {
                "user": len(user_message),
                "agent": len(agent_response)
            }
        }
        
        self.interactions.append(interaction_data)
        self.session_metadata["total_interactions"] = len(self.interactions)
        
        logger.debug(f"💬 Logged interaction {interaction_id} in {phase} phase")
    
    def log_phase_transition(
        self,
        from_phase: str,
        to_phase: str,
        interaction_id: int,
        transition_trigger: str = ""
    ) -> None:
        """Log a phase transition event."""
        
        transition_data = {
            "type": "PHASE_TRANSITION",
            "interaction_id": interaction_id,
            "timestamp": datetime.now().isoformat(),
            "from_phase": from_phase,
            "to_phase": to_phase,
            "transition_trigger": transition_trigger
        }
        
        self.interactions.append(transition_data)
        
        # Update phases tested
        if to_phase not in self.session_metadata.get("phases_tested", []):
            self.session_metadata["phases_tested"].append(to_phase)
        
        logger.info(f"🔄 Phase transition: {from_phase} → {to_phase}")
    
    def log_error(
        self,
        interaction_id: int,
        error_type: str,
        error_message: str,
        phase: str,
        context: Optional[Dict] = None
    ) -> None:
        """Log an error that occurred during testing."""
        
        error_data = {
            "type": "ERROR",
            "interaction_id": interaction_id,
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }
        
        self.interactions.append(error_data)
        logger.error(f"❌ Error logged in {phase} phase: {error_message}")
    
    def end_session(self, test_status: str = "COMPLETED") -> None:
        """End the testing session."""
        self.session_metadata["end_time"] = datetime.now().isoformat()
        self.session_metadata["test_status"] = test_status
        
        # Calculate session duration
        start_time = datetime.fromisoformat(self.session_metadata["start_time"])
        end_time = datetime.fromisoformat(self.session_metadata["end_time"])
        duration = (end_time - start_time).total_seconds()
        
        self.session_metadata["duration_seconds"] = duration
        self.session_metadata["duration_minutes"] = duration / 60
        
        logger.info(f"⏱️ Session ended: {duration:.1f}s, Status: {test_status}")
    
    async def save_log(self, filename: Optional[str] = None) -> str:
        """Save the complete interaction log to JSON file."""
        if not filename:
            session_id = self.session_metadata.get("session_id", "unknown")
            filename = f"{session_id}_interactions.json"
        
        log_path = self.logs_dir / filename
        
        # Compile complete log data
        log_data = {
            "session_metadata": self.session_metadata,
            "interactions": self.interactions,
            "statistics": self._calculate_statistics(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Save to JSON file
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Interaction log saved: {log_path}")
        return str(log_path)
    
    def _calculate_statistics(self) -> Dict:
        """Calculate interaction statistics for reporting."""
        if not self.interactions:
            return {}
        
        # Filter out non-interaction events
        message_interactions = [
            i for i in self.interactions 
            if i.get("type") != "PHASE_TRANSITION" and i.get("type") != "ERROR"
        ]
        
        if not message_interactions:
            return {}
        
        response_times = [i.get("response_time_ms", 0) for i in message_interactions]
        user_message_lengths = [i.get("message_lengths", {}).get("user", 0) for i in message_interactions]
        agent_message_lengths = [i.get("message_lengths", {}).get("agent", 0) for i in message_interactions]
        
        return {
            "total_interactions": len(message_interactions),
            "average_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "average_user_message_length": sum(user_message_lengths) / len(user_message_lengths) if user_message_lengths else 0,
            "average_agent_message_length": sum(agent_message_lengths) / len(agent_message_lengths) if agent_message_lengths else 0,
            "phase_distribution": self._calculate_phase_distribution(),
            "error_count": len([i for i in self.interactions if i.get("type") == "ERROR"]),
            "transition_count": len([i for i in self.interactions if i.get("type") == "PHASE_TRANSITION"])
        }
    
    def _calculate_phase_distribution(self) -> Dict:
        """Calculate interaction distribution across phases."""
        phase_counts = {}
        
        for interaction in self.interactions:
            phase = interaction.get("phase")
            if phase:
                phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        return phase_counts
    
    def get_interactions_for_phase(self, phase: str) -> List[Dict]:
        """Get all interactions for a specific phase."""
        return [
            i for i in self.interactions 
            if i.get("phase") == phase and i.get("type") != "PHASE_TRANSITION"
        ]
    
    def get_session_summary(self) -> Dict:
        """Get a summary of the current session."""
        return {
            "session_id": self.session_metadata.get("session_id"),
            "test_type": self.session_metadata.get("test_type"),
            "status": self.session_metadata.get("test_status"),
            "total_interactions": len(self.interactions),
            "phases_tested": self.session_metadata.get("phases_tested", []),
            "duration_minutes": self.session_metadata.get("duration_minutes", 0)
        }