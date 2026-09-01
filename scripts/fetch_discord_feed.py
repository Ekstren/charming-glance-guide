#!/usr/bin/env python3
"""Mirror a dedicated Discord channel into a small JSON feed for timeline research.

Uses only Python's standard library. The Discord bot token is read from the
DISCORD_BOT_TOKEN environment variable and is never written to disk.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://discord.com/api/v10"
OUTPUT = Path(os.environ.get("DISCORD_FEED_OUTPUT", "data/sxs-official-discord-feed.json"))
TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID", "").strip()


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    if params:
        path = f"{path}?{urlencode(params)}"
    req = Request(
        f"{API}{path}",
        headers={
            "Authorization": f"Bot {TOKEN}",
            "User-Agent": "CharmingGlanceTimelineRelay/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 429:
            try:
                retry = float(json.loads(body).get("retry_after", 1))
            except Exception:
                retry = 1
            time.sleep(min(max(retry, 1), 30))
            return api_get(path.split("?", 1)[0], params)
        fail(f"Discord API returned HTTP {exc.code}: {body[:500]}")
    except URLError as exc:
        fail(f"Could not reach Discord API: {exc}")


def load_feed() -> dict[str, Any]:
    if not OUTPUT.exists():
        return {
            "schema_version": 1,
            "channel": {},
            "last_message_id": None,
            "messages": [],
        }
    try:
        return json.loads(OUTPUT.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Could not parse {OUTPUT}: {exc}")


def compact_embed(embed: dict[str, Any]) -> dict[str, Any]:
    keep = {}
    for key in ("type", "url", "title", "description", "timestamp", "color"):
        if embed.get(key) is not None:
            keep[key] = embed[key]
    if embed.get("author"):
        keep["author"] = {
            k: v for k, v in embed["author"].items() if k in {"name", "url", "icon_url"} and v is not None
        }
    if embed.get("fields"):
        keep["fields"] = [
            {k: v for k, v in field.items() if k in {"name", "value", "inline"} and v is not None}
            for field in embed["fields"]
        ]
    if embed.get("footer"):
        keep["footer"] = {
            k: v for k, v in embed["footer"].items() if k in {"text", "icon_url"} and v is not None
        }
    for media_key in ("image", "thumbnail", "video"):
        if embed.get(media_key):
            keep[media_key] = {
                k: v
                for k, v in embed[media_key].items()
                if k in {"url", "proxy_url", "width", "height"} and v is not None
            }
    return keep


def compact_message(msg: dict[str, Any], guild_id: str | None) -> dict[str, Any]:
    author = msg.get("author") or {}
    attachments = []
    for att in msg.get("attachments") or []:
        attachments.append(
            {
                k: att[k]
                for k in (
                    "id",
                    "filename",
                    "description",
                    "content_type",
                    "size",
                    "url",
                    "proxy_url",
                    "width",
                    "height",
                )
                if att.get(k) is not None
            }
        )

    out: dict[str, Any] = {
        "id": msg["id"],
        "timestamp": msg.get("timestamp"),
        "edited_timestamp": msg.get("edited_timestamp"),
        "type": msg.get("type"),
        "content": msg.get("content") or "",
        "author": {
            k: author[k]
            for k in ("id", "username", "global_name", "bot")
            if author.get(k) is not None
        },
        "webhook_id": msg.get("webhook_id"),
        "embeds": [compact_embed(e) for e in (msg.get("embeds") or [])],
        "attachments": attachments,
    }

    reference = msg.get("message_reference")
    if reference:
        out["message_reference"] = {
            k: reference[k]
            for k in ("message_id", "channel_id", "guild_id", "type")
            if reference.get(k) is not None
        }

    snapshots = msg.get("message_snapshots")
    if snapshots:
        # Announcement forwarding may include source-message snapshots. Keep them
        # so the timeline audit has the official text even when Discord changes
        # how followed announcement webhooks are represented.
        out["message_snapshots"] = snapshots

    if guild_id:
        out["jump_url"] = f"https://discord.com/channels/{guild_id}/{CHANNEL_ID}/{msg['id']}"
    return out


def meaningful(msg: dict[str, Any]) -> bool:
    # Ignore empty system/setup messages while retaining normal webhook posts,
    # embeds, images, files, and edited announcement messages.
    return bool((msg.get("content") or "").strip() or msg.get("embeds") or msg.get("attachments") or msg.get("message_snapshots"))


def fetch_messages(last_id: str | None) -> list[dict[str, Any]]:
    collected: dict[str, dict[str, Any]] = {}

    # Always re-read the latest messages so edits to recent announcements are
    # mirrored even if their message IDs predate last_message_id.
    latest = api_get(f"/channels/{CHANNEL_ID}/messages", {"limit": 100})
    for msg in latest:
        collected[msg["id"]] = msg

    # Also walk forward from the stored cursor so a burst of >100 messages
    # cannot create a gap between scheduled runs.
    if last_id:
        cursor = last_id
        for _ in range(25):  # hard safety cap: 2,500 messages/run
            batch = api_get(f"/channels/{CHANNEL_ID}/messages", {"limit": 100, "after": cursor})
            if not batch:
                break
            previous_cursor = cursor
            for msg in batch:
                collected[msg["id"]] = msg
                if int(msg["id"]) > int(cursor):
                    cursor = msg["id"]
            if len(batch) < 100 or cursor == previous_cursor:
                break

    return list(collected.values())


def main() -> None:
    if not TOKEN:
        fail("DISCORD_BOT_TOKEN is not set")
    if not CHANNEL_ID.isdigit():
        fail("DISCORD_CHANNEL_ID is missing or invalid")

    feed = load_feed()
    channel = api_get(f"/channels/{CHANNEL_ID}")
    guild_id = channel.get("guild_id")
    incoming = fetch_messages(feed.get("last_message_id"))

    existing = {str(m["id"]): m for m in feed.get("messages", []) if m.get("id")}
    for raw in incoming:
        if meaningful(raw):
            existing[str(raw["id"])] = compact_message(raw, guild_id)

    ordered = sorted(existing.values(), key=lambda m: int(m["id"]))
    # Keep a generous rolling archive without letting the repo grow forever.
    ordered = ordered[-5000:]

    feed = {
        "schema_version": 1,
        "channel": {
            "id": CHANNEL_ID,
            "name": channel.get("name"),
            "guild_id": guild_id,
            "purpose": channel.get("topic"),
        },
        "last_message_id": ordered[-1]["id"] if ordered else feed.get("last_message_id"),
        "messages": ordered,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Mirrored {len(incoming)} recent/new Discord messages; archive contains {len(ordered)} messages.")


if __name__ == "__main__":
    main()
