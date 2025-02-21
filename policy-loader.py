import os
import json
import signal
import sys
from daemon.policy_daemon import PolicyDaemon
from types.policy import PolicyDefinition, PolicyCondition, RemediationAction
from dacite import from_dict

def load_policies(file_path: str) -> List[PolicyDefinition]:
    with open(file_path, 'r') as f:
        data = json.load(f)
        return [from_dict(data_class=PolicyDefinition, data=p) for p in data['policies']]

def main():
    subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
    if not subscription_id:
        raise ValueError('AZURE_SUBSCRIPTION_ID environment variable is required')

    policies = load_policies('./policies/sample-policies.json')
    daemon = PolicyDaemon(subscription_id, policies)

    def handle_shutdown(signum, frame):
        print("Shutting down...")
        daemon.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    try:
        daemon.start()
        # Keep the main thread alive
        while True:
            signal.pause()
    except Exception as e:
        print(f"Error: {e}")
        daemon.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
