"""Atlas: a personal job/life knowledge graph.

Typed entity graph (identities, orgs, repos, checkouts, servers, workflows,
rules, plan stores) over human-editable YAML facts, with deterministic
markdown rendering so a zero-context AI agent can bootstrap instantly.
"""

from athenah_ai.atlas.store import AtlasValidationError, FactStore

__all__ = ["AtlasValidationError", "FactStore", "load_atlas"]


def load_atlas(facts_dir: str = None):
    """Load the atlas graph from a facts directory.

    Args:
        facts_dir: Facts directory override; defaults to config.atlas.facts_dir.

    Returns:
        AtlasGraph built from the merged taught + derived facts.
    """
    from athenah_ai.atlas.graph import AtlasGraph
    from athenah_ai.config import config

    store = FactStore(facts_dir or config.atlas.facts_dir)
    return AtlasGraph.from_store(store)
