import pytest
from src.common.log.logger import get_logger


@pytest.mark.unit
def test_get_logger():
    """Test get_logger returns a logger instance."""
    logger = get_logger("test_logger")
    assert logger.name == "test_logger"
    assert hasattr(logger, "info")
    assert hasattr(logger, "debug")
    assert hasattr(logger, "error")
