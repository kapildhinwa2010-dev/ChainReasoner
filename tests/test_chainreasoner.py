import pytest
import torch
from chainreasoner import ChainReasoner, create_chainreasoner

class TestChainReasoner:
    def test_init(self):
        m = ChainReasoner(dim=256, hidden_dim=512)
        assert m.dim == 256
    
    def test_forward(self):
        m = ChainReasoner(dim=256)
        x = torch.randn(32, 256)
        assert m(x).shape == (32, 256)
    
    def test_factory(self):
        m = create_chainreasoner()
        assert isinstance(m, ChainReasoner)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
