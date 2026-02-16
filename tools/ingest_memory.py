
import os
import sys
import re
import asyncio
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.memory_service import memory_service

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Tools.Ingest")

def redact_secrets(text: str) -> str:
    """Redacts common secret patterns (API keys, etc.) from text."""
    # General API keys (High entropy strings usually followed by = or :)
    patterns = [
        r'(?i)(api_key|secret|token|password|auth|key)["\s:=]+[a-z0-9_\-\.]{16,}',
        r'nvapi-[a-z0-9_\-]{32,}', # NVIDIA specifically
        r'sk-[a-z0-9]{32,}',     # OpenAI
        r'ghp_[a-zA-Z0-9]{36}',   # GitHub
    ]
    redacted = text
    for pattern in patterns:
        redacted = re.sub(pattern, "[REDACTED_SECRET]", redacted)
    return redacted

async def ingest_file(filepath: str):
    """Reads a file and stores its content in Milvus."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if not content.strip():
            return
            
        # Security Filter: Redact secrets before vectorization
        content = redact_secrets(content)
        
        logger.info(f"Ingesting: {filepath}")
        
        # Simple Chunking (split by headers or max length)
        # For now, we'll store the whole file if small, or split by 2000 chars
        chunks = [content[i:i+2000] for i in range(0, len(content), 2000)]
        
        for i, chunk in enumerate(chunks):
            metadata = {
                "source": filepath,
                "type": "markdown",
                "chunk_id": i,
                "total_chunks": len(chunks),
                "filename": os.path.basename(filepath)
            }
            success = await memory_service.store(chunk, metadata)
            if success:
                logger.info(f"Successfully ingested chunk {i+1}/{len(chunks)} of {os.path.basename(filepath)}")
            else:
                logger.error(f"Failed to ingest chunk {i+1} of {filepath}")
                
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")

async def ingest_directory(directory: str):
    """Recursively ingests all markdown files in a directory."""
    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return
        
    tasks = []
    for root, dirs, files in os.walk(directory):
        # Skip .git and node_modules
        if '.git' in root or 'node_modules' in root:
            continue
            
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                tasks.append(ingest_file(filepath))
                
    if tasks:
        await asyncio.gather(*tasks)
        logger.info(f"Ingested {len(tasks)} files from {directory}")

async def main():
    # 1. Connect to Milvus
    if not memory_service.connect():
        logger.error("Could not connect to Milvus. Exiting.")
        return
        
    # 2. Ingest Brain directory
    brain_dir = os.environ.get("BRAIN_DIR", r"C:\Users\Abbyk\.gemini\antigravity\brain\554b04c8-e197-4ac0-aae4-ccf15822d7f3")
    logger.info(f"Starting ingestion from brain: {brain_dir}")
    await ingest_directory(brain_dir)
    
    # 3. Ingest Workspace Documentation
    logger.info("Starting ingestion from workspace docs...")
    await ingest_file(r"e:\ABHINAV\MR.VERMA\logs\development_roadmap.md")
    
    logger.info("Ingestion complete.")

if __name__ == "__main__":
    asyncio.run(main())
