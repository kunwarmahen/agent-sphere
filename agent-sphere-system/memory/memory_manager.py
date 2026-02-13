"""
Persistent Long-Term Memory — Phase 4
Stores facts and context per agent across sessions.

Storage: data/memory/<agent_id>.json
Each entry: {id, content, category, source, created_at, importance (1-5)}

Key features:
- Manual storage via /remember command
- LLM-powered auto-extraction from conversation turns
- Memory injected into agent system prompt on every call
- Session compacting: old conversation summaries stored as memories
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "memory")
MAX_MEMORIES = 200          # max entries per agent before oldest are pruned
PROMPT_MEMORY_LIMIT = 15    # how many memories to inject into each prompt


class MemoryManager:

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._cache: Dict[str, List[Dict]] = {}

    # ------------------------------------------------------------------ #
    # Persistence                                                          #
    # ------------------------------------------------------------------ #

    def _path(self, agent_id: str) -> str:
        safe = agent_id.replace("/", "_").replace("..", "_")
        return os.path.join(DATA_DIR, f"{safe}.json")

    def _load(self, agent_id: str) -> List[Dict]:
        if agent_id in self._cache:
            return self._cache[agent_id]
        path = self._path(agent_id)
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                self._cache[agent_id] = data
                return data
            except Exception as e:
                logger.warning(f"Could not load memory for {agent_id}: {e}")
        self._cache[agent_id] = []
        return self._cache[agent_id]

    def _save(self, agent_id: str):
        memories = self._cache.get(agent_id, [])
        # Prune to MAX_MEMORIES — drop lowest-importance oldest entries
        if len(memories) > MAX_MEMORIES:
            memories.sort(key=lambda m: (m.get("importance", 3), m["created_at"]))
            memories = memories[-MAX_MEMORIES:]
            self._cache[agent_id] = memories
        try:
            with open(self._path(agent_id), "w") as f:
                json.dump(memories, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save memory for {agent_id}: {e}")

    # ------------------------------------------------------------------ #
    # CRUD                                                                 #
    # ------------------------------------------------------------------ #

    def add(
        self,
        agent_id: str,
        content: str,
        category: str = "fact",
        source: str = "manual",
        importance: int = 3,
    ) -> Dict:
        """Add a new memory entry. Returns the created entry."""
        content = content.strip()
        if not content:
            return {"success": False, "error": "Memory content is empty"}

        memories = self._load(agent_id)

        # Avoid exact and near-duplicate entries (substring overlap > 80%)
        content_lower = content.lower()
        for m in memories:
            existing = m["content"].lower()
            if existing == content_lower:
                return {"success": False, "error": "Duplicate memory", "memory": m}
            # Reject if one is largely contained in the other (fuzzy dedup)
            shorter, longer = sorted([content_lower, existing], key=len)
            if shorter and shorter in longer:
                return {"success": False, "error": "Duplicate memory", "memory": m}

        entry = {
            "id": uuid.uuid4().hex[:12],
            "agent_id": agent_id,
            "content": content,
            "category": category,      # fact | preference | context | summary
            "source": source,          # manual | auto | command | compact
            "importance": max(1, min(5, importance)),
            "created_at": datetime.now().isoformat(),
        }
        memories.append(entry)
        self._save(agent_id)
        logger.info(f"Memory added for {agent_id}: {content[:60]}")
        return {"success": True, "memory": entry}

    def get_all(self, agent_id: str) -> List[Dict]:
        """Return all memories for an agent, newest first."""
        memories = self._load(agent_id)
        return list(reversed(memories))

    def delete(self, agent_id: str, memory_id: str) -> Dict:
        memories = self._load(agent_id)
        before = len(memories)
        self._cache[agent_id] = [m for m in memories if m["id"] != memory_id]
        if len(self._cache[agent_id]) == before:
            return {"success": False, "error": "Memory not found"}
        self._save(agent_id)
        return {"success": True}

    def clear(self, agent_id: str) -> Dict:
        self._cache[agent_id] = []
        self._save(agent_id)
        return {"success": True}

    def list_agents(self) -> List[str]:
        """Return all agent IDs that have stored memories."""
        agents = []
        if os.path.exists(DATA_DIR):
            for fname in os.listdir(DATA_DIR):
                if fname.endswith(".json"):
                    agents.append(fname[:-5])
        return sorted(agents)

    # ------------------------------------------------------------------ #
    # Prompt injection                                                     #
    # ------------------------------------------------------------------ #

    def format_for_prompt(self, agent_id: str) -> str:
        """Return a formatted memory block to prepend to the system prompt."""
        memories = self._load(agent_id)
        if not memories:
            return ""

        # Sort by importance desc, then recency desc, take top N
        sorted_mems = sorted(
            memories,
            key=lambda m: (m.get("importance", 3), m["created_at"]),
            reverse=True,
        )[:PROMPT_MEMORY_LIMIT]

        lines = ["[Long-term memory — facts you know about the user and context:]"]
        for m in sorted_mems:
            cat = m.get("category", "fact").upper()
            lines.append(f"- [{cat}] {m['content']}")
        lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Auto-extraction                                                      #
    # ------------------------------------------------------------------ #

    def extract_and_store(self, agent_id: str, user_message: str, agent_response: str):
        """
        Ask the LLM to extract memorable facts from a conversation turn.
        Runs asynchronously — failures are silent so they don't block chat.
        """
        try:
            from llm.llm_router import llm_router

            prompt = f"""Extract any important facts, preferences, or personal details worth remembering from this conversation turn.
Output ONLY a JSON array of strings (the facts). If nothing worth saving, output [].
Do NOT include trivial, temporary, or request-specific info.

User said: {user_message[:500]}
Assistant replied: {agent_response[:500]}

Output format: ["fact 1", "fact 2"] or []"""

            result = llm_router.chat([
                {"role": "user", "content": prompt}
            ])

            # Parse the JSON array
            import re
            match = re.search(r'\[.*?\]', result, re.DOTALL)
            if not match:
                return

            facts = json.loads(match.group(0))
            if not isinstance(facts, list):
                return

            for fact in facts[:5]:   # cap at 5 auto-extracted facts per turn
                if isinstance(fact, str) and len(fact) > 10:
                    self.add(
                        agent_id=agent_id,
                        content=fact,
                        category="fact",
                        source="auto",
                        importance=2,
                    )
        except Exception as e:
            logger.debug(f"Auto-extraction skipped: {e}")

    def compact_conversation(self, agent_id: str, conversation: List[Dict]) -> str:
        """
        Summarize a long conversation and store the summary as a memory.
        Returns the summary text.
        """
        if len(conversation) < 6:
            return ""
        try:
            from llm.llm_router import llm_router

            turns = "\n".join(
                f"{m['role'].upper()}: {m['content'][:300]}"
                for m in conversation[-20:]
            )
            summary_prompt = f"""Summarize the key points, decisions, and facts from this conversation in 3-5 bullet points:

{turns}

Output ONLY the bullet points, one per line, starting with -"""

            summary = llm_router.chat([
                {"role": "user", "content": summary_prompt}
            ])

            self.add(
                agent_id=agent_id,
                content=f"Conversation summary: {summary[:600]}",
                category="summary",
                source="compact",
                importance=4,
            )
            return summary
        except Exception as e:
            logger.warning(f"Compaction failed: {e}")
            return ""


# Singleton
memory_manager = MemoryManager()
