import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unified.document_generation import DocumentAgent
from unified.code_generator import CodeGenerator
from rich.console import Console

console = Console()

def verify_generation():
    console.print("[bold blue]Verifying Enhanced Generation...[/bold blue]")
    
    # 1. Document Generation
    doc_agent = DocumentAgent()
    
    # PPTX
    slides = [
        {"type": "title", "title": "Verification Presentation"},
        {"type": "content", "title": "Features", "bullets": ["Fluid Support", "Prisma Support", "Enhanced PPTX"]}
    ]
    res_pptx = doc_agent.create_document("pptx", slides, "verify_slides.pptx")
    console.print(f"PPTX Result: {res_pptx}")

    # 2. Code Generation
    code_gen = CodeGenerator()
    
    # Fluid
    fluid_tmpl = "Hello {{ name }}! Welcome to {{ app }}."
    res_fluid = code_gen.generate("fluid", template=fluid_tmpl, context={"name": "Abhinav", "app": "MR.VERMA"})
    console.print(f"Fluid Result: {res_fluid}")
    
    # Prisma
    prisma_models = {
        "User": {
            "id": "Int @id @default(autoincrement())",
            "email": "String @unique",
            "name": "String?"
        }
    }
    res_prisma = code_gen.generate("prisma", models=prisma_models)
    console.print(f"Prisma Result:\n{res_prisma}")

    console.print("[bold green]Generation Verification Complete[/bold green]")

if __name__ == "__main__":
    verify_generation()
