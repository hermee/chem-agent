"""Load agent definitions from YAML configs."""
import os
import yaml
from pathlib import Path

AGENTS_DIR = Path(__file__).parent


def load_agent_config(agent_id: str) -> dict:
    """Load a single agent config by ID."""
    path = AGENTS_DIR / f"{agent_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Agent config not found: {path}")
    with open(path) as f:
        return yaml.safe_load(f)


def load_all_agents() -> dict[str, dict]:
    """Load all agent configs from the agents directory."""
    agents = {}
    for path in AGENTS_DIR.glob("*.yaml"):
        with open(path) as f:
            data = yaml.safe_load(f)
        # System config vs agent config
        if "agent" in data:
            agents[data["agent"]["id"]] = data["agent"]
        elif "system" in data:
            agents["_system"] = data["system"]
    return agents


def get_system_prompt(agent_id: str) -> str:
    """Get the system prompt for an agent, with global constraints prepended."""
    agents = load_all_agents()
    system = agents.get("_system", {})
    agent = agents.get(agent_id)
    if not agent:
        raise ValueError(f"Unknown agent: {agent_id}")

    constraints = system.get("global_constraints", [])
    prompt = agent.get("system_prompt", "")

    if constraints:
        constraint_block = "\n## Global Constraints\n" + "\n".join(f"- {c}" for c in constraints)
        prompt = prompt.rstrip() + "\n" + constraint_block

    return prompt


def get_model_kwargs(agent_id: str) -> dict:
    """Get model kwargs for an agent."""
    config = load_agent_config(agent_id)
    return config.get("agent", {}).get("model_kwargs", {})
