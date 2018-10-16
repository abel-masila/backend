import os
import requests
import requests_toolbelt.adapters.appengine

from requests.auth import HTTPBasicAuth
from flask import Blueprint

from ..models.mpesa import MpesaCredentials


requests_toolbelt.adapters.appengine.monkeypatch()
mpesa_push_api = Blueprint('mpesa_push_api', __name__)


# @mpesa_push_api.route('/payments/mpesa/paybill', methods=['GET', 'POST'])
def get_or_update_mpesa_access_token():
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    credentials = HTTPBasicAuth(
        os.environ.get("MPESA_API_CONSUMER_KEY"), 
        os.environ.get("MPESA_API_CONSUMER_SECRET")
    )
    response = requests.get(api_url, auth=credentials)
    # {
	#     "access_token": "hsHoclSD53UC3657NAD3d0qBE8cA",
	#     "expires_in": "3599"
    # }
    mpesa_credentials = MpesaCredentials(**response.json())
    mpesa_credentials.put()


@mpesa_push_api.route('/payments/mpesa/paybill/register_webhooks', methods=['POST'])
def register_webhook_urls_with_mpesa():
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    access_token = "Access-Token"
    headers = {
        "Host": "sandbox.safaricom.co.ke",
        "Content-Type": "application/json",
        "Authorization": "Bearer {access_token}".format(access_token=access_token)
    }
    data = {
	    "ShortCode": os.environ.get("MPESA_API_PAYBILL_NUMBER"),
	    "ResponseType": "[Cancelled/Completed]",
	    "ConfirmationURL": "[confirmation URL]",
	    "ValidationURL": "[validation URL]"
    }
    response = requests.post(api_url, json=data, headers=headers)
    print (response.text)


@mpesa_push_api.route('/payments/mpesa/paybill/payment/request', methods=['POST'])
def simulate_payment_via_mpesa_stk_push():
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate"
    access_token = "Access-Token"
    headers = {
        "Host": "sandbox.safaricom.co.ke",
        "Content-Type": "application/json",
        "Authorization": "Bearer {access_token}".format(access_token=access_token)
    }
    data = {
        "ShortCode": "601426",
        "CommandID": "CustomerPayBillOnline",
        "Amount": "100",
        "Msisdn": "254708374149",
        "BillRefNumber": "account"
    }
    response = requests.post(api_url, json=data, headers=headers)
    print (response.text)


@mpesa_push_api.route('/payments/mpesa/paybill/paybill', methods=['POST'])
def request_payment_via_mpesa_stk_push():
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    access_token = "Access-Token"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {access_token}".format(access_token=access_token)
    }
    data = {
        "BusinessShortCode": "BusinessShortCode",
        "Password": "The password for encrypting the request. This is generated by base64 encoding BusinessShortcode, Passkey and Timestamp",
        "Timestamp": "The timestamp of the transaction in the format yyyymmddhhiiss",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": "0",
        "PartyA": "The MSISDN sending the funds.",
        "PartyB": "BusinessShortCode",
        "PhoneNumber": "The MSISDN sending the funds.",
        "CallBackURL": "The url to where responses from M-Pesa will be sent to.",
        "AccountReference": "The ID of the ORDER being paid for",
        "TransactionDesc": "A description of the transaction."
    }
    response = requests.post(api_url, json=data, headers=headers)
    print (response.text)


# Callback response of a successful payment
# {
# 	"Body": 
# 	{
# 		"stkCallback": 
# 		{
# 			"MerchantRequestID": "21605-295434-4",
# 			"CheckoutRequestID": "ws_CO_04112017184930742",
# 			"ResultCode": 0,
# 			"ResultDesc": "The service request is processed successfully.",
# 			"CallbackMetadata": 
# 			{
# 				"Item": 
# 				[
# 					{
# 						"Name": "Amount",
# 						"Value": 1
# 					},
# 					{
# 						"Name": "MpesaReceiptNumber",
# 						"Value": "LK451H35OP"
# 					},
# 					{
# 						"Name": "Balance"
# 					},
# 					{
# 						"Name": "TransactionDate",
# 						"Value": 20171104184944
# 					},
# 					{
# 						"Name": "PhoneNumber",
# 						"Value": 254727894083
# 					}
# 				]
# 			}
# 		}
# 	}
# }
