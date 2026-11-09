"""Text that surrounds a genuine notice when it is forwarded in a chat app.

All fictional and generic. Each wrapper is a function from the notice text to the text a person
would actually paste or screenshot. Used by the engine tests and by eval/run.py.

HARMLESS wrappers carry no web address and no money amount. A genuine notice inside any of
them must be confirmed. Wrappers that carry a payload (a link or money amount that is not in the
record) are in PAYLOAD_WRAPPERS and must NOT be confirmed.
"""

from __future__ import annotations

from collections.abc import Callable

Wrapper = Callable[[str], str]

WRAPPERS: dict[str, Wrapper] = {
    "forwarded": lambda t: f"Forwarded\n\n{t}",
    "forwarded_many_times": lambda t: f"Forwarded many times\n\n{t}",
    "sender_name": lambda t: f"Chidi Okafor\n{t}",
    "sender_tilde": lambda t: f"~ Ngozi Eze\n{t}",
    "sender_phone": lambda t: f"+234 801 234 5678\n~ Ngozi\n{t}",
    "group_prefix": lambda t: f"Mama Ada (Church Group): {t}",
    "timestamp_tail": lambda t: f"{t}\n10:42 AM",
    "timestamp_head_full": lambda t: f"[8/11/2026, 10:42] Chidi: {t}",
    "caption_above": lambda t: f"Please share this with everyone, it is very important.\n{t}",
    "caption_below": lambda t: f"{t}\nPlease forward to all your contacts. God bless you.",
    "caption_with_negations": lambda t: f"Please do not ignore this message.\n{t}\nNo be fake o.",
    "pidgin_caption": lambda t: f"Abeg share dis one o, e dey important.\n{t}",
    "numbers_in_caption": lambda t: f"Forwarded 5 times\n{t}\nSeen by 1,200 people",
    "status_bar_and_input": lambda t: f"10:42 4G 87\n{t}\nType a message",
    "combined": lambda t: (
        "Forwarded\n~ Chidi Okafor\nPlease share, it is urgent!\n" + t + "\nGod bless Nigeria.\n10:42 AM"
    ),
}

# A wrapper that adds something to act on. These must never be confirmed.
PAYLOAD_WRAPPERS: dict[str, Wrapper] = {
    "link_below": lambda t: f"{t}\nRegister faster at https://fast-register.example",
    "link_above": lambda t: f"Click https://fast-register.example first.\n{t}",
    "money_below": lambda t: f"{t}\nPay a processing fee of N500 to your ward officer.",
    "phone_below": lambda t: f"{t}\nCall 08031234567 to complete your registration.",
}
