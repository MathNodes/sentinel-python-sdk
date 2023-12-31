import random

from sentinel_sdk.sdk import SDKInstance
from sentinel_sdk.types import PageRequest, Status

# GRPC_VERBOSITY=debug GRPC_TRACE=tcp,http python test/queryall.py

# [Warning] Sometimes we get an empty data, init sdk and SDKInstance before each query
# Probably is goes in timeout or something like that

sdk = SDKInstance("grpc.sentinel.co", 9090)

nodes = sdk.multiquerier.node_querier.QueryNodes(
    Status.ACTIVE, pagination=PageRequest(limit=500)
)
print(f"{len(nodes)} nodes")
node_random = random.choice(nodes)
node_chain = sdk.multiquerier.node_querier.QueryNode(node_random.address)
assert node_chain == node_random
print(f"Random node: {node_chain}")

plans = sdk.multiquerier.plan_querier.QueryPlans(Status.ACTIVE)
print(f"{len(plans)} plans")
plan_random = random.choice(plans)
plan_chain = sdk.multiquerier.plan_querier.QueryPlan(plan_random.id)
assert plan_chain == plan_random
print(f"Random plan: {plan_chain}")

nodes_4plan = sdk.multiquerier.node_querier.QueryNodesForPlan(
    plan_random.id, Status.ACTIVE
)
print(f"{len(nodes_4plan)} nodes for plan: {plan_random.id}")

deposits = sdk.multiquerier.deposit_querier.QueryDeposits()
print(f"{len(deposits)} deposits")
deposit_random = random.choice(deposits)
deposit_chain = sdk.multiquerier.deposit_querier.QueryDeposit(deposit_random.address)
assert deposit_chain == deposit_random
print(f"Random deposit: {deposit_chain}")

providers = sdk.multiquerier.provider_querier.QueryProviders(Status.ACTIVE)
print(f"{len(providers)} providers")
provider_random = random.choice(providers)
provider_chain = sdk.multiquerier.provider_querier.QueryProvider(
    provider_random.address
)
assert provider_chain == provider_random
print(f"Random provider: {provider_chain}")

subscriptions = sdk.multiquerier.subscription_querier.QuerySubscriptions(
    pagination=PageRequest(limit=1500)
)
print(f"{len(subscriptions)} subscriptions")
subscription_random = random.choice(subscriptions)
subscription_chain = sdk.multiquerier.subscription_querier.QuerySubscription(
    subscription_random.base.id
)
assert subscription_chain == subscription_random
print(f"Random subscription: {subscription_chain}")

"""
# TODO: need investigation ...
allocations = sdk.multiquerier.subscription_querier.QueryAllocations(subscription_random.base.id)
print(f"{len(allocations)} allocations")
allocation_random = random.choice(allocations)
allocation_chain = sdk.multiquerier.subscription_querier.QueryAllocation(allocation_random.address, allocation_random.id)
assert allocation_chain == allocation_random
print(f"Random allocation: {allocation_chain}")
"""

payouts = sdk.multiquerier.subscription_querier.QueryPayouts()
print(f"{len(payouts)} payouts")
payout_random = random.choice(payouts)
payout_chain = sdk.multiquerier.subscription_querier.QueryPayout(payout_random.id)
assert payout_chain == payout_random
print(f"Random payout: {payout_chain}")

# TODO: not sure about this query
payouts = sdk.multiquerier.subscription_querier.QueryPayoutsForAccount(
    subscription_random.base.address
)
print(
    f"{len(payouts)} payouts, QueryPayoutsForAccount({subscription_random.base.address})"
)

payouts = sdk.multiquerier.subscription_querier.QueryPayoutsForNode(
    subscription_random.node_address
)
print(
    f"{len(payouts)} payouts, QueryPayoutsForNode({subscription_random.node_address})"
)

subscriptions = sdk.multiquerier.subscription_querier.QuerySubscriptionsForAccount(
    subscription_random.base.address
)
print(
    f"{len(payouts)} subscriptions, QuerySubscriptionsForAccount({subscription_random.base.address})"
)

subscriptions = sdk.multiquerier.subscription_querier.QuerySubscriptionsForNode(
    subscription_random.node_address
)
print(
    f"{len(payouts)} subscriptions, QuerySubscriptionsForNode({subscription_random.node_address})"
)

subscriptions = sdk.multiquerier.subscription_querier.QuerySubscriptionsForPlan(
    plan_random.id
)
print(f"{len(payouts)} subscriptions, QuerySubscriptionsForPlan({plan_random.id})")
