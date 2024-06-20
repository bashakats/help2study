from django.shortcuts import render
import json
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from django.shortcuts import render
from django.http import HttpResponse
from pyfirebasehandler.firebase_handler import FirebaseHandler

from core import braintree_processor, settings

print("Firebase Key File Path: ", settings.KEY_FILE_PATH)
db = FirebaseHandler(settings.KEY_FILE_PATH)

fsdb = firestore.client()


# Create your views here.


def donate_to_page(request, donor_id, amount, student_id):
    # Firebase calls
    student = db.get_document("users", student_id)
    donor = db.get_document("users", donor_id)
    donations = (
        fsdb.collection("donations")
        .where(filter=FieldFilter("student_id", "==", student_id))
        .get()
    )
    amount_raised = sum([int(float(donation.to_dict().get("amount"))) for donation in donations]) if donations else 0
    customer_id = donor.get("agent_id", None)
    if not customer_id:
        customer_id = braintree_processor.create_account(donor["email"])
        db.update_document("users", donor_id, {"agent_id": customer_id})
    client_payment_token = braintree_processor.generate_client_token(customer_id)


    # Data formatting
    # Security stuff
    context = {
        "student": student,
        "donor": donor,
        "amount": amount,
        "amount_raised": amount_raised,
        "percent_raised": (amount_raised * 100) / 1000,
        "client_token": client_payment_token,
    }
    return render(request, "donateTo.html", context=context)


def complete_donation(request, donor_id, student_id):
    if request.method == "POST":
        donor = db.get_document("users", donor_id)

        token = request.POST.get("paymentNonce", None)
        card_id = request.POST.get("card_id", None)
        description = request.POST.get("description", None)
        currency = request.POST.get("currency", None)
        set_default = request.POST.get("set_default", None)
        amount = request.POST.get("amount")

        agent_id = donor.get("agent_id", None)
        if not agent_id:
            agent_id = braintree_processor.create_account(donor["email"])
            if not agent_id:
                return HttpResponse(
                    json.dumps(
                        {
                            "result": "error",
                            "message": "Something went wrong. Please try again",
                        }
                    ),
                    content_type="application/json",
                )
            db.update_document("users", donor_id, {"agent_id": agent_id})

        payment = braintree_processor.make_payments(
            agent_id=agent_id,
            token=token,
            card_id=card_id,
            amount=amount,
            description=description,
            currency=currency,
            set_default=set_default,
        )

        if payment["message"] == "Paid":
            transaction_id = payment["tran_id"]
            transaction_list = braintree_processor.get_transaction(transaction_id)
            if not transaction_list:
                return HttpResponse(
                    json.dumps(
                        {
                            "result": "error",
                            "message": "Could not find the transaction. Please try again",
                        }
                    ),
                    content_type="application/json",
                )
            transaction = transaction_list[0]
            donation = {
                "donor_id": donor_id,
                "student_id": student_id,
                "transaction_id": transaction.pop("id"),
            }
            donation.update(transaction)
            db.create_document("donations", donation)
            return HttpResponse(
                json.dumps({"result": "okay"}), content_type="application/json"
            )
        else:
            return HttpResponse(
                json.dumps({"result": "error", "message": payment["message"]}),
                content_type="application/json",
            )
    else:
        return HttpResponse(
            json.dumps(
                {"result": "error", "message": "No data found cant make transaction"}
            ),
            content_type="application/json",
        )
