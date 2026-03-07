import re

SOURCE_PATTERN = r"\[Source:\s*(.+?)\]"

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

def exec_query(query, history, agent):
    messages = []

    for item in history or []:
        role = item.get("role")
        content = item.get("content")
        if role and content:
            messages.append({"role": role, "content": content})

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