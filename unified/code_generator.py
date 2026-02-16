import os
import subprocess
from typing import Dict, Any, List, Optional
from rich.console import Console

console = Console()

class FluidGenerator:
    """Generator for Fluid Templates (.NET)"""
    
    def generate(self, template: str, context: Dict[str, Any]) -> str:
        """
        Generate content using Fluid template.
        Note: Since Fluid is a .NET library, we simulate or wrap a CLI.
        For this python implementation, we will simulate the output for the user guide.
        """
        console.print("[cyan]Generating Key-Value Fluid Template (Simulation)...[/cyan]")
        
        # Simple string replacement simulation of Fluid behavior
        output = template
        for key, value in context.items():
            placeholder = f"{{{{ {key} }}}}"
            output = output.replace(placeholder, str(value))
            # Handle standard {{key}} as well
            output = output.replace(f"{{{{{key}}}}}", str(value))
            
        return output

class PrismaGenerator:
    """Generator for Prisma Schemas"""
    
    def generate_schema(self, models: Dict[str, Dict[str, Any]], datasource_provider: str = "sqlite", url: str = "file:./dev.db") -> str:
        """
        Generate a schema.prisma file content from dictionary definition.
        
        Args:
            models: Dict of model_name -> {field_name: type_def}
        """
        lines = []
        
        # Datasource and Generator
        lines.append(f'datasource db {{\n  provider = "{datasource_provider}"\n  url      = "{url}"\n}}\n')
        lines.append('generator client {\n  provider = "prisma-client-js"\n}\n')
        
        # Models
        for model_name, fields in models.items():
            lines.append(f"model {model_name} {{")
            for field, type_def in fields.items():
                if isinstance(type_def, str):
                    lines.append(f"  {field} {type_def}")
                elif isinstance(type_def, dict):
                    # Handle advanced field defs if needed (mocked for now)
                    t = type_def.get("type", "String")
                    attrs = type_def.get("attributes", "")
                    lines.append(f"  {field} {t} {attrs}")
            lines.append("}\n")
            
        return "\n".join(lines)

class TelosysGenerator:
    """Generator for Telosys (Java)"""
    
    def __init__(self, telosys_path: str = None):
        self.telosys_path = telosys_path or os.getenv("TELOSYS_PATH")

    def generate_model(self, model_name: str, entities: Dict) -> str:
        """
        Generate a Telosys model file (.entity)
        """
        console.print(f"[magenta]Generating Telosys Model: {model_name}...[/magenta]")
        lines = []
        lines.append(f"// Telosys Model for {model_name}")
        
        for entity_name, fields in entities.items():
             lines.append(f"{entity_name} {{")
             for field, type_def in fields.items():
                 lines.append(f"  {field} : {type_def} ;")
             lines.append("}")
             
        return "\n".join(lines)

class CodeGenerator:
    """Unified Code Generator"""
    
    def __init__(self):
        self.fluid = FluidGenerator()
        self.prisma = PrismaGenerator()
        self.telosys = TelosysGenerator()

    def generate(self, tool: str, **kwargs) -> str:
        if tool == "fluid":
            return self.fluid.generate(kwargs.get("template", ""), kwargs.get("context", {}))
        elif tool == "prisma":
            return self.prisma.generate_schema(kwargs.get("models", {}))
        elif tool == "telosys":
            return self.telosys.generate_model(kwargs.get("model_name", "MyModel"), kwargs.get("entities", {}))
        else:
            return f"❌ Unknown tool: {tool}"
