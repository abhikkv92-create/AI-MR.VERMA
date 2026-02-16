import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unified.platform_adapters import PlatformFactory
from rich.console import Console

console = Console()

def verify_adapters():
    console.print("[bold blue]Verifying Platform Adapters...[/bold blue]")
    
    platforms = ["antigravity", "opencode", "quoder", "trae", "claude"]
    
    for p_name in platforms:
        console.print(f"\n[bold]Testing {p_name.capitalize()}...[/bold]")
        adapter = PlatformFactory.get_adapter(p_name)
        
        if adapter:
            status = adapter.get_status()
            console.print(f"  Status: {status}")
            
            # Simple execution test
            result = adapter.execute_task("Hello World Task")
            console.print(f"  Result: {result}")
        else:
            console.print(f"  [red]Failed to load adapter[/red]")

    console.print("\n[bold green]Adapter Verification Complete[/bold green]")

if __name__ == "__main__":
    verify_adapters()
