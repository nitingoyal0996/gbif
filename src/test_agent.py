"""Test"""
import asyncio
from typing import List
from ichatbio.agent_response import ResponseContext
from src.agent import GBIFAgent


class SimpleInMemoryContext(ResponseContext):
    """Simple in-memory context to collect messages"""
    def __init__(self):
        self.messages = []
        self.replies = []
    
    async def reply(self, message: str):
        self.replies.append(message)
        print(f"Reply: {message}")
    
    def begin_process(self, title: str):
        return SimpleProcess(title, self.messages)


class SimpleProcess:
    """Simple process to collect logs and artifacts"""
    def __init__(self, title: str, messages: List):
        self.title = title
        self.messages = messages
        print(f"Starting process: {title}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"Process failed: {exc_val}")
        else:
            print(f"Process completed: {self.title}")

    async def log(self, message: str, data=None):
        log_entry = {"message": message, "data": data}
        self.messages.append(log_entry)
        if data:
            print(f"Log: {message} | Data: {data}")
        else:
            print(f"Log: {message}")

    async def create_artifact(self, mimetype: str, description: str, uris=None, metadata=None):
        artifact = {
            "type": "artifact",
            "mimetype": mimetype,
            "description": description,
            "uris": uris,
            "metadata": metadata
        }
        self.messages.append(artifact)
        print(f"Artifact: {description}")
        if metadata:
            print(f"   Metadata: {metadata}")

Q1 = 'Who collected the oldest plant record in Palm Springs, California?'
Q2 = 'Find the records of Apis mellifera colleceted after 2020'
Q3 = 'Count the number of birds collected in the United States in 2024'
Q4 = "Count the records of Apis mellifera colleceted between yearly 2020 and 2024 in California state"
# ---- species queries ----
Q5 = 'Find oak species and related taxa'
Q6 = 'Find endangered cat species by rank, status and threat level'
Q7 = "Count endangered cat species by rank, status and threat level"

async def test_find_occurrence_records():
    context = SimpleInMemoryContext()
    agent = GBIFAgent()
    await agent.run(context=context, request=Q2, entrypoint="find_occurrence_records")


async def test_count_occurrence_records():
    context = SimpleInMemoryContext()
    agent = GBIFAgent()
    await agent.run(context=context, request=Q4, entrypoint="count_occurrence_records")


async def test_find_species_records():
    context = SimpleInMemoryContext()
    agent = GBIFAgent()
    await agent.run(context=context, request=Q6, entrypoint="find_species_records")


async def test_count_species_records():
    context = SimpleInMemoryContext()
    agent = GBIFAgent()
    await agent.run(context=context, request=Q7, entrypoint="count_species_records")


async def run_all_tests():
    try:
        await test_find_occurrence_records()
        await test_count_occurrence_records()
        await test_find_species_records()
        await test_count_species_records()

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
