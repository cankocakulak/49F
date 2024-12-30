import pytest
from datetime import datetime
from src.dtn_core import Bundle, DTNNode

def test_bundle_creation():
    """Bundle oluşturma testi."""
    bundle = Bundle(
        source="mars_rover",
        destination="earth_station",
        payload="Test message"
    )
    assert bundle.source == "mars_rover"
    assert bundle.destination == "earth_station"
    assert bundle.payload == "Test message"
    assert isinstance(bundle.creation_timestamp, datetime)

def test_node_operations():
    """DTN düğüm operasyonları testi."""
    node1 = DTNNode("node1")
    node2 = DTNNode("node2")

    bundle = Bundle(
        source="node1",
        destination="node2",
        payload="Test message"
    )

    # Bundle'ı node1'e gönder
    assert node1.receive_bundle(bundle) == True
    assert len(node1.storage) == 1

    # node1'den node2'ye ilet
    assert node1.forward_bundle(node2) == True
    assert len(node1.storage) == 0