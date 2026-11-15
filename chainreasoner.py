# ChainReasoner - Multi-hop path analysis over stored facts
# Part of the Kapildhinwa2010-dev Toolkit.

"""ChainReasoner - multi-hop path analysis over stored facts.

Lineage: reserv.dean-part-2 (HELIX). On top of the shared triple store
this repo focuses on PATHS: all branch paths (chain_all), full
reachability (reachable), and BFS shortest-path hop counts
(shortest_path). Storage, rules and alias derivation live in the
sibling repos.
"""

from __future__ import annotations

from collections import defaultdict

__all__ = ["Fact", "KnowledgeNet"]


class Fact:
    """A single (subject, predicate, object) triple."""

    __slots__ = ("subject", "predicate", "object")

    def __init__(self, subject: str, predicate: str, obj: str) -> None:
        for value in (subject, predicate, obj):
            if not isinstance(value, str) or not value:
                raise ValueError("subject, predicate and object must be non-empty strings")
        self.subject = subject
        self.predicate = predicate
        self.object = obj

    def as_tuple(self):
        return (self.subject, self.predicate, self.object)

    def __eq__(self, other) -> bool:
        return isinstance(other, Fact) and self.as_tuple() == other.as_tuple()

    def __hash__(self) -> int:
        return hash(self.as_tuple())

    def __repr__(self) -> str:
        return "Fact({!r}, {!r}, {!r})".format(*self.as_tuple())


class KnowledgeNet:
    """Fact store with indexed direct and reverse queries."""

    def __init__(self) -> None:
        self._facts: set = set()
        self._by_subject: dict = defaultdict(list)
        self._by_object: dict = defaultdict(list)

    def add(self, subject: str, predicate: str, obj: str) -> bool:
        """Add a fact; returns False if it already exists."""
        fact = Fact(subject, predicate, obj)
        if fact in self._facts:
            return False
        self._facts.add(fact)
        self._by_subject[fact.subject].append(fact)
        self._by_object[fact.object].append(fact)
        return True

    def facts(self):
        return sorted(self._facts, key=lambda f: f.as_tuple())

    def __len__(self) -> int:
        return len(self._facts)

    def query(self, subject=None, predicate=None, obj=None):
        """Return facts matching the given pattern (None = wildcard)."""
        results = self._facts
        if subject is not None:
            results = [f for f in results if f.subject == subject]
        if predicate is not None:
            results = [f for f in results if f.predicate == predicate]
        if obj is not None:
            results = [f for f in results if f.object == obj]
        return sorted(results, key=lambda f: f.as_tuple())

    def derive_aliases(self) -> dict:
        """Transitive closure of ``same_as`` equality facts."""
        return self.derive_aliases_from(["same_as"])

    def derive_aliases_from(self, predicates) -> dict:
        """Transitive closure over ANY of the given equality predicates."""
        preds = set(predicates)
        if not preds:
            raise ValueError("predicates must be non-empty")
        adjacency: dict = defaultdict(set)
        for fact in self._facts:
            if fact.predicate in preds:
                adjacency[fact.subject].add(fact.object)
                adjacency[fact.object].add(fact.subject)
        aliases: dict = {}
        for node in list(adjacency):
            if node in aliases:
                continue
            component = set()
            stack = [node]
            while stack:
                current = stack.pop()
                if current in component:
                    continue
                component.add(current)
                stack.extend(adjacency[current] - component)
            canonical = min(component)
            for member in component:
                aliases[member] = canonical
        return aliases

    def chain(self, start: str, predicate: str, max_hops: int = 4) -> list:
        """Multi-hop walk following ``predicate`` from ``start``."""
        if max_hops < 1:
            raise ValueError("max_hops must be >= 1")
        hops = []
        current = start
        seen = {start}
        for _ in range(max_hops):
            nxt = [f.object for f in self._by_subject.get(current, []) if f.predicate == predicate]
            if not nxt:
                break
            hops.append(nxt[0])
            if nxt[0] in seen:
                break
            seen.add(nxt[0])
            current = nxt[0]
        return hops

    def interference(self, query: str, top_k: int = 3) -> list:
        """Rank facts related to ``query`` by co-occurrence interference."""
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        scores: dict = {}
        for fact in self._facts:
            if query in (fact.subject, fact.object):
                related = self.query(subject=fact.object) + self.query(obj=fact.subject)
                scores[fact] = len(related)
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0].as_tuple()))
        return [fact for fact, _ in ranked[:top_k]]

    def chain_all(self, start: str, predicate: str, max_hops: int = 4) -> list:
        """Every acyclic node sequence following ``predicate``, up to max_hops.

        Unlike chain() (which follows only the first match per hop), this
        enumerates all branches. Returns a list of paths (each a list of
        node names starting with ``start``).
        """
        if max_hops < 1:
            raise ValueError("max_hops must be >= 1")
        paths: list = []

        def walk(node: str, path: list) -> None:
            if len(path) - 1 >= max_hops:
                return
            for f in self._by_subject.get(node, []):
                if f.predicate == predicate and f.object not in path:
                    paths.append(path + [f.object])
                    walk(f.object, path + [f.object])

        walk(start, [start])
        return paths

    def reachable(self, start: str, predicate: str, max_hops: int = 8) -> list:
        """Every node reachable from ``start`` via ``predicate`` (BFS)."""
        if max_hops < 1:
            raise ValueError("max_hops must be >= 1")
        seen: set = set()
        frontier = [start]
        for _ in range(max_hops):
            nxt = []
            for node in frontier:
                for f in self._by_subject.get(node, []):
                    if f.predicate == predicate and f.object not in seen:
                        seen.add(f.object)
                        nxt.append(f.object)
            if not nxt:
                break
            frontier = nxt
        return sorted(seen)

    def shortest_path(self, start: str, end: str, predicate: str, max_hops: int = 8) -> int:
        """Fewest hops from ``start`` to ``end`` via ``predicate``; -1 if unreachable."""
        if max_hops < 1:
            raise ValueError("max_hops must be >= 1")
        from collections import deque

        dist = {start: 0}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            if node == end:
                return dist[node]
            if dist[node] >= max_hops:
                continue
            for f in self._by_subject.get(node, []):
                if f.predicate == predicate and f.object not in dist:
                    dist[f.object] = dist[node] + 1
                    queue.append(f.object)
        return -1
