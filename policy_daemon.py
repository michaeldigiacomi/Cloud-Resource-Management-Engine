import threading
import time
import asyncio
from typing import List
from policy_engine import PolicyEngine
from policy_types import PolicyDefinition

class PolicyDaemon:
    def __init__(self, subscription_id: str, policies: List[PolicyDefinition], cloud_provider: str = 'azure', management_group_id: str = None):
        self.policy_engine = PolicyEngine(subscription_id, cloud_provider, management_group_id)
        self.policies = policies
        self.threads: List[threading.Thread] = []
        self.running = False
        self.loop = asyncio.new_event_loop()

    async def _evaluate_policy(self, policy: PolicyDefinition):
        try:
            await self.policy_engine.evaluate_policy(policy)
        except Exception as e:
            print(f"Error evaluating policy {policy.id}: {e}")

    def _policy_loop(self, policy: PolicyDefinition):
        asyncio.set_event_loop(self.loop)
        while self.running:
            try:
                self.loop.run_until_complete(self._evaluate_policy(policy))
                time.sleep(policy.evaluation_frequency * 60)
            except Exception as e:
                print(f"Error in policy loop for {policy.id}: {e}")
                time.sleep(60)  # Wait before retry

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
