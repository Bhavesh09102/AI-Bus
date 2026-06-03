EPISODIC_TRIGGERS = [
    "yesterday", "last week", "last month", "previously", "earlier", "before",
    "recently", "last time", "when did", "what did i work", "history", "ago",
    "on monday", "on tuesday", "on wednesday", "on thursday", "on friday",
]

SEMANTIC_TRIGGERS = [
    "how should", "what's the best", "which approach", "recommend",
    "should i use", "better way", "how do i normally", "what's my",
    "do i usually", "what do i prefer", "fix", "debug", "write", "build",
    "create", "implement", "refactor", "review", "help me", "how do i",
    "explain", "error",
]


def route_memory(message: str) -> set:
    msg = message.lower()
    types = {"working"}
    if any(t in msg for t in EPISODIC_TRIGGERS):
        types.add("episodic")
    if any(t in msg for t in SEMANTIC_TRIGGERS):
        types.add("semantic")
    return types


def build_context_string(fetched_memories: dict):
    sections = []
    total = 0
    cap = 5
    breakdown = {"working": 0, "episodic": 0, "semantic": 0}

    working = fetched_memories.get("working") or {}
    if working and total < cap:
        lines = []
        for key, value in working.items():
            if total >= cap:
                break
            lines.append(f"  - {key}: {value}")
            total += 1
            breakdown["working"] += 1
        if lines:
            sections.append("Current session:\n" + "\n".join(lines))

    episodic = fetched_memories.get("episodic") or []
    if episodic and total < cap:
        lines = []
        for item in episodic:
            if total >= cap:
                break
            date = item.get("written_at", "")[:10]
            content = item.get("content", "")
            lines.append(f"  - {date}: {content}")
            total += 1
            breakdown["episodic"] += 1
        if lines:
            sections.append("Recent activity:\n" + "\n".join(lines))

    semantic = fetched_memories.get("semantic") or []
    if semantic and total < cap:
        lines = []
        for item in semantic:
            if total >= cap:
                break
            content = item.get("content", "")
            lines.append(f"  - {content}")
            total += 1
            breakdown["semantic"] += 1
        if lines:
            sections.append("About this user:\n" + "\n".join(lines))

    if not sections:
        return "", 0, breakdown
    return "\n\n".join(sections), total, breakdown
