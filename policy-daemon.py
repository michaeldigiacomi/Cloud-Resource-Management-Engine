import threading
import time
from typing import List
from ..services.policy_engine import PolicyEngine
from ..types.policy import PolicyDefinition

class PolicyDaemon:
    def __init__(self, subscription_id: str, policies: List[PolicyDefinition], cloud_provider: str = 'azure'):
        self.policy_engine = PolicyEngine(subscription_id, cloud_provider)
        self.policies = policies
        self.threads: List[threading.Thread] = []
        self.running = False

    def _policy_loop(self, policy: PolicyDefinition):
        while self.running:
            asyncio.run(self.policy_engine.evaluate_policy(policy))
            time.sleep(policy.evaluation_frequency * 60)

    def start(self):
        self.running = True
        for policy in self.policies:
            thread = threading.Thread(
                target=self._policy_loop,
                args=(policy,),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)

    def stop(self):
        self.running = False
        for thread in self.threads:
            thread.join()
        self.threads.clear()
