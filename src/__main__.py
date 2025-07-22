from .agent import GBIFAgent
from ichatbio.server import run_agent_server
from src.log import setup_logger

# Force logger initialization
logger = setup_logger()
logger.info("TEST: Logging system startup check")
print("DEBUG: Logging initialized, test message logged")

if __name__ == "__main__":
    gbif = GBIFAgent()
    run_agent_server(gbif, host="0.0.0.0", port=9999)
