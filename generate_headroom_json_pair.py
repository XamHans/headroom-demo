#!/usr/bin/env python3
"""Generate two JSON files for the Headroom video.

Goal:
- one JSON shows the raw incident payloads
- one JSON shows the Headroom-compressed payloads

This is meant to be obvious on screen during the recording:
- lots of repeated logs in the raw file
- much smaller, cleaner output in the Headroom file
- clear lists of what got filtered out

Run:
    cd /Volumes/PortableSSD/headroom_video
    uv run --env-file .env generate_headroom_json_pair.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from statistics import mean

import tiktoken
from headroom import compress

ROOT = Path("/Volumes/PortableSSD/headroom_video")
RAW_OUTPUT = ROOT / "headroom_demo_raw.json"
OPT_OUTPUT = ROOT / "headroom_demo_headroom.json"
MODEL = os.getenv("DEMO_MODEL", "gpt-4o")


def make_cases():
    incident_logs = "\n".join(
        [
            f"2026-06-23 10:14:{i:02d} payment-service ERROR checkout_id=chk_{1000+i} "
            f"provider=stripe status=502 retry={i%3} message=upstream timeout from payments-api"
            for i in range(120)
        ]
    )

    support_tickets = json.dumps(
        [
            {
                "ticket_id": f"CS-{2000 + i}",
                "customer_tier": "pro" if i % 4 else "enterprise",
                "channel": "email" if i % 2 else "chat",
                "issue_type": "payment_failed",
                "country": ["DE", "AT", "CH", "NL"][i % 4],
                "status": "waiting_for_retry",
                "message": "I tried to pay and got an error. Please check my invoice.",
            }
            for i in range(180)
        ],
        indent=2,
    )

    root_cause_notes = "\n".join(
        [
            "Incident summary: Stripe returned intermittent 502s on the payment authorization endpoint.",
            "Impact: checkout success rate dropped from 98.7% to 81.4% for 17 minutes.",
            "Timeline:",
            "- 10:12 UTC: first spike in failed payment attempts",
            "- 10:14 UTC: customer support started receiving duplicate complaints",
            "- 10:15 UTC: retries increased load on the upstream payments API",
            "- 10:19 UTC: fallback route engaged, incident stabilized",
            "Hypothesis: upstream network issue caused transient failures, not a code regression.",
            "Next step: correlate with provider status page and retry policy metrics.",
            "Open questions: was the failure regional, and did idempotency affect retries?",
        ]
    )

    return {
        "incident_logs": {
            "content": incident_logs,
            "filtered_out": [
                "117 duplicate checkout timeout log lines",
                "repeated provider/status/retry fields across the same failure pattern",
                "boilerplate upstream timeout wording repeated over and over",
            ],
        },
        "support_tickets": {
            "content": support_tickets,
            "filtered_out": [
                "180 nearly identical customer complaints",
                "repeated invoice / payment-failed boilerplate",
                "repeated JSON structure that does not add new signal",
            ],
        },
        "root_cause_notes": {
            "content": root_cause_notes,
            "filtered_out": [
                "nothing important — this is already high-signal incident context",
            ],
        },
    }


def messages_for(content: str):
    return [
        {
            "role": "user",
            "content": "Analyze this incident material and summarize what matters for the on-call response.",
        },
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "collect_incident_data", "arguments": "{}"},
                }
            ],
        },
        {"role": "tool", "tool_call_id": "call_1", "content": content},
    ]


def token_count(model: str, messages) -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception:
        encoding = tiktoken.get_encoding("o200k_base")
    serialized = json.dumps(messages, ensure_ascii=False, sort_keys=True)
    return len(encoding.encode(serialized))


def compact_preview(text: str, limit: int = 260) -> str:
    text = text.replace("\n", " ").strip()
    return text[:limit] + ("…" if len(text) > limit else "")


def main() -> None:
    raw_cases = {}
    headroom_cases = {}
    savings = []

    for name, payload in make_cases().items():
        content = payload["content"]
        messages = messages_for(content)
        before = token_count(MODEL, messages)

        result = compress(
            messages,
            model=MODEL,
            compress_user_messages=True,
            protect_recent=0,
            target_ratio=0.3,
            min_tokens_to_compress=0,
        )
        after = token_count(MODEL, result.messages)
        saved = before - after
        ratio = (saved / before) if before else 0.0
        savings.append(ratio)

        raw_cases[name] = {
            "tokens": before,
            "content": content,
            "preview": compact_preview(content),
            "signal_removed": payload["filtered_out"],
        }

        headroom_cases[name] = {
            "tokens_before": before,
            "tokens_after": after,
            "tokens_saved": saved,
            "ratio": round(ratio, 4),
            "compressed_content": result.messages[-1].get("content", ""),
            "preview": compact_preview(str(result.messages[-1].get("content", ""))),
            "transforms": result.transforms_applied,
            "signal_removed": payload["filtered_out"],
        }

    raw_doc = {
        "title": "Headroom video demo — raw payload",
        "model": MODEL,
        "cases": raw_cases,
    }
    headroom_doc = {
        "title": "Headroom video demo — compressed payload",
        "model": MODEL,
        "summary": {
            "average_savings_ratio": round(mean(savings), 4) if savings else 0.0,
        },
        "cases": headroom_cases,
    }

    RAW_OUTPUT.write_text(json.dumps(raw_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    OPT_OUTPUT.write_text(json.dumps(headroom_doc, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {RAW_OUTPUT}")
    print(f"Wrote {OPT_OUTPUT}")
    print(f"Cases: {len(raw_cases)}")
    print(f"Model: {MODEL}")


if __name__ == "__main__":
    main()
