import re
from langgraph.types import Send

from backend.models.state import State
from backend.models.schema import Plan
from backend.core.settings import settings
from backend.graph.prompt import load_prompt
from backend.services.llm_service import llm


def planner_node(state: State) -> dict:

    print("============ Calling Planner ============")

    planner_prompt = load_prompt(agent="planner")
    messages = planner_prompt.format_messages(topic=state.topic)

    planner = llm.with_structured_output(Plan, method="json_mode")

    plan = planner.invoke(messages)

    print(f"PLANNER OUTPUT:\n{plan}\n")

    print("============ Ending Planner ============")
    
    return {"plan": plan}


def fanout(state: State):
    return [
        Send("writer_node", {"task": task, "topic": state.topic, "plan": state.plan})
        for task in state.plan.tasks
    ]


def writer_node(payload: dict) -> dict:

    print("============ Calling Writer ============")

    # payload contains what we sent
    task = payload["task"]
    topic = payload["topic"]
    plan = payload["plan"]

    bullets_text = "\n- " + "\n- ".join(task.bullets)

    writer_prompt = load_prompt("writer")
    messages = writer_prompt.format_messages(
        blog_title=plan.blog_title,
        audience=plan.audience,
        tone=plan.tone,
        topic=topic,
        section_title=task.title,
        section_type=task.section_type,
        goal=task.goal,
        target_words=task.target_words,
        bullets_text=bullets_text,
    )

    section_md = llm.invoke(messages).content.strip()

    return {"sections": [section_md]}


def refiner_node(state: State) -> dict:

    print("============ Calling Refiner ============")
    
    title = state.plan.blog_title
    title = re.sub(r"\.md$", "", title, flags=re.IGNORECASE)
    title = re.sub(r'[<>:"/\\|?*]', "", title)

    body = "\n\n".join(state.sections).strip()
    final_md = f"# {title}\n\n{body}\n"

    # ---- save to file ----
    filename = title.lower().replace(" ", "_") + ".md"
    output_path = settings.OUTPUT_DIR / filename
    output_path.write_text(final_md, encoding="utf-8")

    print(f"Saved markdown to: {output_path.resolve()}")

    print("============ Ending Refiner ============")

    return {"final": final_md}