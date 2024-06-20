
import braintree

from core import settings


if settings.BT_ENVIRONMENT == "sandbox":
    bt_env = braintree.Environment.Sandbox
else:
    bt_env = braintree.Environment.Production


gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment=bt_env,
        merchant_id=settings.BT_MERCHANT_ID,
        public_key=settings.BT_PUBLIC_KEY,
        private_key=settings.BT_PRIVATE_KEY
    )
)


def generate_client_token(customer_id):
    return gateway.client_token.generate({
        "customer_id": customer_id
    })


def transact(options):
    return gateway.transaction.sale(options)


def find_transaction(transaction_id):
    return gateway.transaction.find(transaction_id)


'''
Manages the creation of a Braintree user account
'''


def create_account(email):
    response = gateway.customer.create({"email": email})
    if not response.is_success:
        return None
    return response.customer.id


'''
Manage payments
'''


def make_payments(**kwargs):
    agent_id = kwargs.get("agent_id")
    token = kwargs.get("token")
    amount = kwargs.get("amount")
    card_id = kwargs.get("card_id")
    description = kwargs.get("description")
    currency = kwargs.get("currency")
    set_default = kwargs.get("set_default")

    gateway.payment_method.create(
        {
            "customer_id": agent_id,
            "payment_method_nonce": token,
            "options": {
                "make_default": True,
                "verify_card": True,
                "fail_on_duplicate_payment_method": True
            }
        }
    )

    result = transact({
        'amount': amount,
        'customer_id': agent_id,
        'options': {
            "submit_for_settlement": True
        }
    })

    if result.is_success or result.transaction:
        return {
            "message": "Paid",
            "tran_id": result.transaction.id
        }
    else:
        return {
            "message": ", ".join([f'{x.code} - {x.message}' for x in result.errors.deep_errors]),
            "tran_id": "N/A"
        }


class Payment:

    def __init__(self, *args, **kwargs):
        self.agent_id = kwargs.get("agent_id")
        self.token = kwargs.get("token")
        self.amount = kwargs.get("amount")
        self.card_id = kwargs.get("card_id")
        self.description = kwargs.get("description")
        self.currency = kwargs.get("currency")
        self.set_default = kwargs.get("set_default")

    def create(self):

        gateway.payment_method.create(
            {
                "customer_id": self.agent_id,
                "payment_method_nonce": self.token,
                "options": {
                    "make_default": True,
                    "verify_card": True,
                    "fail_on_duplicate_payment_method": True
                }
            }
        )

        result = transact({
            'amount': self.amount,
            'customer_id': self.agent_id,
            'options': {
                "submit_for_settlement": True
            }
        })

        if result.is_success or result.transaction:
            return {
                "message": "Paid",
                "tran_id": result.transaction.id
            }
        else:
            return {
                "message": ", ".join([f'{x.code} - {x.message}' for x in result.errors.deep_errors]),
                "tran_id": "N/A"
            }


def get_transaction(transaction_id):
    result = gateway.transaction.search(
        braintree.TransactionSearch.id == transaction_id
    )

    return [
        {
            "id": inv.id,
            "purchase_date": inv.created_at.strftime('%d-%m-%Y'),
            "amount": str(inv.amount)
        }
        for inv in result.items
    ]


class BraintreeData:

    def __init__(self, user):
        self.user = user

    def invoices(self):
        agent_id = self.user.userprofile.agent_id

        # try:

        # Query user invoices
        invoices = gateway.transaction.search(
            braintree.TransactionSearch.customer_id == agent_id
        )

        invoice_list = [
            [
                inv.id,
                inv.created_at.strftime('%d-%m-%Y'),
                inv.amount,
            ]
            for inv in invoices.items]

        if not invoice_list:
            return None
        return invoice_list
    # except:
    # 	return None
