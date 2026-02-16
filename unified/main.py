import sys
import os
import time
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.layout import Layout
from rich.live import Live

from unified.platform_adapters import PlatformFactory
from unified.autonomous_toolkit import autonomous_agent
from unified.document_generation import DocumentAgent
from unified.code_generator import CodeGenerator
from unified import workflow_example

console = Console()

class VermaSystem:
    def __init__(self):
        self.agent = autonomous_agent("antigravity")
        self.doc_agent = DocumentAgent()
        self.code_gen = CodeGenerator()

    def display_header(self):
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]MR.VERMA[/bold cyan] [dim]v5.0[/dim]\n"
            "[bold white]Autonomous AI System • Google Antigravity • Unified Core[/bold white]",
            border_style="cyan"
        ))

    def show_platform_status(self):
        table = Table(title="Platform Adapters Status")
        table.add_column("Platform", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        platforms = ["Antigravity", "OpenCode", "Quoder", "Trae", "Claude"]
        for p in platforms:
            adapter = PlatformFactory.get_adapter(p)
            status = adapter.get_status()
            status_str = "Active" if status.get("status") in ["active", "ready"] else "Inactive/Simulated"
            style = "green" if status_str == "Active" else "yellow"
            table.add_row(p, f"[{style}]{status_str}[/{style}]", str(status))

        console.print(table)
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def run_showcase(self):
        console.print("\n[bold blue]🚀 Launching Autonomous Startup Creator Showcase...[/bold blue]\n")
        workflow_example.run_integrated_workflow()
        Prompt.ask("\n[dim]Press Enter to return to menu...[/dim]")

    def feature_not_implemented(self):
        console.print("[yellow]Feature coming soon![/yellow]")
        time.sleep(1)

    def main_menu(self):
        while True:
            self.display_header()
            
            console.print("\n[bold]System Modules:[/bold]")
            console.print("1. [bold green]🚀 Launch Comprehensive Showcase[/bold green] (Startup Creator)")
            console.print("2. 📄 Document Generation Tools (Word, PPT, Excel)")
            console.print("3. 💻 Code Generation Tools (Fluid, Prisma, Telosys)")
            console.print("4. 🌐 Platform Status Check")
            console.print("5. ❌ Exit")

            choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5"], default="1")

            if choice == "1":
                self.run_showcase()
            elif choice == "2":
                self.doc_menu()
            elif choice == "3":
                self.code_menu()
            elif choice == "4":
                self.show_platform_status()
            elif choice == "5":
                console.print("[bold cyan]Shutting down MR.VERMA System...[/bold cyan]")
                sys.exit(0)

    def doc_menu(self):
        while True:
            console.clear()
            console.print(Panel("[bold]Document Generation Hub[/bold]", style="blue"))
            console.print("1. Generate Sample DOCX")
            console.print("2. Generate Sample PPTX")
            console.print("3. Generate Sample XLSX")
            console.print("4. Back to Main Menu")
            
            choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4"], default="4")
            
            if choice == "4":
                break
            
            filename = Prompt.ask("Enter output filename")
            
            if choice == "1":
                content = {"sections": [{"heading": "Sample Doc", "paragraphs": [{"text": "Generated from CLI"}]}]}
                res = self.doc_agent.create_document("docx", content, filename if filename.endswith(".docx") else f"{filename}.docx")
            elif choice == "2":
                content = [{"type": "title", "title": "Sample Pres"}, {"type": "content", "title": "Slide 1", "content": "Generated from CLI"}]
                res = self.doc_agent.create_document("pptx", content, filename if filename.endswith(".pptx") else f"{filename}.pptx")
            elif choice == "3":
                content = {"sheet_name": "Data", "rows": [["ID", "Value"], [1, "Test"]]}
                res = self.doc_agent.create_document("xlsx", content, filename if filename.endswith(".xlsx") else f"{filename}.xlsx")
                
            console.print(res)
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def code_menu(self):
        while True:
            console.clear()
            console.print(Panel("[bold]Code Generation Hub[/bold]", style="magenta"))
            console.print("1. Generate Fluid Template")
            console.print("2. Generate Prisma Schema")
            console.print("3. Generate Telosys Model")
            console.print("4. Back to Main Menu")
            
            choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4"], default="4")
            
            if choice == "4":
                break
            
            if choice == "1":
                tmpl = Prompt.ask("Enter template string (e.g. Hello {{ name }})")
                ctx_str = Prompt.ask("Enter context (key=value,key2=value2)")
                ctx = dict(item.split("=") for item in ctx_str.split(","))
                res = self.code_gen.generate("fluid", template=tmpl, context=ctx)
                console.print(Panel(res, title="Output"))
            elif choice == "2":
                console.print("[dim]Generating sample User schema...[/dim]")
                models = {"User": {"id": "Int @id", "email": "String"}}
                res = self.code_gen.generate("prisma", models=models)
                console.print(Panel(res, title="Output", style="dim"))
            elif choice == "3":
                console.print("[dim]Generating sample Entity model...[/dim]")
                res = self.code_gen.generate("telosys", model_name="User", entities={"User": {"id": "int"}})
                console.print(Panel(res, title="Output", style="dim"))
                
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

if __name__ == "__main__":
    system = VermaSystem()
    system.main_menu()
