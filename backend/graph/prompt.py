from langchain_core.prompts import ChatPromptTemplate

from backend.core.settings import settings


def load_prompt(
    agent: str,
    human_template: str | None = None,
) -> ChatPromptTemplate:
    """
    Loads prompts/{agent}/system.md and returns a ChatPromptTemplate.

    Args:
        agent: planner, writer, reviewer, etc.
        human_template: Override human prompt if desired.
    """

    agent_dir = settings.PROMPTS_DIR / agent

    system_prompt = (agent_dir / "system.md").read_text(encoding="utf-8").strip()

    if human_template is None:
        human_prompt = (agent_dir / "human.md").read_text(encoding="utf-8").strip()
    else:
        human_prompt = human_template

    return ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt),
        ]
    )