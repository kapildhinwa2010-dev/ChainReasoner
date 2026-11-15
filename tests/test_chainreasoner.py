import pytest

from chainreasoner import Fact, KnowledgeNet


def test_fact_basic():
    fact = Fact("a", "next", "b")
    assert fact.as_tuple() == ("a", "next", "b")


def test_fact_rejects_empty():
    with pytest.raises(ValueError):
        Fact("", "next", "b")


def test_add_and_len():
    net = KnowledgeNet()
    assert net.add("a", "next", "b") is True
    assert len(net) == 1


def test_chain_walk():
    net = KnowledgeNet()
    net.add("a", "next", "b")
    net.add("b", "next", "c")
    net.add("c", "next", "d")
    assert net.chain("a", "next") == ["b", "c", "d"]


def test_chain_respects_max_hops():
    net = KnowledgeNet()
    net.add("a", "next", "b")
    net.add("b", "next", "c")
    assert net.chain("a", "next", max_hops=1) == ["b"]


def test_chain_handles_cycles():
    net = KnowledgeNet()
    net.add("a", "next", "b")
    net.add("b", "next", "a")
    assert net.chain("a", "next") == ["b"]


# --- path analysis (ChainReasoner-specific) ---


def test_chain_all_enumerates_branches():
    net = KnowledgeNet()
    net.add("a", "next", "b")
    net.add("a", "next", "c")
    net.add("b", "next", "d")
    paths = net.chain_all("a", "next")
    assert ["a", "b"] in paths
    assert ["a", "c"] in paths
    assert ["a", "b", "d"] in paths
    assert len(paths) == 3


def test_chain_all_rejects_bad_hops():
    net = KnowledgeNet()
    with pytest.raises(ValueError):
        net.chain_all("a", "next", max_hops=0)


def test_reachable():
    net = KnowledgeNet()
    net.add("a", "next", "b")
    net.add("b", "next", "c")
    net.add("z", "next", "y")
    assert net.reachable("a", "next") == ["b", "c"]
    assert net.reachable("z", "next") == ["y"]
    assert net.reachable("lonely", "next") == []


def test_shortest_path_found():
    net = KnowledgeNet()
    net.add("a", "next", "b")
    net.add("b", "next", "c")
    net.add("c", "next", "d")
    assert net.shortest_path("a", "d", "next") == 3
    assert net.shortest_path("a", "b", "next") == 1


def test_shortest_path_unreachable():
    net = KnowledgeNet()
    net.add("a", "next", "b")
    net.add("x", "next", "y")
    assert net.shortest_path("a", "y", "next") == -1


def test_shortest_path_rejects_bad_hops():
    net = KnowledgeNet()
    with pytest.raises(ValueError):
        net.shortest_path("a", "a", "next", max_hops=0)