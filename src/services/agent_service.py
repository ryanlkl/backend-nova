import re

SOURCE_PATTERN = r"\[Source:\s*(.+?)\]"

def exec_query(query, history, agent):
    messages = clean_history(history)
    messages.append({"role": "user", "content": query})

    result = agent.invoke({"messages": messages})
    all_messages = result["messages"]

    final_ai_message = None
    for msg in reversed(all_messages):
        if getattr(msg, "type", None) == "ai":
            final_ai_message = msg
            break

    if final_ai_message is None:
        return {
            "message": "No AI response returned.",
            "tools": [],
            "legislation_tool_response": None,
            "market_tool_response": None,
        }

    raw_message = final_ai_message.content
    if not isinstance(raw_message, str):
        raw_message = str(raw_message)

    tools = getattr(final_ai_message, "tool_calls", []) or []

    legislation_tool_response = None
    market_tool_response = None
    collected_sources = []

    for msg in all_messages:
        if getattr(msg, "type", None) == "tool":
            tool_name = getattr(msg, "name", None)
            tool_content = msg.content or ""

            if tool_name == "search_legislation":
                legislation_tool_response = tool_content
            elif tool_name == "search_market":
                market_tool_response = tool_content

            collected_sources.extend(extract_sources(tool_content))

    unique_sources = list(dict.fromkeys(collected_sources))
    clean_message = remove_answer_and_sources_block(raw_message)

    if unique_sources:
        source_lines = "\n".join(f"[Source: {source}]" for source in unique_sources)
        final_message = f"{clean_message}\n\n{source_lines}"
    else:
        final_message = clean_message

    return {
        "message": final_message,
        "tools": tools,
        "legislation_tool_response": legislation_tool_response,
        "market_tool_response": market_tool_response
    }


def extract_sources(text: str) -> list[str]:
    if not text:
        return []
    return re.findall(SOURCE_PATTERN, text)


def remove_answer_and_sources_block(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    if text.startswith("Answer:"):
        text = text[len("Answer:"):].strip()

    text = re.sub(r"\n*Sources:\s*\n[\s\S]*$", "", text, flags=re.IGNORECASE).strip()
    return text


def clean_history(history: list[dict], max_turns: int = 4) -> list[dict]:
    cleaned = []

    for msg in history or []:
        role = msg.get("role")
        content = (msg.get("content") or "").strip()

        if role not in {"user", "assistant"}:
            continue
        if not content:
            continue

        if role == "assistant":
            lower = content.lower()
            if "sorry, something went wrong" in lower:
                continue
            if "network error occurred" in lower:
                continue
            if "[object object]" in lower:
                continue

        cleaned.append({"role": role, "content": content})

    return cleaned[-(max_turns * 2):]