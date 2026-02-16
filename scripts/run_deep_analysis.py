
import sys
import os
import asyncio
import json
import logging

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.intelligence_cluster import ResearchAnalyst, DataScientist
from agents.platform_cluster import SecurityArchitect

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DeepScan")

async def run_deep_scan():
    logger.info("Initializing Deep System Analysis...")
    
    target_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    task_payload = {"target_dir": target_dir}
    
    agents = [ResearchAnalyst(), DataScientist(), SecurityArchitect()]
    tasks = []
    
    for agent in agents:
        agent.start()
        tasks.append(agent.process_task(task_payload))
        
    logger.info(f"Scanning directory: {target_dir}")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    analysis_report = {
        "timestamp": "2026-02-13",
        "scanned_dir": target_dir,
        "findings": []
    }
    
    for i, res in enumerate(results):
        agent_name = agents[i].name
        if isinstance(res, Exception):
            logger.error(f"{agent_name} Failed: {res}")
            analysis_report["findings"].append({agent_name: {"error": str(res)}})
        else:
            logger.info(f"{agent_name} Finished.")
            analysis_report["findings"].append({agent_name: res})
            
    # Save Report
    logs_dir = os.path.join(target_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    report_path = os.path.join(logs_dir, "comprehensive_analysis.json")
    
    with open(report_path, "w") as f:
        json.dump(analysis_report, f, indent=2)
        
    logger.info(f"Analysis Report saved to {report_path}")
    
    # Generate Evolution Roadmap based on findings
    roadmap_path = os.path.join(logs_dir, "evolution_roadmap.md")
    with open(roadmap_path, "w") as f:
        f.write("# Production & Evolution Roadmap\n\n")
        f.write("Based on Deep System Analysis\n\n")
        
        for finding in analysis_report["findings"]:
            for agent, data in finding.items():
                f.write(f"## Finding from {agent}\n")
                f.write(f"```json\n{json.dumps(data, indent=2)}\n```\n\n")

if __name__ == "__main__":
    asyncio.run(run_deep_scan())
