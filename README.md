# ChainReasoner

ChainReasoner is a small Python module for storing string-valued subject–predicate–object facts and exploring paths through them. Its current implementation provides an in-memory fact store, basic pattern queries, alias grouping, and bounded graph-walk helpers. It is an early-stage utility, not a persistent knowledge base or a general-purpose symbolic reasoning system.

## Features

- Store unique `Fact` triples in a `KnowledgeNet`; `add()` returns `False` when a fact is already present.
- Query facts by subject, predicate, and/or object, with omitted (`None`) fields acting as wildcards.
- Follow a predicate with `chain()` (one matching outgoing edge per step), or enumerate acyclic branch paths with `chain_all()`.
- Find predicate-constrained reachable nodes with breadth-first search using `reachable()`, and compute a shortest-path hop count with `shortest_path()` (`-1` when no route is found within the bound).
- Group entities connected through equality predicates with `derive_aliases()` or `derive_aliases_from()`; each component is mapped to its lexicographically smallest member.
- Rank directly associated facts with `interference()`.

## Requirements and installation

Python 3.9 or newer is declared in `pyproject.toml`. Install the project from its repository root with:

```bash
python -m pip install .
```

The package metadata declares `numpy>=1.24` as a dependency. The current `chainreasoner.py` implementation does not import NumPy.

## Example

```python
from chainreasoner import KnowledgeNet

net = KnowledgeNet()
net.add("a", "next", "b")
net.add("b", "next", "c")

print(net.query(subject="a"))                  # [Fact('a', 'next', 'b')]
print(net.reachable("a", "next"))             # ['b', 'c']
print(net.shortest_path("a", "c", "next"))    # 2
print(net.chain_all("a", "next"))              # [['a', 'b'], ['a', 'b', 'c']]
```

The example uses the module-level import exposed by `chainreasoner.py`. All facts and indexes live in the `KnowledgeNet` instance; the repository contains no persistence or serialization interface.

## API notes

- `Fact(subject, predicate, obj)` requires three non-empty strings. `as_tuple()` returns the triple.
- `KnowledgeNet.add(subject, predicate, obj)` inserts a fact and reports whether it was new. `facts()` returns all stored facts in sorted triple order; `len(net)` reports their count.
- `query(subject=None, predicate=None, obj=None)` filters facts by the supplied fields.
- `chain(start, predicate, max_hops=4)` follows a single matching outgoing edge at each step and stops before revisiting a node. If a node has multiple matching edges, this method does not enumerate all alternatives; use `chain_all()` for branch paths.
- `chain_all(start, predicate, max_hops=4)` returns each discovered acyclic path as a list of nodes, including the start node. Branching can produce many paths, so keep the hop limit small for dense graphs.
- `reachable(start, predicate, max_hops=8)` returns the sorted set of nodes reached within the hop bound.
- `shortest_path(start, end, predicate, max_hops=8)` returns only the number of hops, not the path itself. It returns `-1` if the target is not reached within the bound.
- `derive_aliases_from(predicates)` requires a non-empty collection of predicate names. Alias relations are treated as undirected connected components for this operation.
- `interference(query, top_k=3)` ranks facts that contain `query` as their subject or object by the number of related facts; this is a simple local count, not a general relevance or inference score.

Methods with a `max_hops` argument reject values below 1. Edges have no weights or costs, and queries/path operations do not apply logical rules or infer new facts.

## Tests and CI

The test suite is run with:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

At commit `b5ca3bd9d71fa04229333516cef1b76bad0fcf1c`, `python3 -m pytest -q` completed with **12 passed**. The repository’s CI workflow also defines tests and compile/import smoke checks on Python 3.10, 3.11, and 3.12; this README does not assert a remote workflow result.

## License

The repository includes an MIT License. See [LICENSE](LICENSE) for the complete terms and copyright notice.
