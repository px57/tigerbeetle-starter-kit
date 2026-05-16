




# TigerBeetle Imports
from tigerbeetle.client import Client
from tigerbeetle import ClientSync
import tigerbeetle as tb

client = Client(
    cluster_id=0,
    replica_addresses="10.0.0.1:3000"
)


# Create account with multiple wallet types
def create_account():
    with tb.ClientSync(cluster_id=0, replica_addresses="10.0.0.130:3000") as client:
        account = tb.Account(
            id=tb.id(), # TigerBeetle time-based ID.
            debits_pending=0,
            debits_posted=0,
            credits_pending=0,
            credits_posted=0,
            user_data_128=0,
            user_data_64=0,
            user_data_32=0,
            ledger=1,
            code=718,
            flags=0,
            timestamp=0,
        )

        account_errors = client.create_accounts([account])

account = create_account()
account2 = create_account()