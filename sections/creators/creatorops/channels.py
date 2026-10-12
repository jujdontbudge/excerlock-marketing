"""Message channel seam. A channel has `name` and send(to, subject, body) -> provider id; raises ChannelError.

email: Resend API. dm: nothing is sent; the message is marked ready for a human to paste into the app,
because automated TikTok/Instagram DMs get accounts flagged.
"""
from __future__ import annotations

import os

import requests


class ChannelError(RuntimeError):
    pass


class ResendEmail:
    name = "email"

    def __init__(self, api_key: str | None = None, sender: str | None = None):
        self.key = api_key or os.environ.get("RESEND_API_KEY")
        self.sender = sender or os.environ.get("CREATORS_FROM", "ExcerLock <onboarding@resend.dev>")
        self.reply_to = os.environ.get("CREATORS_REPLY_TO")

    def send(self, to: str, subject: str, body: str) -> str:
        if not self.key:
            raise ChannelError("RESEND_API_KEY missing")
        r = requests.post("https://api.resend.com/emails", timeout=30,
                          headers={"Authorization": f"Bearer {self.key}"},
                          json={"from": self.sender, "to": [to], "subject": subject, "text": body,
                                **({"reply_to": self.reply_to} if self.reply_to else {})})
        if r.status_code >= 300:
            raise ChannelError(f"resend HTTP {r.status_code}: {r.text[:200]}")
        return r.json()["id"]


class ManualDM:
    name = "dm"

    def send(self, to: str, subject: str, body: str) -> str:
        return "manual"


def default_channels() -> dict:
    return {"email": ResendEmail(), "dm": ManualDM()}
