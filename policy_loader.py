import os
import json
import signal
import sys
import logging
from time import time
from pathlib import Path
from policy_daemon import PolicyDaemon
from policy_types import PolicyDefinition
from dacite import from_dict, Config
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def validate_policy_file(file_path: str) -> bool:
    """Validate that the policy file exists and is valid JSON"""
    try:
        if not Path(file_path).exists():
            logger.error(f"Policy file not found: {file_path}")
            return False
        with open(file_path, 'r') as f:
            json.load(f)
        logger.debug(f"Policy file validated successfully: {file_path}")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in policy file {file_path}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error validating policy file {file_path}: {str(e)}")
        return False

def load_policies(file_path: str) -> List[PolicyDefinition]:
    start_time = time()
    logger.info(f"Starting policy load from: {file_path}")
    
    if not validate_policy_file(file_path):
        raise ValueError(f"Invalid policy file: {file_path}")

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            logger.debug(f"Found {len(data.get('policies', []))} policies in file")
            
            policies = []
            for index, policy_data in enumerate(data.get('policies', []), 1):
                try:
                    logger.debug(f"Loading policy {index}: {policy_data.get('id', 'UNKNOWN')}")
                    policy = from_dict(
                        data_class=PolicyDefinition,
                        data=policy_data,
                        config=Config(check_types=True)
                    )
                    policies.append(policy)
                    logger.debug(f"Successfully loaded policy: {policy.id}")
                except Exception as e:
                    logger.error(f"Error loading policy {index}: {str(e)}")
                    logger.error(f"Policy data: {json.dumps(policy_data, indent=2)}")
                    raise

            load_time = time() - start_time
            logger.info(f"Successfully loaded {len(policies)} policies in {load_time:.2f} seconds")
            return policies

    except Exception as e:
        logger.error(f"Failed to load policies from {file_path}: {str(e)}")
        raise

def main():
    logger.info("Starting policy engine")
    
    subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
    if not subscription_id:
        logger.error("AZURE_SUBSCRIPTION_ID environment variable is required")
        raise ValueError('AZURE_SUBSCRIPTION_ID environment variable is required')

    management_group_id = os.environ.get('AZURE_MANAGEMENT_GROUP_ID')
    policy_file = os.environ.get('POLICY_CONFIG', './policies/sample-policies.json')
    
    logger.info(f"Loading policies from: {policy_file}")
    policies = load_policies(policy_file)
    logger.info(f"Initializing daemon with {len(policies)} policies")
    
    daemon = PolicyDaemon(subscription_id, policies, management_group_id)

    def handle_shutdown(signum, frame):
        logger.info("Received shutdown signal")
        daemon.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    try:
        logger.info("Starting policy daemon")
        daemon.start()
        while True:
            signal.pause()
    except Exception as e:
        logger.error(f"Fatal error in main loop: {str(e)}")
        daemon.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
