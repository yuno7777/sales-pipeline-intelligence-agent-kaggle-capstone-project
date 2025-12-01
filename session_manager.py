import time
from typing import Dict, Any, Optional, List
from utils import logger

class InMemorySessionService:
    """
    A simple in-memory session management service.
    Stores session state in a dictionary.
    """

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, session_id: str) -> Dict[str, Any]:
        """
        Creates a new session with the given session_id.
        If the session already exists, it is overwritten (or could raise an error).
        Here we overwrite for simplicity, but logging a warning.
        """
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists. Overwriting.")

        now = time.time()
        session_data = {
            "session_id": session_id,
            "created_at": now,
            "updated_at": now,
            "state": {}
        }
        self.sessions[session_id] = session_data
        logger.info(f"Created session: {session_id}")
        return session_data

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a session by ID. Returns None if not found.
        """
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, new_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates the state of an existing session.
        Merges new_state into the existing state.
        Updates 'updated_at'.
        Returns the updated session data, or None if session not found.
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Attempted to update non-existent session: {session_id}")
            return None

        # Merge state
        session["state"].update(new_state)
        session["updated_at"] = time.time()
        
        logger.info(f"Updated session: {session_id}")
        return session

    def delete_session(self, session_id: str) -> bool:
        """
        Deletes a session. Returns True if deleted, False if not found.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        Returns a list of all active sessions.
        """
        return list(self.sessions.values())
