import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rich.console import Console
console = Console()

def verify_system():
    console.print("[bold blue]Running MR.VERMA Integration Verification...[/bold blue]")
    
    try:
        from unified.document_generation import DocumentAgent
        from unified.vector_store import VectorStore
        from unified.template_engine import TemplateEngine
        
        console.print("[green]✓ Imports successful[/green]")
    except ImportError as e:
        console.print(f"[red]❌ Import failed: {e}[/red]")
        return
        
    # Initialize Agent
    try:
        agent = DocumentAgent()
        console.print("[green]✓ DocumentAgent initialized[/green]")
        
        caps = agent.get_capabilities()
        console.print(f"  Capabilities: {caps}")
        
        # Check Vector Store
        if agent.vector_store:
            console.print(f"[green]✓ Vector Store linked: {agent.vector_store.backend_type}[/green]")
            if agent.vector_store.backend_type == "milvus":
                 console.print(f"  [cyan]Using Milvus Backend[/cyan]")
        else:
            console.print("[yellow]⚠ Vector Store not linked (check dependencies)[/yellow]")
            
        # Check Template Engine
        if agent.template_engine:
            console.print(f"[green]✓ Template Engine linked[/green]")
        else:
            console.print("[yellow]⚠ Template Engine not linked[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Initialization failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return

    # Test Document Creation (Internal Mock or Real)
    try:
        # We'll try a simple DOCX if dependencies exist, otherwise skip
        if caps['libraries']['docx']:
            console.print("\n[blue]Testing Document Creation & Indexing...[/blue]")
            doc_content = {
                "sections": [{"heading": "Test Doc", "paragraphs": [{"text": "Hello World"}]}]
            }
            result = agent.create_document("docx", doc_content, "test_integration.docx")
            console.print(f"  Result: {result}")
            
            if "Indexed" in result:
                console.print("[green]✓ Auto-indexing triggered[/green]")
            else:
                console.print("[yellow]⚠ Auto-indexing not triggered (check vector store status)[/yellow]")
                
            # Cleanup
            if os.path.exists("output/documents/test_integration.docx"):
                os.remove("output/documents/test_integration.docx")
        else:
            console.print("[yellow]⚠ Skipping DOCX test (python-docx not installed)[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Document test failed: {e}[/red]")

    console.print("\n[bold green]Verification Complete![/bold green]")

if __name__ == "__main__":
    verify_system()
