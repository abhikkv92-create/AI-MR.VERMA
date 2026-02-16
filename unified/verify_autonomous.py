import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unified.autonomous_toolkit import autonomous_agent
from rich.console import Console

console = Console()

def verify_autonomous():
    console.print("[bold blue]Verifying Autonomous Toolkit...[/bold blue]")

    try:
        # Create agent with default 'antigravity' adapter
        agent = autonomous_agent("antigravity")
        console.print("[green]✓ Autonomous Agent initialized[/green]")
        
        # Verify Tools
        tools = agent.registry.list_tools()
        console.print(f"  Registered Tools: {[t['name'] for t in tools]}")
        
        if "create_document" in [t['name'] for t in tools]:
             console.print("[green]✓ 'create_document' tool registered[/green]")
        else:
             console.print("[red]❌ 'create_document' tool missing[/red]")

        # Execute Goal
        console.print("\n[bold]Testing Goal Execution...[/bold]")
        result = agent.execute_goal("Research and create a report on AI trends")
        console.print(f"  Result:\n{result}")

    except Exception as e:
        console.print(f"[red]❌ Verification failed: {e}[/red]")
        import traceback
        traceback.print_exc()

    console.print("\n[bold green]Autonomous Verification Complete[/bold green]")

if __name__ == "__main__":
    verify_autonomous()
