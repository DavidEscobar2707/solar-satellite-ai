import os
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def load_env_file(env_path: Optional[str] = None) -> Dict[str, str]:
    """Load environment variables from .env file."""
    if env_path is None:
        # Try to find .env in the current directory or parent directories
        current = Path.cwd()
        while current != current.parent:
            env_file = current / ".env"
            if env_file.exists():
                env_path = str(env_file)
                break
            current = current.parent
    
    if not env_path or not Path(env_path).exists():
        logger.warning("No .env file found")
        return {}
    
    env_vars = {}
    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
                # Also set in environment
                os.environ[key.strip()] = value.strip()
        if env_vars:
            logger.info(f"Loaded environment variables from {env_path}")
    except Exception as e:
        logger.error(f"Error loading .env file: {e}")
    
    return env_vars
