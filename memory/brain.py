from __future__ import annotations

from pathlib import Path
from typing import Any

from memory.bus import MemoryBus
from memory.embeddings import get_engine
from memory.episodic import EpisodicMemory, Episode
from memory.semantic import SemanticMemory, Concept


class Brain:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.base_path = self.repo_root / ".ai-team" / "memory"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._validate_scope()
        self._bus = MemoryBus(self.repo_root)
        self.episodic = EpisodicMemory(self.base_path / "episodes")
        self.semantic = SemanticMemory(self.base_path / "semantic")
        self.engine = get_engine()

    def _validate_scope(self) -> None:
        scope_file = self.base_path / ".project_scope"
        scope_text = str(self.repo_root)
        if scope_file.exists():
            stored = scope_file.read_text(encoding="utf-8").strip()
            if stored != scope_text:
                raise RuntimeError(
                    f"Memory scope mismatch: stored project is '{stored}', "
                    f"but requested project is '{scope_text}'. "
                    f"Agents may not access memory from a different project."
                )
        else:
            scope_file.write_text(scope_text, encoding="utf-8")

    def perceive(self, context: str, action: str, outcome: str = "", emotion: str = "neutral", tags: list[str] | None = None) -> Episode:
        with self._bus.exclusive():
            ep = self.episodic.record(context, action, outcome, emotion, tags)
            self._extract_concepts(context + " " + action + " " + outcome)
            return ep

    def remember(self, query: str, top_k: int = 5) -> dict[str, Any]:
        with self._bus.shared():
            episodes = self.episodic.recall(query, top_k)
            concepts = self.semantic.query(query, top_k)
        return {
            "episodes": [ep.to_dict() for ep in episodes],
            "concepts": [c.to_dict() for c in concepts],
            "query": query,
        }

    def recent(self, n: int = 5) -> list[Episode]:
        with self._bus.shared():
            return self.episodic.recent(n)

    def learn(self, concept_id: str, label: str, description: str = "", related: list[str] | None = None) -> Concept:
        with self._bus.exclusive():
            return self.semantic.learn(concept_id, label, description, related)

    def relate(self, a: str, b: str) -> None:
        with self._bus.exclusive():
            self.semantic.relate(a, b)

    def _extract_concepts(self, text: str) -> None:
        words = [w for w in text.lower().split() if len(w) > 5]
        for word in set(words):
            cid = word.replace(" ", "_")
            existing = self.semantic.get(cid)
            if existing is not None:
                continue
            # Deduplication: check similarity against all existing concepts
            all_concepts = self.semantic.list_all()
            if not all_concepts:
                self.semantic.learn(cid, label=word, description=f"Auto-extracted from experience: {word}")
                continue
            vec = self.engine.encode(word)
            np = __import__("numpy")
            best_sim = 0.0
            best_concept = None
            for c in all_concepts:
                if c.embedding:
                    cvec = np.array(c.embedding, dtype=np.float32)
                    sim = self.engine.similarity(vec, cvec)
                    if sim > best_sim:
                        best_sim = sim
                        best_concept = c
            if best_sim > 0.85 and best_concept is not None:
                # Merge: update description of existing concept
                desc = f"{best_concept.description}; also: {word}"
                self.semantic.learn(best_concept.id, label=best_concept.label, description=desc, related=best_concept.related)
            elif best_sim > 0.60 and best_concept is not None:
                # Add as related
                self.semantic.relate(best_concept.id, cid)
                # Also create the new concept with relation back
                related = [best_concept.id]
                self.semantic.learn(cid, label=word, description=f"Auto-extracted from experience: {word}", related=related)
            else:
                self.semantic.learn(cid, label=word, description=f"Auto-extracted from experience: {word}")

    def summarize(self, n_episodes: int = 10) -> str:
        with self._bus.shared():
            eps = self.episodic.recent(n_episodes)
            concepts = self.semantic.list_all()[:10]
        if not eps:
            return "No memories yet."
        lines = [f"Recent {len(eps)} episodes:"]
        for ep in eps:
            lines.append(f"- [{ep.timestamp}] {ep.context} -> {ep.action} -> {ep.outcome}")
        if concepts:
            lines.append("\nKnown concepts:")
            for c in concepts:
                lines.append(f"- {c.label}: {c.description[:60]}")
        return "\n".join(lines)
