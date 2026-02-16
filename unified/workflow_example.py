import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unified.autonomous_toolkit import autonomous_agent
from unified.code_generator import CodeGenerator
from rich.console import Console

console = Console()

def run_integrated_workflow():
    console.print("[bold blue]Starting Integrated Workflow: Startup Creator[/bold blue]")
    
    # 1. Initialize Autonomous Agent
    agent = autonomous_agent("antigravity")
    console.print("[green]1. Agent Initialized[/green]")
    
    # 2. Define Startup Idea
    startup_name = "QuickDeliver"
    startup_description = "AI-powered drone delivery service."
    console.print(f"[cyan]2. Startup Defined: {startup_name}[/cyan]")
    
    # 3. Code Generation (Schema)
    code_gen = CodeGenerator()
    console.print("[cyan]3. Generating Database Schema (Prisma)...[/cyan]")
    
    schema_models = {
        "User": {
            "id": "Int @id @default(autoincrement())",
            "email": "String @unique",
            "role": "String @default(\"customer\")"
        },
        "Order": {
            "id": "Int @id @default(autoincrement())",
            "status": "String",
            "droneId": "Int?"
        }
    }
    prisma_schema = code_gen.generate("prisma", models=schema_models)
    console.print(f"[dim]{prisma_schema}[/dim]")
    
    # 4. Code Generation (Landing Page)
    console.print("[cyan]4. Generating Landing Page (Fluid)...[/cyan]")
    fluid_tmpl = "Welcome to {{ name }}! We offer {{ desc }}."
    landing_page = code_gen.generate("fluid", template=fluid_tmpl, context={"name": startup_name, "desc": startup_description})
    console.print(f"  > {landing_page}")
    
    # 5. Document Generation (Pitch Deck)
    console.print("[cyan]5. Generating Pitch Deck (PPTX)...[/cyan]")
    slides = [
        {"type": "title", "title": f"{startup_name} Pitch Deck"},
        {"type": "content", "title": "Problem", "content": "Delivery is slow and expensive."},
        {"type": "content", "title": "Solution", "content": "Autonomous drones.", "bullets": ["Fast", "Cheap", "Green"]}
    ]
    # Use agent's registered tool
    pptx_result = agent.registry.invoke_tool("create_document", doc_type="pptx", content=slides, filename="quickdeliver_pitch.pptx")
    console.print(f"  {pptx_result}")
    
    # 6. Document Generation (Technical Report)
    console.print("[cyan]6. Generating Technical Report (DOCX)...[/cyan]")
    report_content = {
        "sections": [
            {"heading": f"Technical Spec: {startup_name}", "level": 1},
            {"heading": "Architecture", "level": 2, "paragraphs": [{"text": "Microservices based architecture using Prisma and Fluid."}]},
            {"heading": "Database Schema", "level": 2, "paragraphs": [{"text": "See prisma schema above.", "italic": True}]}
        ]
    }
    docx_result = agent.registry.invoke_tool("create_document", doc_type="docx", content=report_content, filename="quickdeliver_tech_spec.docx")
    console.print(f"  {docx_result}")
    
    console.print("\n[bold green]Integrated Workflow Complete![/bold green]")
    console.print(f"Artifacts generated in: output/documents/")

if __name__ == "__main__":
    run_integrated_workflow()
