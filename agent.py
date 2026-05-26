import logging
import os
import sys

from dotenv import load_dotenv

# Load .env before importing ddtrace / LangChain so DD_API_KEY is visible
# to ddtrace at patch time, and DD patches LangChain before we import it.
load_dotenv()

# Silence ddtrace's stderr chatter (trace writer warnings, etc.) so it
# doesn't bleed into the CLI prompt. Real errors still surface.
logging.getLogger("ddtrace").setLevel(logging.ERROR)

from ddtrace.llmobs import LLMObs

_LLMOBS_ENABLED = bool(os.environ.get("DD_API_KEY"))
if _LLMOBS_ENABLED:
    LLMObs.enable(ml_app="anime-recommender", agentless_enabled=True)
else:
    print(
        "warning: DD_API_KEY not set — running without Datadog LLM Observability.",
        file=sys.stderr,
    )

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


SYSTEM_PROMPT = """You are a friendly, knowledgeable anime recommender helping a user find a series to watch.

Do not ask them about anime they've enjoyed or anime genres they like — they might not have that frame of reference yet. Instead, learn about their general tastes and preferences from things they already know: movies, TV shows, books, video games, themes / settings / characters they tend to gravitate toward, and what they want to get out of watching something (e.g. escapism, something thought-provoking, something light and fun).

How to behave:
- If the user's request is vague (e.g. "recommend me something"), ask 1-2 brief clarifying questions before recommending. Good things to ask about: favorite movies / shows / books / games, themes or settings they're drawn to, characters they find interesting, and series-length preference (short ~12 episodes vs. longer commitment). Do NOT ask about mood or about anime they've watched.
- If the user's request is specific (e.g. "I like the movie Inception"), go straight to recommending.
- Once you have enough signal, recommend 2-3 titles. For each, give:
  - the title (English),
  - the length (number of episodes),
  - a one-line pitch,
  - why it fits this user specifically (reference the non-anime tastes they shared — e.g. "since you loved Inception, this one plays with reality the same way"),
  - a brief tonal heads-up if relevant (e.g. "heavy themes", "very slow-paced", "lots of fanservice").
- Lean toward beginner-friendly picks — strong standalone stories, accessible art styles, and series that don't require prior anime literacy. Avoid recommending titles that only land if you already know the medium's conventions.
- Do not invent anime. If you are unsure whether a title exists, skip it.
- Stay on topic. If the user goes off-topic, politely redirect back to anime recommendations.
- Keep responses tight and conversational. No long preambles."""


def build_model() -> ChatAnthropic:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "error: ANTHROPIC_API_KEY is not set. "
            "Add it to .env or export it in your shell.",
            file=sys.stderr,
        )
        sys.exit(1)
    return ChatAnthropic(
        model="claude-sonnet-4-6",
        temperature=0.7,
        max_tokens=1024,
    )


WELCOME = """\
╭──────────────────────────────────────────────────────────────╮
│  🍥  anime recommender                                        │
╰──────────────────────────────────────────────────────────────╯

Hey! I help people pick their first anime to watch.

Tell me about the kinds of stories you already love — favorite movies,
shows, books, games, themes you can't get enough of — and I'll suggest
a few anime that match.

Commands: /reset to start over · /quit to exit
"""


def run_repl(model: ChatAnthropic) -> None:
    messages: list = [SystemMessage(content=SYSTEM_PROMPT)]
    print(WELCOME)
    while True:
        try:
            user_input = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not user_input:
            continue
        if user_input in {"/quit", "/exit"}:
            return
        if user_input == "/reset":
            messages = [SystemMessage(content=SYSTEM_PROMPT)]
            print("(conversation reset)\n")
            continue

        messages.append(HumanMessage(content=user_input))
        response = model.invoke(messages)
        messages.append(AIMessage(content=response.content))
        print(f"\nagent > {response.content}\n")


def main() -> None:
    model = build_model()
    try:
        run_repl(model)
    finally:
        if _LLMOBS_ENABLED:
            LLMObs.flush()


if __name__ == "__main__":
    main()
