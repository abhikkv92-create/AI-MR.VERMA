# MR.VERMA Document & Code Generation System

> **Complete Document Generation (DOCX, PPTX, XLSX) + Database Management + Vector Embeddings + Code Templates**

## 🚀 Quick Start

### Windows
```bash
Double-click: START_DOCUMENTS.bat
```

### Linux/Mac
```bash
./start_documents.sh
```

---

## ✨ Features

### 📄 Document Generation
Create professional documents programmatically:

#### 1. Word Documents (.docx)
- **Library**: `python-docx`
- **Features**:
  - Headers and paragraphs
  - Bullet lists
  - Tables
  - Text formatting (bold, italic)
  - Alignment options

**Example**:
```python
from unified.document_generation import DocumentAgent

agent = DocumentAgent()
content = {
    'sections': [
        {
            'heading': 'Project Report',
            'level': 1,
            'paragraphs': [
                {'text': 'This is the main content.'},
                {'text': 'Important note!', 'bold': True}
            ],
            'bullets': [
                'Feature 1: Auto-generated',
                'Feature 2: Professional formatting'
            ]
        }
    ]
}
agent.create_document('docx', content, 'report.docx')
```

#### 2. PowerPoint Presentations (.pptx)
- **Library**: `python-pptx`
- **Features**:
  - Multiple slide layouts
  - Title slides
  - Content slides with bullets
  - Text formatting

**Example**:
```python
slides = [
    {
        'type': 'title',
        'title': 'Project Presentation'
    },
    {
        'type': 'content',
        'title': 'Key Features',
        'bullets': [
            'Automatic generation',
            'Professional templates',
            'Easy customization'
        ]
    }
]
agent.create_document('pptx', slides, 'presentation.pptx')
```

#### 3. Excel Spreadsheets (.xlsx)
- **Library**: `openpyxl`
- **Features**:
  - Headers with formatting
  - Data rows
  - Formulas
  - Auto-width columns
  - Styling (fonts, colors)

**Example**:
```python
data = {
    'sheet_name': 'Project Data',
    'headers': ['Task', 'Status', 'Priority'],
    'rows': [
        ['Design UI', 'Complete', 'High'],
        ['Backend API', 'In Progress', 'High'],
        ['Testing', 'Pending', 'Medium']
    ],
    'formulas': [
        {'row': 5, 'col': 2, 'formula': '=SUM(C2:C4)'}
    ]
}
agent.create_document('xlsx', data, 'data.xlsx')
```

---

### 🗄️ Database & Schema Management

#### SQLite Integration
- Create tables from schema definitions
- Insert and query data
- Schema introspection
- Full CRUD operations

**Example**:
```python
from unified.document_generation import DatabaseManager

db = DatabaseManager()

# Create schema
schema = {
    'users': {
        'id': {'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
        'name': {'type': 'TEXT', 'not_null': True},
        'email': {'type': 'TEXT', 'unique': True},
        'created_at': {'type': 'TEXT', 'default': 'CURRENT_TIMESTAMP'}
    }
}
db.create_table('users', schema['users'])

# Insert data
db.insert_data('users', {'name': 'Alice', 'email': 'alice@example.com'})

# Query
results = db.query("SELECT * FROM users WHERE name = ?", ('Alice',))
```

---

### 🔢 Vector Embeddings & Search

#### Vector Storage
- Store high-dimensional vectors
- Cosine similarity search
- Metadata association
- Scalable storage

**Example**:
```python
from unified.document_generation import VectorStore

store = VectorStore(dimension=384)

# Add vectors
store.add_vector('doc1', [0.1, 0.2, ...], {'title': 'Document 1'})
store.add_vector('doc2', [0.3, 0.4, ...], {'title': 'Document 2'})

# Search
results = store.search([0.15, 0.25, ...], top_k=5)
# Returns: [('doc1', 0.95, {...}), ('doc2', 0.82, {...})]
```

---

### 🛠️ Code Generation from Templates

#### Template Engine
- Python class generation
- API endpoint generation
- React component generation
- Custom template support

**Example**:
```python
from unified.document_generation import TemplateEngine

engine = TemplateEngine()

# Generate Python class
code = engine.generate_code('python_class', {
    'class_name': 'UserManager',
    'params': [
        {'name': 'db_path', 'default': '"users.db"'}
    ],
    'methods': [
        {
            'method_name': 'get_user',
            'args': ['user_id'],
            'description': 'Retrieve user by ID',
            'body': 'return self.db.query(user_id)'
        }
    ]
})

print(code)
# Output:
# class UserManager:
#     def __init__(self, db_path="users.db"):
#         self.db_path = db_path
#     
#     def get_user(self, user_id):
#         """Retrieve user by ID"""
#         return self.db.query(user_id)
```

---

## 🎮 Unified Document Agent

The `DocumentAgent` combines all capabilities:

```python
from unified.document_generation import DocumentAgent

agent = DocumentAgent()

# Check capabilities
caps = agent.get_capabilities()
print(caps)
# {
#     'document_types': ['docx', 'pptx', 'xlsx'],
#     'database': 'SQLite with schema management',
#     'vectors': '384-dimensional embeddings',
#     'code_generation': 'Template-based',
#     'libraries': {
#         'docx': True,
#         'pptx': True,
#         'xlsx': True,
#         'vectors': True
#     }
# }

# Generate documents
agent.create_document('docx', {...}, 'report.docx')
agent.create_document('pptx', {...}, 'slides.pptx')
agent.create_document('xlsx', {...}, 'data.xlsx')

# Database operations
agent.create_database_schema({...})

# Code generation
agent.generate_code('python_class', {...}, 'output.py')
```

---

## 📁 File Structure

```
MR.VERMA/
├── unified/
│   └── document_generation.py      # Main document generation module
├── output/
│   └── documents/                   # Generated documents
├── data/
│   └── mrverma.db                  # SQLite database
├── templates/                       # Code templates
└── START_DOCUMENTS.bat             # Launcher script
```

---

## 📚 API Reference

### DocumentGenerator Class

```python
generator = DocumentGenerator(config)

# Create Word document
generator.create_docx(content: Dict, filename: str) -> str

# Create PowerPoint
generator.create_pptx(slides: List[Dict], filename: str) -> str

# Create Excel
generator.create_xlsx(data: Dict, filename: str) -> str
```

### DatabaseManager Class

```python
db = DatabaseManager(db_path="data/app.db")

db.connect() -> bool
db.create_table(table_name: str, schema: Dict) -> str
db.insert_data(table_name: str, data: Dict) -> str
db.query(sql: str, params: tuple) -> List
db.get_schema(table_name: str = None) -> Dict
db.close()
```

### VectorStore Class

```python
store = VectorStore(dimension=384)

store.add_vector(id: str, vector: List[float], metadata: Dict)
store.search(query_vector: List[float], top_k: int) -> List
generate_embedding(text: str) -> List[float]
```

### TemplateEngine Class

```python
engine = TemplateEngine()

engine.render_template(template_name: str, data: Dict) -> str
engine.generate_code(template: str, data: Dict, output: str) -> str
```

---

## 🆘 Troubleshooting

### "Module not found" errors
```bash
pip install python-docx python-pptx openpyxl numpy
```

### "Permission denied" when saving files
- Check that `output/documents/` directory exists
- Ensure write permissions
- Run as administrator if needed

### Unicode errors on Windows
The system automatically handles Unicode encoding for special characters.

---

## 🎯 Use Cases

### 1. Automated Reporting
```python
# Generate weekly report
report_data = fetch_weekly_data()
agent.create_document('docx', report_data, 'weekly_report.docx')
agent.create_document('xlsx', report_data, 'weekly_data.xlsx')
```

### 2. Database Schema Generation
```python
# Create database from model definition
schema = generate_schema_from_models()
agent.create_database_schema(schema)
```

### 3. Presentation Generation
```python
# Create project presentation
slides = generate_slides_from_project_data()
agent.create_document('pptx', slides, 'project_presentation.pptx')
```

### 4. Vector Search Implementation
```python
# Build document search system
for doc in documents:
    embedding = store.generate_embedding(doc.text)
    store.add_vector(doc.id, embedding, doc.metadata)

# Search
results = store.search(query_embedding, top_k=10)
```

---

## 🔧 Advanced Configuration

### Custom Templates
Add your own templates to `templates/` directory:

```python
# templates/custom_class.py
template = '''
class {{class_name}}:
    """{{description}}"""
    
    def __init__(self{{#params}}, {{name}}={{default}}{{/params}}):
        {{#params}}
        self.{{name}} = {{name}}
        {{/params}}
'''
```

### Document Styling
Customize document appearance:

```python
# For DOCX
doc = Document()
style = doc.styles['Normal']
font = style.font
font.name = 'Arial'
font.size = Pt(12)

# For XLSX
from openpyxl.styles import Font, PatternFill
cell.font = Font(bold=True, color="FFFFFF")
cell.fill = PatternFill(start_color="4472C4", fill_type="solid")
```

---

## 📊 Integration with MR.VERMA

This document generation system integrates with:
- **MR.VERMA Autonomous** - Auto-generate docs based on project needs
- **MR.VERMA Ultimate** - Use 82 system prompts for better generation
- **Agent System** - @documentation-writer agent uses these tools
- **Workflow System** - /document workflow automatically creates docs

---

**Generate professional documents, manage databases, and create code automatically!** 📄✨

Version: 8.1 Document Generation | 2026-02-16
