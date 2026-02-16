"""
MR.VERMA Unified Template Engine

A comprehensive multi-engine templating system supporting:
- Jinja2 (primary Python templating)
- Mako (alternative)
- Fluid (.NET bridge)
- Telosys (Java bridge)

Provides code generation features with built-in templates and rich console output.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()


class TemplateEngineType(Enum):
    """Supported template engine types."""

    JINJA2 = auto()
    MAKO = auto()
    FLUID = auto()
    TELOSYS = auto()


class TemplateEngineError(Exception):
    """Base exception for template engine errors."""

    pass


class EngineNotAvailableError(TemplateEngineError):
    """Raised when a template engine is not available."""

    pass


class TemplateRenderError(TemplateEngineError):
    """Raised when template rendering fails."""

    pass


@dataclass
class TemplateResult:
    """Result of a template rendering operation."""

    content: str
    engine: TemplateEngineType
    success: bool
    metadata: Dict[str, Any]
    errors: List[str]


@dataclass
class BuiltInTemplate:
    """Built-in template definition."""

    name: str
    description: str
    template: str
    engine: TemplateEngineType
    context_schema: Dict[str, Any]


class TemplateEngine:
    """
    Multi-engine template processor for MR.VERMA.

    Supports Jinja2 (primary), Mako (alternative), Fluid (.NET), and Telosys (Java).
    Provides code generation capabilities with built-in templates and subprocess bridges.

    Examples:
        >>> engine = TemplateEngine()
        >>> result = engine.render_template(
        ...     "Hello {{ name }}!",
        ...     {"name": "World"},
        ...     engine_type=TemplateEngineType.JINJA2
        ... )
        >>> print(result.content)
        Hello World!

    Attributes:
        templates_dir: Directory for custom templates discovery
        fallback_engine: Default engine to use when primary fails
        verbose: Enable verbose output
    """

    def __init__(
        self,
        templates_dir: Optional[Union[str, Path]] = None,
        fallback_engine: TemplateEngineType = TemplateEngineType.JINJA2,
        verbose: bool = False,
    ) -> None:
        """
        Initialize the Template Engine.

        Args:
            templates_dir: Directory containing custom templates
            fallback_engine: Engine to fall back to if primary fails
            verbose: Enable detailed console output
        """
        self.templates_dir = Path(templates_dir) if templates_dir else Path("templates")
        self.fallback_engine = fallback_engine
        self.verbose = verbose

        self._engines: Dict[TemplateEngineType, bool] = {}
        self._jinja_env = None
        self._mako_lookup = None
        self._built_in_templates: Dict[str, BuiltInTemplate] = {}

        self._detect_engines()
        self._register_built_in_templates()

        if self.verbose:
            console.print("[bold green]✓[/bold green] Template Engine initialized")

    def _detect_engines(self) -> None:
        """Detect available template engines."""
        # Check Jinja2
        try:
            import jinja2

            self._engines[TemplateEngineType.JINJA2] = True
            self._init_jinja()
            if self.verbose:
                console.print("[blue]•[/blue] Jinja2 available")
        except ImportError:
            self._engines[TemplateEngineType.JINJA2] = False
            console.print(
                "[yellow]⚠[/yellow] Jinja2 not installed (pip install jinja2)"
            )

        # Check Mako
        try:
            import mako

            self._engines[TemplateEngineType.MAKO] = True
            self._init_mako()
            if self.verbose:
                console.print("[blue]•[/blue] Mako available")
        except ImportError:
            self._engines[TemplateEngineType.MAKO] = False
            if self.verbose:
                console.print(
                    "[yellow]⚠[/yellow] Mako not installed (pip install mako)"
                )

        # Check Fluid (.NET CLI)
        self._engines[TemplateEngineType.FLUID] = self._check_fluid()
        if self.verbose and self._engines[TemplateEngineType.FLUID]:
            console.print("[blue]•[/blue] Fluid (.NET) available")
        elif self.verbose:
            console.print(
                "[yellow]⚠[/yellow] Fluid not available (dotnet tool install --global fluid)"
            )

        # Check Telosys (Java CLI)
        self._engines[TemplateEngineType.TELOSYS] = self._check_telosys()
        if self.verbose and self._engines[TemplateEngineType.TELOSYS]:
            console.print("[blue]•[/blue] Telosys (Java) available")
        elif self.verbose:
            console.print(
                "[yellow]⚠[/yellow] Telosys not available (install from telosys.org)"
            )

    def _init_jinja(self) -> None:
        """Initialize Jinja2 environment."""
        from jinja2 import Environment, FileSystemLoader, PackageLoader

        loaders = []

        # Add filesystem loader if templates directory exists
        if self.templates_dir.exists():
            loaders.append(FileSystemLoader(str(self.templates_dir)))

        # Create environment with custom filters
        self._jinja_env = Environment(
            loader=loaders[0] if loaders else None,
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols"],
        )

        # Register built-in filters
        self._register_jinja_filters()
        self._register_jinja_globals()

    def _register_jinja_filters(self) -> None:
        """Register custom Jinja2 filters."""
        if self._jinja_env:
            self._jinja_env.filters.update(
                {
                    "camelcase": lambda s: "".join(
                        word.capitalize() for word in s.split("_")
                    ),
                    "snakecase": lambda s: "".join(
                        ["_" + c.lower() if c.isupper() else c for c in s]
                    ).lstrip("_"),
                    "pascalcase": lambda s: "".join(
                        word.capitalize() for word in s.split("_")
                    ),
                    "kebabcase": lambda s: s.replace("_", "-").lower(),
                    "constantcase": lambda s: s.upper().replace("-", "_"),
                    "pluralize": self._pluralize,
                    "singularize": self._singularize,
                    "comment": lambda s, lang="python": self._format_comment(s, lang),
                    "indent_code": lambda s, level=1: self._indent_code(s, level),
                }
            )

    def _register_jinja_globals(self) -> None:
        """Register custom Jinja2 globals."""
        if self._jinja_env:
            self._jinja_env.globals.update(
                {
                    "now": self._get_timestamp,
                    "uuid": self._generate_uuid,
                    "env": os.environ.get,
                    "random_string": self._random_string,
                }
            )

    def _init_mako(self) -> None:
        """Initialize Mako template lookup."""
        from mako.lookup import TemplateLookup

        if self.templates_dir.exists():
            self._mako_lookup = TemplateLookup(
                directories=[str(self.templates_dir)],
                module_directory=os.path.join(tempfile.gettempdir(), "mako_modules"),
                collection_size=500,
            )

    def _check_fluid(self) -> bool:
        """Check if Fluid CLI is available."""
        try:
            result = subprocess.run(
                ["fluid", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_telosys(self) -> bool:
        """Check if Telosys CLI is available."""
        try:
            result = subprocess.run(
                ["telosys", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _register_built_in_templates(self) -> None:
        """Register built-in code generation templates."""
        self._built_in_templates = {
            "python_class": BuiltInTemplate(
                name="python_class",
                description="Generate a Python class with type hints",
                template='''class {{ class_name }}:
    """{{ description | default('') }}"""
    
    def __init__(self{% for param in params %}, {{ param.name }}: {{ param.type | default('Any') }}{% if param.default is defined %} = {{ param.default }}{% endif %}{% endfor %}):
        """Initialize {{ class_name }}."""
        {% for param in params %}
        self.{{ param.name }} = {{ param.name }}
        {% endfor %}
    {% if methods %}
    {% for method in methods %}
    def {{ method.name }}(self{% for param in method.params %}, {{ param.name }}: {{ param.type | default('Any') }}{% endfor %}){% if method.return_type %} -> {{ method.return_type }}{% endif %}:
        """{{ method.docstring | default(method.name + ' method') }}."""
        {% if method.implementation %}
        {{ method.implementation | indent_code(2) }}
        {% else %}
        pass
        {% endif %}
    {% endfor %}
    {% endif %}''',
                engine=TemplateEngineType.JINJA2,
                context_schema={"class_name": str, "params": list, "methods": list},
            ),
            "python_api_endpoint": BuiltInTemplate(
                name="python_api_endpoint",
                description="Generate FastAPI endpoint",
                template='''from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

router = APIRouter(prefix="/{{ prefix }}", tags=["{{ tag }}"])

{% for endpoint in endpoints %}
@router.{{ endpoint.method }}("{{ endpoint.path }}")
async def {{ endpoint.name }}({% for param in endpoint.params %}{{ param.name }}: {{ param.type }}{% if not loop.last %}, {% endif %}{% endfor %}):
    """
    {{ endpoint.description | default('Endpoint') }}
    """
    try:
        {% if endpoint.implementation %}
        {{ endpoint.implementation | indent_code(2) }}
        {% else %}
        # TODO: Implement endpoint logic
        return {"message": "{{ endpoint.name }} executed"}
        {% endif %}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

{% endfor %}''',
                engine=TemplateEngineType.JINJA2,
                context_schema={"prefix": str, "tag": str, "endpoints": list},
            ),
            "react_component": BuiltInTemplate(
                name="react_component",
                description="Generate React functional component",
                template="""import React{% if hooks %}, { {% for hook in hooks %}{{ hook }}{% if not loop.last %}, {% endif %}{% endfor %} }{% endif %} from 'react';
{% if imports %}
{% for imp in imports %}
import {{ imp.name }} from '{{ imp.path }}';
{% endfor %}
{% endif %}

interface {{ component_name }}Props {
    {% for prop in props %}
    {{ prop.name }}{% if prop.optional %}?{% endif %}: {{ prop.type }};
    {% endfor %}
}

export const {{ component_name }}: React.FC<{{ component_name }}Props> = ({ {% for prop in props %}{{ prop.name }}{% if prop.default %} = {{ prop.default }}{% endif %}{% if not loop.last %}, {% endif %}{% endfor %} }) => {
    {% if state_vars %}
    {% for state in state_vars %}
    const [{{ state.name }}, set{{ state.name | pascalcase }}] = useState<{{ state.type }}>({{ state.initial }});
    {% endfor %}
    {% endif %}
    
    {% if effects %}
    {% for effect in effects %}
    useEffect(() => {
        {{ effect.implementation | indent_code(2) }}
    }, [{% for dep in effect.deps %}{{ dep }}{% if not loop.last %}, {% endif %}{% endfor %}]);
    {% endfor %}
    {% endif %}
    
    return (
        <div className="{{ component_name | kebabcase }}">
            {{ jsx_content | default('// Component content') | indent_code(3) }}
        </div>
    );
};

export default {{ component_name }};""",
                engine=TemplateEngineType.JINJA2,
                context_schema={"component_name": str, "props": list, "hooks": list},
            ),
            "vue_component": BuiltInTemplate(
                name="vue_component",
                description="Generate Vue 3 component",
                template="""<template>
  <div class="{{ component_name | kebabcase }}">
    {{ template_content | default('<!-- Component content -->') }}
  </div>
</template>

<script setup lang="ts">
{% if imports %}
{% for imp in imports %}
import {{ imp.name }} from '{{ imp.path }}';
{% endfor %}
{% endif %}

interface Props {
  {% for prop in props %}
  {{ prop.name }}{% if prop.optional %}?{% endif %}: {{ prop.type }};
  {% endfor %}
}

const props = defineProps<Props>();

{% if emits %}
const emit = defineEmits<{
  {% for emit in emits %}
  (e: '{{ emit.name }}'{% if emit.payload %}, payload: {{ emit.payload }}{% endif %}): void;
  {% endfor %}
}>();
{% endif %}

{% if reactive_vars %}
{% for var in reactive_vars %}
const {{ var.name }} = ref<{{ var.type }}>({{ var.initial }});
{% endfor %}
{% endif %}

{% if methods %}
{% for method in methods %}
const {{ method.name }} = ({% for param in method.params %}{{ param.name }}: {{ param.type }}{% if not loop.last %}, {% endif %}{% endfor %}) => {
  {{ method.implementation | indent_code(1) }}
};
{% endfor %}
{% endif %}
</script>

<style scoped>
.{{ component_name | kebabcase }} {
  {{ styles | default('/* Component styles */') | indent_code(1) }}
}
</style>""",
                engine=TemplateEngineType.JINJA2,
                context_schema={"component_name": str, "props": list, "emits": list},
            ),
            "sqlalchemy_model": BuiltInTemplate(
                name="sqlalchemy_model",
                description="Generate SQLAlchemy database model",
                template='''from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text{% if relationships %}, relationship{% endif %}
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class {{ class_name }}(Base):
    """{{ description | default(class_name + ' model') }}"""
    
    __tablename__ = '{{ table_name | default(class_name | snakecase) }}'
    
    id = Column(Integer, primary_key=True, index=True)
    {% for field in fields %}
    {{ field.name }} = Column({{ field.type | default('String') }}{% if field.length %}(length={{ field.length }}){% endif %}{% if field.nullable %}, nullable=True{% endif %}{% if field.unique %}, unique=True{% endif %}{% if field.index %}, index=True{% endif %})
    {% endfor %}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    {% if relationships %}
    
    {% for rel in relationships %}
    {{ rel.name }} = relationship("{{ rel.target }}", back_populates="{{ rel.back_populates }}")
    {% endfor %}
    {% endif %}
    
    def __repr__(self):
        return f"<{{ class_name }}(id={self.id})>"''',
                engine=TemplateEngineType.JINJA2,
                context_schema={"class_name": str, "fields": list, "table_name": str},
            ),
            "django_model": BuiltInTemplate(
                name="django_model",
                description="Generate Django ORM model",
                template='''from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class {{ class_name }}(models.Model):
    """{{ description | default(class_name + ' model') }}"""
    
    {% for field in fields %}
    {{ field.name }} = models.{{ field.type | default('CharField') }}(
        {% if field.type == 'CharField' %}max_length={{ field.max_length | default(255) }}{% endif %}
        {% if field.nullable %}, null=True, blank=True{% endif %}
        {% if field.default %}, default={{ field.default }}{% endif %}
        {% if field.choices %}, choices={{ field.choices }}{% endif %}
    )
    {% endfor %}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    {% if meta %}
    class Meta:
        {% if meta.verbose_name %}verbose_name = "{{ meta.verbose_name }}"{% endif %}
        {% if meta.verbose_name_plural %}verbose_name_plural = "{{ meta.verbose_name_plural }}"{% endif %}
        {% if meta.ordering %}ordering = {{ meta.ordering }}{% endif %}
        {% if meta.db_table %}db_table = "{{ meta.db_table }}"{% endif %}
    {% endif %}
    
    def __str__(self):
        return str(self.{% if str_field %}{{ str_field }}{% else %}id{% endif %})
    
    {% if methods %}
    {% for method in methods %}
    def {{ method.name }}(self{% for param in method.params %}, {{ param.name }}{% endfor %}):
        """{{ method.docstring | default(method.name) }}."""
        {% if method.implementation %}
        {{ method.implementation | indent_code(1) }}
        {% else %}
        pass
        {% endif %}
    {% endfor %}
    {% endif %}''',
                engine=TemplateEngineType.JINJA2,
                context_schema={"class_name": str, "fields": list, "meta": dict},
            ),
        }

    # Utility methods for filters
    def _pluralize(self, word: str) -> str:
        """Simple pluralization."""
        if word.endswith("y"):
            return word[:-1] + "ies"
        elif word.endswith(("s", "sh", "ch", "x", "z")):
            return word + "es"
        else:
            return word + "s"

    def _singularize(self, word: str) -> str:
        """Simple singularization."""
        if word.endswith("ies"):
            return word[:-3] + "y"
        elif word.endswith("es") and word[-3] in ("s", "h", "c", "x", "z"):
            return word[:-2]
        elif word.endswith("s") and not word.endswith("ss"):
            return word[:-1]
        return word

    def _format_comment(self, text: str, lang: str = "python") -> str:
        """Format text as a comment."""
        if lang in ("python", "ruby", "yaml"):
            return "\n".join(f"# {line}" for line in text.split("\n"))
        elif lang in ("javascript", "typescript", "java", "c", "cpp", "go"):
            return "\n".join(f"// {line}" for line in text.split("\n"))
        elif lang == "html":
            return f"<!-- {text} -->"
        else:
            return f"# {text}"

    def _indent_code(self, code: str, level: int = 1) -> str:
        """Indent code by specified level."""
        indent = "    " * level
        return "\n".join(
            indent + line if line.strip() else line for line in code.split("\n")
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().isoformat()

    def _generate_uuid(self) -> str:
        """Generate a UUID."""
        import uuid

        return str(uuid.uuid4())

    def _random_string(self, length: int = 10) -> str:
        """Generate random string."""
        import random
        import string

        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def is_engine_available(self, engine_type: TemplateEngineType) -> bool:
        """
        Check if a template engine is available.

        Args:
            engine_type: The engine type to check

        Returns:
            True if engine is available, False otherwise
        """
        return self._engines.get(engine_type, False)

    def list_available_engines(self) -> List[TemplateEngineType]:
        """
        List all available template engines.

        Returns:
            List of available engine types
        """
        return [engine for engine, available in self._engines.items() if available]

    def render_template(
        self,
        template_string: str,
        context: Dict[str, Any],
        engine_type: TemplateEngineType = TemplateEngineType.JINJA2,
    ) -> TemplateResult:
        """
        Render a template string with the specified context.

        Args:
            template_string: The template content to render
            context: Dictionary of variables to substitute
            engine_type: Which template engine to use

        Returns:
            TemplateResult containing rendered content and metadata

        Raises:
            EngineNotAvailableError: If specified engine is not available
            TemplateRenderError: If rendering fails

        Examples:
            >>> engine = TemplateEngine()
            >>> result = engine.render_template(
            ...     "Hello {{ name }}!",
            ...     {"name": "World"}
            ... )
            >>> print(result.content)
            Hello World!
        """
        if not self.is_engine_available(engine_type):
            # Try fallback
            if engine_type != self.fallback_engine and self.is_engine_available(
                self.fallback_engine
            ):
                console.print(
                    f"[yellow]⚠[/yellow] {engine_type.name} not available, falling back to {self.fallback_engine.name}"
                )
                engine_type = self.fallback_engine
            else:
                raise EngineNotAvailableError(
                    f"Engine {engine_type.name} is not available"
                )

        try:
            if engine_type == TemplateEngineType.JINJA2:
                return self._render_jinja_string(template_string, context)
            elif engine_type == TemplateEngineType.MAKO:
                return self._render_mako_string(template_string, context)
            elif engine_type == TemplateEngineType.FLUID:
                return self._render_fluid_string(template_string, context)
            else:
                raise TemplateRenderError(
                    f"String rendering not supported for {engine_type.name}"
                )

        except Exception as e:
            raise TemplateRenderError(f"Failed to render template: {str(e)}")

    def render_file(
        self,
        template_path: Union[str, Path],
        context: Dict[str, Any],
        engine_type: TemplateEngineType = TemplateEngineType.JINJA2,
    ) -> TemplateResult:
        """
        Render a template file with the specified context.

        Args:
            template_path: Path to the template file
            context: Dictionary of variables to substitute
            engine_type: Which template engine to use

        Returns:
            TemplateResult containing rendered content and metadata

        Raises:
            EngineNotAvailableError: If specified engine is not available
            FileNotFoundError: If template file doesn't exist
            TemplateRenderError: If rendering fails
        """
        if not self.is_engine_available(engine_type):
            if engine_type != self.fallback_engine and self.is_engine_available(
                self.fallback_engine
            ):
                console.print(
                    f"[yellow]⚠[/yellow] {engine_type.name} not available, falling back to {self.fallback_engine.name}"
                )
                engine_type = self.fallback_engine
            else:
                raise EngineNotAvailableError(
                    f"Engine {engine_type.name} is not available"
                )

        template_path = Path(template_path)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        try:
            if engine_type == TemplateEngineType.JINJA2:
                return self._render_jinja_file(template_path, context)
            elif engine_type == TemplateEngineType.MAKO:
                return self._render_mako_file(template_path, context)
            elif engine_type == TemplateEngineType.FLUID:
                return self._render_fluid_file(template_path, context)
            elif engine_type == TemplateEngineType.TELOSYS:
                return self._render_telosys_file(template_path, context)
            else:
                raise TemplateRenderError(f"Unknown engine type: {engine_type}")

        except Exception as e:
            raise TemplateRenderError(f"Failed to render template file: {str(e)}")

    def _render_jinja_string(
        self, template_string: str, context: Dict[str, Any]
    ) -> TemplateResult:
        """Render using Jinja2 from string."""
        from jinja2 import Template

        template = Template(template_string)

        # Add custom filters
        template.environment.filters.update(
            self._jinja_env.filters if self._jinja_env else {}
        )
        template.environment.globals.update(
            self._jinja_env.globals if self._jinja_env else {}
        )

        rendered = template.render(**context)

        return TemplateResult(
            content=rendered,
            engine=TemplateEngineType.JINJA2,
            success=True,
            metadata={"source": "string", "engine_version": "3.x"},
            errors=[],
        )

    def _render_jinja_file(
        self, template_path: Path, context: Dict[str, Any]
    ) -> TemplateResult:
        """Render using Jinja2 from file."""
        if self._jinja_env is None:
            from jinja2 import Environment

            self._jinja_env = Environment()
            self._register_jinja_filters()
            self._register_jinja_globals()

        template = self._jinja_env.get_template(template_path.name)
        rendered = template.render(**context)

        return TemplateResult(
            content=rendered,
            engine=TemplateEngineType.JINJA2,
            success=True,
            metadata={"source": str(template_path), "engine_version": "3.x"},
            errors=[],
        )

    def _render_mako_string(
        self, template_string: str, context: Dict[str, Any]
    ) -> TemplateResult:
        """Render using Mako from string."""
        from mako.template import Template

        template = Template(template_string)
        rendered = template.render(**context)

        return TemplateResult(
            content=rendered,
            engine=TemplateEngineType.MAKO,
            success=True,
            metadata={"source": "string", "engine_version": "1.x"},
            errors=[],
        )

    def _render_mako_file(
        self, template_path: Path, context: Dict[str, Any]
    ) -> TemplateResult:
        """Render using Mako from file."""
        from mako.template import Template

        template = Template(filename=str(template_path))
        rendered = template.render(**context)

        return TemplateResult(
            content=rendered,
            engine=TemplateEngineType.MAKO,
            success=True,
            metadata={"source": str(template_path), "engine_version": "1.x"},
            errors=[],
        )

    def _render_fluid_string(
        self, template_string: str, context: Dict[str, Any]
    ) -> TemplateResult:
        """
        Render using Fluid (.NET) from string.

        Falls back to Jinja2 if Fluid is not available.
        """
        if not self.is_engine_available(TemplateEngineType.FLUID):
            console.print(
                "[yellow]⚠[/yellow] Fluid not available, falling back to Jinja2"
            )
            return self._render_jinja_string(template_string, context)

        # Create temporary files for Fluid
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".liquid", delete=False
        ) as tmpl_file:
            tmpl_file.write(template_string)
            tmpl_path = tmpl_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as data_file:
            json.dump(context, data_file)
            data_path = data_file.name

        try:
            result = subprocess.run(
                ["fluid", "render", tmpl_path, data_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise TemplateRenderError(f"Fluid error: {result.stderr}")

            return TemplateResult(
                content=result.stdout,
                engine=TemplateEngineType.FLUID,
                success=True,
                metadata={"source": "string", "engine": "Fluid (.NET)"},
                errors=[],
            )
        finally:
            os.unlink(tmpl_path)
            os.unlink(data_path)

    def _render_fluid_file(
        self, template_path: Path, context: Dict[str, Any]
    ) -> TemplateResult:
        """Render using Fluid (.NET) from file."""
        if not self.is_engine_available(TemplateEngineType.FLUID):
            console.print(
                "[yellow]⚠[/yellow] Fluid not available, falling back to Jinja2"
            )
            return self._render_jinja_file(template_path, context)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as data_file:
            json.dump(context, data_file)
            data_path = data_file.name

        try:
            result = subprocess.run(
                ["fluid", "render", str(template_path), data_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise TemplateRenderError(f"Fluid error: {result.stderr}")

            return TemplateResult(
                content=result.stdout,
                engine=TemplateEngineType.FLUID,
                success=True,
                metadata={"source": str(template_path), "engine": "Fluid (.NET)"},
                errors=[],
            )
        finally:
            os.unlink(data_path)

    def _render_telosys_file(
        self, template_path: Path, context: Dict[str, Any]
    ) -> TemplateResult:
        """
        Render using Telosys (Java) from file.

        Note: Telosys requires a specific project structure. This is a simplified
        integration that may need adjustment based on your Telosys setup.
        """
        if not self.is_engine_available(TemplateEngineType.TELOSYS):
            error_msg = """Telosys is not available.

To install Telosys:
1. Download from https://www.telosys.org/
2. Extract to a directory
3. Add to PATH: export PATH=$PATH:/path/to/telosys/bin

Or use Jinja2/Mako as an alternative template engine.
"""
            console.print(
                Panel(
                    error_msg,
                    title="[red]Telosys Not Available[/red]",
                    border_style="red",
                )
            )
            raise EngineNotAvailableError("Telosys CLI not found")

        # Telosys typically works with a specific project structure
        # This is a simplified implementation
        telosys_dir = context.get("telosys_dir", ".")

        try:
            result = subprocess.run(
                ["telosys", "generate", "-c", str(template_path)],
                cwd=telosys_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                raise TemplateRenderError(f"Telosys error: {result.stderr}")

            # Telosys outputs to files, read the generated content
            output_files = list(Path(telosys_dir).glob("*.generated"))
            content = ""
            for f in output_files:
                content += f.read_text()
                f.unlink()

            return TemplateResult(
                content=content,
                engine=TemplateEngineType.TELOSYS,
                success=True,
                metadata={
                    "source": str(template_path),
                    "engine": "Telosys (Java)",
                    "output_languages": context.get("languages", ["java"]),
                },
                errors=[],
            )
        except subprocess.TimeoutExpired:
            raise TemplateRenderError("Telosys generation timed out")

    def generate_code(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
    ) -> TemplateResult:
        """
        Generate code using a built-in template.

        Args:
            template_name: Name of the built-in template
            context: Template context variables
            output_path: Optional path to write generated code

        Returns:
            TemplateResult with generated code

        Examples:
            >>> engine = TemplateEngine()
            >>> result = engine.generate_code('python_class', {
            ...     'class_name': 'User',
            ...     'params': [{'name': 'name', 'type': 'str'}]
            ... })
        """
        if template_name not in self._built_in_templates:
            available = ", ".join(self._built_in_templates.keys())
            raise TemplateRenderError(
                f"Unknown template '{template_name}'. Available: {available}"
            )

        template = self._built_in_templates[template_name]

        if self.verbose:
            console.print(
                f"[blue]Generating code with template:[/blue] {template_name}"
            )
            console.print(f"[dim]{template.description}[/dim]")

        result = self.render_template(
            template.template, context, engine_type=template.engine
        )

        # Write to file if specified
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result.content, encoding="utf-8")

            if self.verbose:
                console.print(
                    f"[green]✓[/green] Generated code written to: {output_path}"
                )

        return result

    def list_built_in_templates(self) -> Table:
        """
        Display available built-in templates in a formatted table.

        Returns:
            Rich Table object
        """
        table = Table(title="Built-in Templates")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Engine", style="green")

        for name, template in self._built_in_templates.items():
            table.add_row(name, template.description, template.engine.name)

        return table

    def discover_templates(self) -> List[Path]:
        """
        Discover templates in the templates directory.

        Returns:
            List of discovered template paths
        """
        if not self.templates_dir.exists():
            return []

        templates = []
        for pattern in ["*.j2", "*.mako", "*.liquid", "*.vm", "*.tel"]:
            templates.extend(self.templates_dir.glob(pattern))

        return templates

    def display_result(self, result: TemplateResult) -> None:
        """
        Display template result with syntax highlighting.

        Args:
            result: TemplateResult to display
        """
        if result.success:
            # Detect language for syntax highlighting
            lang = "python"  # default
            if "<!DOCTYPE html>" in result.content or "<html" in result.content:
                lang = "html"
            elif "<template>" in result.content or "import React" in result.content:
                lang = "tsx"
            elif "function" in result.content and ("{" in result.content):
                lang = "javascript"

            syntax = Syntax(result.content, lang, theme="monokai", line_numbers=True)

            console.print(
                Panel(
                    syntax,
                    title=f"Generated Code ({result.engine.name})",
                    border_style="green",
                )
            )

            if result.errors:
                console.print("[yellow]Warnings:[/yellow]")
                for error in result.errors:
                    console.print(f"  • {error}")
        else:
            console.print(
                Panel(
                    "\n".join(result.errors) if result.errors else "Rendering failed",
                    title="[red]Error[/red]",
                    border_style="red",
                )
            )

    def create_project_templates(
        self, project_type: str, output_dir: Union[str, Path]
    ) -> List[Path]:
        """
        Create a set of templates for a new project.

        Args:
            project_type: Type of project (python, react, vue, django)
            output_dir: Directory to create templates in

        Returns:
            List of created template paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        templates = {
            "python": {
                "class.j2": '''class {{ class_name }}:
    """{{ description }}"""
    
    def __init__(self{% for param in params %}, {{ param.name }}: {{ param.type | default('Any') }}{% endfor %}):
        {% for param in params %}
        self.{{ param.name }} = {{ param.name }}
        {% endfor %}''',
                "api_endpoint.j2": '''@app.{{ method }}("{{ path }}")
async def {{ name }}({% for param in params %}{{ param.name }}: {{ param.type }}{% endfor %}):
    """{{ description }}"""
    return {"message": "Hello World"}''',
            },
            "react": {
                "component.tsx.j2": """import React from 'react';

interface {{ name }}Props {
    {% for prop in props %}{{ prop.name }}: {{ prop.type }};{% endfor %}
}

export const {{ name }}: React.FC<{{ name }}Props> = ({ {% for prop in props %}{{ prop.name }}{% endfor %} }) => {
    return (
        <div className="{{ name | kebabcase }}">
            {/* Component content */}
        </div>
    );
};"""
            },
            "vue": {
                "component.vue.j2": """<template>
  <div class="{{ name | kebabcase }}">
    <!-- Component content -->
  </div>
</template>

<script setup lang="ts">
interface Props {
  {% for prop in props %}{{ prop.name }}: {{ prop.type }};{% endfor %}
}

const props = defineProps<Props>();
</script>"""
            },
            "django": {
                "model.py.j2": '''from django.db import models

class {{ name }}(models.Model):
    """{{ description }}"""
    
    {% for field in fields %}{{ field.name }} = models.{{ field.type }}({% if field.params %}{{ field.params }}{% endif %})
    {% endfor %}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "{{ name }}"
        verbose_name_plural = "{{ name }}s"'''
            },
        }

        created = []
        if project_type in templates:
            for filename, content in templates[project_type].items():
                filepath = output_dir / filename
                filepath.write_text(content, encoding="utf-8")
                created.append(filepath)

            if self.verbose:
                console.print(
                    f"[green]✓[/green] Created {len(created)} templates for {project_type}"
                )
        else:
            console.print(f"[yellow]⚠[/yellow] Unknown project type: {project_type}")

        return created


# Convenience functions for common use cases
def render_jinja_template(template_string: str, **context) -> str:
    """
    Quick Jinja2 template rendering.

    Args:
        template_string: Template content
        **context: Template variables

    Returns:
        Rendered string
    """
    engine = TemplateEngine()
    result = engine.render_template(
        template_string, context, engine_type=TemplateEngineType.JINJA2
    )
    return result.content


def generate_python_class(class_name: str, **kwargs) -> str:
    """
    Generate a Python class quickly.

    Args:
        class_name: Name of the class
        **kwargs: Additional context (params, methods, description)

    Returns:
        Generated class code
    """
    engine = TemplateEngine()
    context = {"class_name": class_name, **kwargs}
    result = engine.generate_code("python_class", context)
    return result.content


def main():
    """Demo the template engine capabilities."""
    console.print(
        Panel.fit(
            "[bold blue]MR.VERMA Template Engine[/bold blue]\n"
            "Multi-engine templating with Jinja2, Mako, Fluid, and Telosys support",
            border_style="blue",
        )
    )

    # Initialize engine
    engine = TemplateEngine(verbose=True)

    # Show available engines
    console.print("\n[bold]Available Engines:[/bold]")
    for eng in TemplateEngineType:
        status = (
            "[green]✓[/green]" if engine.is_engine_available(eng) else "[red]✗[/red]"
        )
        console.print(f"  {status} {eng.name}")

    # Demo Jinja2
    console.print("\n[bold]Demo: Jinja2 Template[/bold]")
    result = engine.render_template(
        "Hello {{ name }}! Today is {{ day }}.", {"name": "World", "day": "Monday"}
    )
    console.print(result.content)

    # Demo Python class generation
    console.print("\n[bold]Demo: Python Class Generation[/bold]")
    result = engine.generate_code(
        "python_class",
        {
            "class_name": "User",
            "description": "User model with authentication",
            "params": [
                {"name": "username", "type": "str"},
                {"name": "email", "type": "str"},
                {"name": "is_active", "type": "bool", "default": "True"},
            ],
            "methods": [
                {
                    "name": "authenticate",
                    "params": [{"name": "password", "type": "str"}],
                    "return_type": "bool",
                    "docstring": "Authenticate user with password",
                    "implementation": "# TODO: Implement authentication logic\nreturn True",
                }
            ],
        },
    )
    engine.display_result(result)

    # Show built-in templates
    console.print("\n")
    console.print(engine.list_built_in_templates())


if __name__ == "__main__":
    main()
