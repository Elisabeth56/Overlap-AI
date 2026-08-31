"""Strands hello-world.

Day 1 keeps the loop trivial: no LLM reasoning, no strategy switch — just
call the read_project tool and return the name. This lets us verify the
plumbing (FastAPI → agent module → Postgres) before Bedrock access lands.

On Day 2 we swap `run_hello()` for an actual Strands Agent invocation
(commented at the bottom) once Claude on Bedrock is enabled.
"""
from __future__ import annotations

from overlap.state.db import emit_event, get_project


def run_hello(project_id: str) -> dict:
    """Day 1 loop: read the project, log an event, return its name."""
    row = get_project(project_id)
    if row is None:
        raise LookupError(f"project {project_id} not found")

    emit_event(
        project_id=project_id,
        kind="agent.tick",
        actor="agent",
        payload={"phase": "hello", "project_name": row["name"]},
    )
    return {"project_id": str(row["id"]), "project_name": row["name"]}


# --- Day 2+ shape (kept commented until Bedrock access lands) ------------
#
# from pathlib import Path
# from strands import Agent
# from strands.models.bedrock import BedrockModel
# from overlap.config import settings
# from overlap.tools import read_project
#
# _PROMPT = (Path(__file__).parent / "prompts" / "hello.md").read_text()
#
# def build_agent() -> Agent:
#     return Agent(
#         model=BedrockModel(
#             model_id=settings.bedrock_model_id,
#             region_name=settings.aws_region,
#         ),
#         tools=[read_project],
#         system_prompt=_PROMPT,
#     )
#
# def run_with_llm(project_id: str) -> str:
#     agent = build_agent()
#     return agent(f"project_id: {project_id}")
