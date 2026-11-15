# ChainReasoner

[![CI](https://github.com/kapildhinwa2010-dev/ChainReasoner/actions/workflows/ci.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/ChainReasoner/actions/workflows/ci.yml)
[![CI](https://github.com/kapildhinwa2010-dev/ChainReasoner/actions/workflows/codeql.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/ChainReasoner/actions/workflows/codeql.yml)

Multi-hop path analysis over stored facts: branch paths, reachability, shortest path.

**Part of the [Kapildhinwa2010-dev Toolkit](https://github.com/kapildhinwa2010-dev/Kapildhinwa2010-dev).**

## What it does

ChainReasoner is the PATHS layer of the fact-tool family. On top of
the shared triple store it enumerates all branch paths (chain_all),
computes full reachability (reachable) and BFS shortest-path hop
counts (shortest_path). Storage extras live in FactBase; rules in
RuleEngine; alias derivation in AliasDeriver.

## Install

```bash
pip install -r requirements.txt
```

## Quick start

```python
from chainreasoner import KnowledgeNet

net = KnowledgeNet()
net.add("a", "next", "b")
net.add("b", "next", "c")
print(net.shortest_path("a", "c", "next"))  # 2
print(net.reachable("a", "next"))           # ["b", "c"]
```

## API

- add / query / facts / chain / interference - shared triple store
- chain_all(start, predicate, max_hops) - every acyclic path
- reachable(start, predicate, max_hops) - BFS-reachable nodes
- shortest_path(start, end, predicate) - hop count, -1 if unreachable

## Honest results and limitations

- chain_all() is exponential in branching; max_hops is the only guard,
  keep it small on dense graphs.
- shortest_path() counts hops via BFS but does not return the path
  itself.
- No weights or costs - all edges are equal.

## License

MIT - see [LICENSE](LICENSE).
