import pytest
from unittest.mock import patch

def test_minimax_client_initialization():
    from src.services.minimax_client import MiniMaxClient
    client = MiniMaxClient(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.base_url == "https://api.minimax.chat/v1"
