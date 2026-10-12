"""Payouts: pay what a deal owes. Only runs after the captain approves the payment in the dashboard.

Provider seam: an adapter has `name`, send(payment_id, amount_usd, details) -> provider_ref and
status(provider_ref) -> 'pending' | 'paid' | 'failed'. Both must be idempotent per payment id.
  manual  nothing is sent; the dashboard shows who to pay and the captain marks it paid
  paypal  PayPal Payouts API (business account with Payouts enabled); PAYPAL_CLIENT_ID/SECRET, PAYPAL_ENV
  wise    Wise API with a personal token (US business accounts can fund by API); WISE_TOKEN, WISE_ENV
Pick one with CREATORS_PAYOUTS (default manual).
"""
from __future__ import annotations

import os
import sqlite3
import uuid

import requests

from .db import event, now


class PayoutError(RuntimeError):
    pass


class Manual:
    name = "manual"

    def send(self, payment_id, amount_usd, details):
        return "manual"

    def status(self, ref):
        return "pending"


class PayPal:
    """https://developer.paypal.com/docs/api/payments.payouts-batch/v1/"""
    name = "paypal"

    def __init__(self, client_id=None, secret=None, env=None, http=None):
        self.id = client_id or os.environ.get("PAYPAL_CLIENT_ID")
        self.secret = secret or os.environ.get("PAYPAL_CLIENT_SECRET")
        live = (env or os.environ.get("PAYPAL_ENV", "sandbox")) == "live"
        self.base = "https://api-m.paypal.com" if live else "https://api-m.sandbox.paypal.com"
        self.http = http or requests.Session()

    def _token(self):
        if not (self.id and self.secret):
            raise PayoutError("PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET missing")
        r = self.http.post(f"{self.base}/v1/oauth2/token", auth=(self.id, self.secret),
                           data={"grant_type": "client_credentials"}, timeout=30)
        if r.status_code != 200:
            raise PayoutError(f"paypal auth HTTP {r.status_code}: {r.text[:200]}")
        return r.json()["access_token"]

    def send(self, payment_id, amount_usd, details):
        if details["method"] != "paypal":
            raise PayoutError(f"creator chose {details['method']}, not paypal")
        body = {"sender_batch_header": {"sender_batch_id": f"excerlock-payment-{payment_id}",  # PayPal rejects repeats
                                        "email_subject": "ExcerLock creator payment",
                                        "email_message": "Thanks for your videos!"},
                "items": [{"recipient_type": "EMAIL", "receiver": details["address"], "note": f"ExcerLock payment {payment_id}",
                           "sender_item_id": str(payment_id),
                           "amount": {"value": f"{amount_usd:.2f}", "currency": "USD"}}]}
        r = self.http.post(f"{self.base}/v1/payments/payouts", json=body, timeout=30,
                           headers={"Authorization": f"Bearer {self._token()}"})
        if r.status_code not in (200, 201):
            raise PayoutError(f"paypal payout HTTP {r.status_code}: {r.text[:300]}")
        return r.json()["batch_header"]["payout_batch_id"]

    def status(self, ref):
        r = self.http.get(f"{self.base}/v1/payments/payouts/{ref}", timeout=30,
                          headers={"Authorization": f"Bearer {self._token()}"})
        if r.status_code != 200:
            raise PayoutError(f"paypal status HTTP {r.status_code}")
        items = r.json().get("items") or []
        st = (items[0].get("transaction_status") if items else r.json()["batch_header"]["batch_status"]) or ""
        return {"SUCCESS": "paid", "FAILED": "failed", "RETURNED": "failed", "BLOCKED": "failed", "REFUNDED": "failed",
                "DENIED": "failed", "CANCELED": "failed"}.get(st.upper(), "pending")


class Wise:
    """https://docs.wise.com/api-docs: quote -> recipient -> transfer -> fund from USD balance."""
    name = "wise"

    def __init__(self, token=None, env=None, http=None):
        self.token = token or os.environ.get("WISE_TOKEN")
        live = (env or os.environ.get("WISE_ENV", "sandbox")) == "live"
        self.base = "https://api.wise.com" if live else "https://api.sandbox.transferwise.tech"
        self.http = http or requests.Session()

    def _call(self, method, path, **kw):
        if not self.token:
            raise PayoutError("WISE_TOKEN missing")
        r = self.http.request(method, self.base + path, timeout=30, headers={"Authorization": f"Bearer {self.token}"}, **kw)
        if r.status_code >= 300:
            raise PayoutError(f"wise {path} HTTP {r.status_code}: {r.text[:300]}")
        return r.json()

    def send(self, payment_id, amount_usd, details):
        if details["method"] != "wise":
            raise PayoutError(f"creator chose {details['method']}, not wise")
        profile = next(p["id"] for p in self._call("GET", "/v2/profiles") if p["type"].upper() == "BUSINESS")
        quote = self._call("POST", f"/v3/profiles/{profile}/quotes", json={
            "sourceCurrency": "USD", "targetCurrency": "USD", "targetAmount": amount_usd, "payOut": "BALANCE"})
        recipient = self._call("POST", "/v1/accounts", json={
            "profile": profile, "accountHolderName": details.get("legal_name") or details["address"],
            "currency": "USD", "type": "email", "details": {"email": details["address"]}})
        transfer = self._call("POST", "/v1/transfers", json={
            "targetAccount": recipient["id"], "quoteUuid": quote["id"],
            "customerTransactionId": str(uuid.uuid5(uuid.NAMESPACE_URL, f"excerlock-payment-{payment_id}")),
            "details": {"reference": f"ExcerLock {payment_id}"}})
        self._call("POST", f"/v3/profiles/{profile}/transfers/{transfer['id']}/payments", json={"type": "BALANCE"})
        return str(transfer["id"])

    def status(self, ref):
        st = self._call("GET", f"/v1/transfers/{ref}")["status"]
        return "paid" if st == "outgoing_payment_sent" else "failed" if st in ("cancelled", "funds_refunded", "bounced_back") else "pending"


def provider():
    return {"manual": Manual, "paypal": PayPal, "wise": Wise}[os.environ.get("CREATORS_PAYOUTS", "manual")]()


def approve(conn: sqlite3.Connection, payment_id: int, prov=None) -> str:
    """Captain approved: send through the provider if the creator gave payout details. Returns the new status."""
    prov = prov or provider()
    p = conn.execute("SELECT py.*, d.person_id FROM payments py JOIN deals d ON d.id=py.deal_id WHERE py.id=?",
                     (payment_id,)).fetchone()
    if p["status"] != "owed":
        return p["status"]
    details = conn.execute("SELECT * FROM payout_details WHERE person_id=?", (p["person_id"],)).fetchone()
    if prov.name != "manual" and not details:
        raise PayoutError("creator hasn't added payout details in their portal yet")
    try:
        ref = prov.send(payment_id, p["amount_usd"], dict(details) if details else {})
    except PayoutError as e:
        conn.execute("UPDATE payments SET error=? WHERE id=?", (str(e)[:300], payment_id))
        conn.commit()
        raise
    status = "approved" if prov.name == "manual" else "sending"
    conn.execute("UPDATE payments SET status=?, provider=?, provider_ref=?, error=NULL WHERE id=?",
                 (status, prov.name, ref, payment_id))
    event(conn, "payout_" + status, p["person_id"], p["deal_id"], payment=payment_id, provider=prov.name, ref=ref)
    conn.commit()
    return status


def mark_paid(conn: sqlite3.Connection, payment_id: int) -> None:
    """Manual payouts: the captain paid outside the system."""
    conn.execute("UPDATE payments SET status='paid', paid_at=? WHERE id=? AND status='approved'", (now(), payment_id))
    conn.commit()


def check_sending(conn: sqlite3.Connection, prov=None) -> list[int]:
    """Jobs: ask the provider about every payment in flight; paid or failed ends it."""
    prov = prov or provider()
    done = []
    for p in conn.execute("SELECT * FROM payments WHERE status='sending' AND provider=?", (prov.name,)).fetchall():
        st = prov.status(p["provider_ref"])
        if st == "paid":
            conn.execute("UPDATE payments SET status='paid', paid_at=? WHERE id=?", (now(), p["id"]))
        elif st == "failed":
            conn.execute("UPDATE payments SET status='owed', error='provider reported failure' WHERE id=?", (p["id"],))
        if st != "pending":
            event(conn, "payout_" + st, deal_id=p["deal_id"], payment=p["id"])
            done.append(p["id"])
    conn.commit()
    return done
