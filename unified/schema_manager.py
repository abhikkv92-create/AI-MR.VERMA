#!/usr/bin/env python3
"""
MR.VERMA Schema Manager
=======================

A comprehensive database schema management module for MR.VERMA that provides:
- SQLAlchemy ORM integration with multi-database support
- Schema validation and migration capabilities
- Vector metadata storage for document embeddings
- Connection pooling and backup/restore functionality

Database Support:
    - SQLite (default) - file-based, perfect for development
    - PostgreSQL - production-ready with full features

Features:
    - create_table(): Create tables with schema definitions
    - insert_data(): Insert data into tables
    - query(): Execute SQL queries with parameters
    - get_schema(): Retrieve current schema information
    - migrate_schema(): Apply schema migrations
    - backup/restore(): Database backup and restoration

Usage:
    from unified.schema_manager import SchemaManager

    # Initialize with SQLite (default)
    manager = SchemaManager()

    # Or with PostgreSQL
    manager = SchemaManager(
        db_type="postgresql",
        connection_string="postgresql://user:pass@localhost/mrverma"
    )

    # Create tables
    schema = {
        'users': {
            'id': {'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
            'name': {'type': 'TEXT', 'not_null': True},
            'email': {'type': 'TEXT', 'unique': True},
        }
    }
    manager.create_table('users', schema['users'])

Author: MR.VERMA
Version: 1.0.0
"""

import os
import sys
import json
import shutil
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
import threading
import logging

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# SQLAlchemy imports
try:
    from sqlalchemy import (
        create_engine,
        MetaData,
        Table,
        Column,
        Integer,
        String,
        Text,
        Float,
        DateTime,
        Boolean,
        JSON,
        ForeignKey,
        Index,
        inspect,
        text,
        event,
        insert,
    )
    from sqlalchemy.orm import sessionmaker, Session, declarative_base
    from sqlalchemy.pool import QueuePool, NullPool
    from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
    from sqlalchemy.types import TypeDecorator, UserDefinedType
    from sqlalchemy.schema import CreateTable, CreateIndex

    SQLALCHEMY_AVAILABLE = True

    # Custom type for storing vector embeddings as JSON
    class VectorType(TypeDecorator):
        """Custom type for storing vector embeddings as JSON"""

        impl = JSON
        cache_ok = True

        def process_bind_param(self, value, dialect):
            """Convert vector to JSON for storage"""
            if value is None:
                return None
            if isinstance(value, list):
                return value
            return list(value)

        def process_result_value(self, value, dialect):
            """Convert JSON back to vector"""
            if value is None:
                return None
            return value

except ImportError:
    SQLALCHEMY_AVAILABLE = False
    VectorType = None

# PostgreSQL support
try:
    import psycopg2
    import psycopg2.extras

    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Rich console for output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax

    RICH_AVAILABLE = True

    # Create console with safe encoding for Windows
    import sys

    if sys.platform == "win32":
        # Use color_system=None and force_terminal to avoid Windows encoding issues
        console = Console(color_system=None, force_terminal=True)
    else:
        console = Console()
except ImportError:
    RICH_AVAILABLE = False

    class SimpleConsole:
        """Fallback console when rich is not available"""

        def print(self, *args, **kwargs):
            print(" ".join(str(a) for a in args))

        def status(self, message):
            class DummyStatus:
                def __enter__(self):
                    print(f"Processing: {message}...")
                    return self

                def __exit__(self, *args):
                    pass

            return DummyStatus()

    console = SimpleConsole()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MR.VERMA.SchemaManager")


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS AND DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════


class DatabaseType(Enum):
    """Supported database types"""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class ColumnType(Enum):
    """Supported column types with mappings"""

    INTEGER = "INTEGER"
    TEXT = "TEXT"
    VARCHAR = "VARCHAR"
    FLOAT = "FLOAT"
    REAL = "REAL"
    BOOLEAN = "BOOLEAN"
    DATETIME = "DATETIME"
    TIMESTAMP = "TIMESTAMP"
    JSON = "JSON"
    BLOB = "BLOB"
    VECTOR = "VECTOR"


@dataclass
class ColumnDefinition:
    """Definition of a database column"""

    name: str
    type: str
    primary_key: bool = False
    autoincrement: bool = False
    not_null: bool = False
    unique: bool = False
    default: Any = None
    index: bool = False
    foreign_key: Optional[str] = None
    max_length: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "type": self.type,
            "primary_key": self.primary_key,
            "autoincrement": self.autoincrement,
            "not_null": self.not_null,
            "unique": self.unique,
            "default": self.default,
            "index": self.index,
            "foreign_key": self.foreign_key,
            "max_length": self.max_length,
        }


@dataclass
class SchemaChange:
    """Represents a schema migration change"""

    operation: str  # 'add_column', 'drop_column', 'modify_column', 'create_index', 'drop_index'
    table_name: str
    column_name: Optional[str] = None
    column_def: Optional[Dict[str, Any]] = None
    new_name: Optional[str] = None
    index_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "operation": self.operation,
            "table_name": self.table_name,
            "column_name": self.column_name,
            "column_def": self.column_def,
            "new_name": self.new_name,
            "index_name": self.index_name,
        }


@dataclass
class VectorMetadata:
    """Metadata for vector embeddings"""

    document_id: str
    vector_location: str
    embedding_dimension: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "document_id": self.document_id,
            "vector_location": self.vector_location,
            "embedding_dimension": self.embedding_dimension,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class BackupInfo:
    """Information about a database backup"""

    backup_path: str
    original_path: str
    timestamp: datetime
    size_bytes: int
    checksum: str
    tables: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA MANAGER CLASS
# ═══════════════════════════════════════════════════════════════════════════════


class SchemaManager:
    """
    Comprehensive database schema management for MR.VERMA.

    Provides SQLAlchemy ORM integration, multi-database support,
    schema validation, migrations, and vector metadata storage.

    Attributes:
        db_type: Type of database (sqlite or postgresql)
        connection_string: Database connection string
        engine: SQLAlchemy engine instance
        session_factory: Factory for creating database sessions
        metadata: SQLAlchemy metadata instance
        tables: Dictionary of created tables
        _lock: Thread lock for thread-safe operations

    Example:
        >>> manager = SchemaManager()
        >>> schema = {
        ...     'id': {'type': 'INTEGER', 'primary_key': True},
        ...     'name': {'type': 'TEXT', 'not_null': True}
        ... }
        >>> manager.create_table('users', schema)
        [OK] Table 'users' created successfully
    """

    def __init__(
        self,
        db_type: str = "sqlite",
        database_path: Optional[str] = None,
        connection_string: Optional[str] = None,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
    ):
        """
        Initialize the Schema Manager.

        Args:
            db_type: Database type ('sqlite' or 'postgresql')
            database_path: Path for SQLite database (ignored for PostgreSQL)
            connection_string: Full connection string for PostgreSQL
            echo: Enable SQLAlchemy query logging
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
            pool_timeout: Connection pool timeout in seconds

        Raises:
            ImportError: If SQLAlchemy is not installed
            ValueError: If invalid database type specified
        """
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError(
                "SQLAlchemy is required. Install with: pip install sqlalchemy"
            )

        self.db_type = DatabaseType(db_type.lower())
        self.database_path = database_path
        self.connection_string = connection_string
        self.echo = echo
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout

        self.engine = None
        self.session_factory = None
        self.metadata = MetaData()
        self.tables: Dict[str, Table] = {}
        self._lock = threading.RLock()

        # Initialize vector metadata tables
        self._vector_tables_created = False

        self._initialize_engine()
        self._setup_vector_metadata_tables()

        console.print(f"[OK] Schema Manager initialized with {self.db_type.value}")

    def _initialize_engine(self) -> None:
        """Initialize the database engine with appropriate configuration."""
        if self.db_type == DatabaseType.SQLITE:
            self._init_sqlite_engine()
        elif self.db_type == DatabaseType.POSTGRESQL:
            self._init_postgresql_engine()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def _init_sqlite_engine(self) -> None:
        """Initialize SQLite engine with connection pooling."""
        if self.database_path is None:
            # Default to data directory
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            self.database_path = str(data_dir / "mrverma.db")

        connection_url = f"sqlite:///{self.database_path}"

        # SQLite specific settings for better concurrency
        self.engine = create_engine(
            connection_url,
            echo=self.echo,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            connect_args={"check_same_thread": False, "timeout": 30},
        )

        # Enable foreign keys
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        self.session_factory = sessionmaker(bind=self.engine)

    def _init_postgresql_engine(self) -> None:
        """Initialize PostgreSQL engine with connection pooling."""
        if not POSTGRES_AVAILABLE:
            raise ImportError(
                "PostgreSQL support requires psycopg2. "
                "Install with: pip install psycopg2-binary"
            )

        if self.connection_string is None:
            raise ValueError("Connection string is required for PostgreSQL")

        self.engine = create_engine(
            self.connection_string,
            echo=self.echo,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_pre_ping=True,  # Verify connections before using
        )

        self.session_factory = sessionmaker(bind=self.engine)

    def _setup_vector_metadata_tables(self) -> None:
        """Create internal tables for vector metadata storage."""
        if self._vector_tables_created:
            return

        try:
            # Vector metadata table
            self._vector_metadata = Table(
                "_vector_metadata",
                self.metadata,
                Column("id", Integer, primary_key=True, autoincrement=True),
                Column(
                    "document_id", String(255), unique=True, nullable=False, index=True
                ),
                Column("vector_location", String(512), nullable=False),
                Column("embedding_dimension", Integer, nullable=False),
                Column("metadata", JSON, default={}),
                Column("created_at", DateTime, default=datetime.now),
                Column("updated_at", DateTime, nullable=True),
                Index("idx_vector_doc_id", "document_id"),
                Index("idx_vector_location", "vector_location"),
            )

            # Vector search index table
            self._vector_search_index = Table(
                "_vector_search_index",
                self.metadata,
                Column("id", Integer, primary_key=True, autoincrement=True),
                Column(
                    "document_id",
                    String(255),
                    ForeignKey("_vector_metadata.document_id"),
                    nullable=False,
                ),
                Column("search_tags", JSON, default=[]),
                Column("category", String(100), index=True),
                Column("last_accessed", DateTime, nullable=True),
                Index("idx_vector_category", "category"),
                Index("idx_vector_tags", "search_tags"),
            )

            self.metadata.create_all(self.engine)
            self._vector_tables_created = True
            logger.info("Vector metadata tables initialized")

        except Exception as e:
            logger.error(f"Failed to create vector metadata tables: {e}")
            raise

    @contextmanager
    def session_scope(self):
        """
        Context manager for database sessions.

        Automatically handles commit/rollback and session cleanup.

        Yields:
            Session: SQLAlchemy session object

        Example:
            >>> with manager.session_scope() as session:
            ...     result = session.query(MyTable).all()
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()

    def create_table(
        self,
        name: str,
        schema_definition: Dict[str, Dict[str, Any]],
        if_not_exists: bool = True,
    ) -> str:
        """
        Create a new table with the specified schema.

        Args:
            name: Table name
            schema_definition: Dictionary defining columns and their properties
            if_not_exists: Only create if table doesn't exist

        Returns:
            str: Success or error message

        Example:
            >>> schema = {
            ...     'id': {'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
            ...     'name': {'type': 'TEXT', 'not_null': True},
            ...     'email': {'type': 'TEXT', 'unique': True}
            ... }
            >>> manager.create_table('users', schema)
            '[OK] Table users created successfully'
        """
        with self._lock:
            try:
                # Check if table exists in database
                inspector = inspect(self.engine)
                existing_tables = inspector.get_table_names()

                if if_not_exists and name in existing_tables:
                    # Table already exists in database
                    if name not in self.tables:
                        # Reflect the existing table
                        table = Table(name, self.metadata, autoload_with=self.engine)
                        self.tables[name] = table
                    return f"[WARN] Table '{name}' already exists"

                # Build columns
                columns = []
                indexes = []

                for col_name, col_def in schema_definition.items():
                    column = self._build_column(col_name, col_def)
                    columns.append(column)

                    # Track indexes to create separately
                    if col_def.get("index") and not col_def.get("primary_key"):
                        indexes.append(col_name)

                # Create table using metadata (SQLAlchemy 2.0 compatible)
                table = Table(name, self.metadata, *columns)

                # Create in database (SQLAlchemy 2.0 - create all tables in metadata)
                self.metadata.create_all(self.engine)

                # Create additional indexes
                for idx_col in indexes:
                    idx_name = f"idx_{name}_{idx_col}"
                    idx = Index(idx_name, table.c[idx_col])
                    idx.create(self.engine, checkfirst=True)

                # Store reference
                self.tables[name] = table

                msg = f"[OK] Table '{name}' created successfully"
                console.print(f"[green]{msg}[/green]" if RICH_AVAILABLE else msg)
                return msg

            except SQLAlchemyError as e:
                error_msg = f"[ERROR] Failed to create table '{name}': {str(e)}"
                logger.error(error_msg)
                console.print(
                    f"[red]{error_msg}[/red]" if RICH_AVAILABLE else error_msg
                )
                return error_msg

    def _build_column(self, name: str, definition: Dict[str, Any]) -> Column:
        """
        Build a SQLAlchemy Column from definition dictionary.

        Args:
            name: Column name
            definition: Column properties dictionary

        Returns:
            Column: SQLAlchemy Column object
        """
        col_type_str = definition.get("type", "TEXT").upper()

        # Map type strings to SQLAlchemy types
        type_mapping = {
            "INTEGER": Integer,
            "TEXT": Text,
            "VARCHAR": lambda: String(definition.get("max_length", 255)),
            "STRING": lambda: String(definition.get("max_length", 255)),
            "FLOAT": Float,
            "REAL": Float,
            "BOOLEAN": Boolean,
            "DATETIME": DateTime,
            "TIMESTAMP": DateTime,
            "JSON": JSON,
            "BLOB": Text,  # Store as base64 text
            "VECTOR": VectorType,
        }

        col_type = type_mapping.get(col_type_str, Text)
        if callable(col_type):
            col_type = col_type()

        # Build column arguments
        kwargs = {}

        if definition.get("primary_key"):
            kwargs["primary_key"] = True

        if definition.get("autoincrement"):
            kwargs["autoincrement"] = True

        if definition.get("not_null"):
            kwargs["nullable"] = False

        if definition.get("unique"):
            kwargs["unique"] = True

        if "default" in definition:
            default_val = definition["default"]
            if default_val == "CURRENT_TIMESTAMP":
                kwargs["default"] = datetime.now
            else:
                kwargs["default"] = default_val

        if definition.get("foreign_key"):
            kwargs["ForeignKey"] = ForeignKey(definition["foreign_key"])

        return Column(name, col_type, **kwargs)

    def insert_data(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        returning: Optional[List[str]] = None,
    ) -> Union[str, List[Dict[str, Any]]]:
        """
        Insert data into a table.

        Args:
            table: Table name
            data: Dictionary or list of dictionaries containing data
            returning: List of column names to return after insert (PostgreSQL only)

        Returns:
            str or list: Success message or inserted records

        Example:
            >>> data = {'name': 'John Doe', 'email': 'john@example.com'}
            >>> manager.insert_data('users', data)
            '[OK] Inserted 1 row into users'
        """
        with self._lock:
            try:
                if table not in self.tables:
                    # Try to reflect from database
                    self._reflect_table(table)

                if isinstance(data, dict):
                    data = [data]

                with self.session_scope() as session:
                    table_obj = self.tables[table]

                    inserted_ids = []
                    for record in data:
                        stmt = insert(table_obj).values(**record)
                        result = session.execute(stmt)
                        inserted_ids.append(
                            result.inserted_primary_key[0]
                            if result.inserted_primary_key
                            else None
                        )

                    count = len(data)
                    msg = f"[OK] Inserted {count} row{'s' if count > 1 else ''} into '{table}'"
                    console.print(f"[green]{msg}[/green]" if RICH_AVAILABLE else msg)

                    if returning and self.db_type == DatabaseType.POSTGRESQL:
                        # Return specified columns
                        return self.query(
                            f"SELECT {', '.join(returning)} FROM {table} WHERE id = ANY(:ids)",
                            {"ids": [id for id in inserted_ids if id is not None]},
                        )

                    return msg

            except IntegrityError as e:
                error_msg = (
                    f"[ERROR] Integrity error inserting into '{table}': {str(e)}"
                )
                logger.error(error_msg)
                return error_msg
            except SQLAlchemyError as e:
                error_msg = f"[ERROR] Error inserting into '{table}': {str(e)}"
                logger.error(error_msg)
                return error_msg

    def query(
        self, sql: str, params: Optional[Dict[str, Any]] = None, fetch_all: bool = True
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], str]:
        """
        Execute a SQL query with parameters.

        Args:
            sql: SQL query string (use :param_name for parameters)
            params: Dictionary of parameters
            fetch_all: Return all results or just first row

        Returns:
            list, dict, or str: Query results or error message

        Example:
            >>> results = manager.query(
            ...     "SELECT * FROM users WHERE email = :email",
            ...     {'email': 'john@example.com'}
            ... )
        """
        try:
            with self.session_scope() as session:
                result = session.execute(text(sql), params or {})

                if result.returns_rows:
                    rows = (
                        result.mappings().all()
                        if fetch_all
                        else [result.mappings().first()]
                    )
                    # Convert to list of dicts
                    if fetch_all:
                        return [dict(row) for row in rows if row]
                    else:
                        return dict(rows[0]) if rows and rows[0] else {}
                else:
                    return f"[OK] Query executed successfully. Rows affected: {result.rowcount}"

        except SQLAlchemyError as e:
            error_msg = f"[ERROR] Query error: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def get_schema(
        self, table_name: Optional[str] = None, include_indexes: bool = True
    ) -> Dict[str, Any]:
        """
        Get current database schema information.

        Args:
            table_name: Specific table to get schema for (None for all)
            include_indexes: Include index information

        Returns:
            dict: Schema definition dictionary

        Example:
            >>> schema = manager.get_schema('users')
            >>> print(schema)
            {
                'users': {
                    'columns': {...},
                    'indexes': [...],
                    'foreign_keys': [...]
                }
            }
        """
        try:
            inspector = inspect(self.engine)
            schema_info = {}

            tables_to_inspect = (
                [table_name] if table_name else inspector.get_table_names()
            )

            for table in tables_to_inspect:
                if table is None:
                    continue

                columns = inspector.get_columns(table)
                column_info = {}

                for col in columns:
                    col_def = {
                        "type": str(col["type"]),
                        "nullable": col.get("nullable", True),
                        "default": str(col.get("default"))
                        if col.get("default")
                        else None,
                    }
                    column_info[col["name"]] = col_def

                table_info = {"columns": column_info}

                if include_indexes:
                    table_info["indexes"] = inspector.get_indexes(table)
                    table_info["foreign_keys"] = inspector.get_foreign_keys(table)
                    table_info["primary_key"] = inspector.get_pk_constraint(table)

                schema_info[table] = table_info

            return schema_info

        except SQLAlchemyError as e:
            error_msg = f"[ERROR] Error getting schema: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def migrate_schema(self, changes: List[SchemaChange]) -> List[str]:
        """
        Apply schema migration changes.

        Args:
            changes: List of SchemaChange objects describing migrations

        Returns:
            list: List of operation results

        Example:
            >>> changes = [
            ...     SchemaChange('add_column', 'users', column_name='age',
            ...                  column_def={'type': 'INTEGER'}),
            ...     SchemaChange('create_index', 'users', index_name='idx_email',
            ...                  column_name='email')
            ... ]
            >>> results = manager.migrate_schema(changes)
        """
        results = []

        with self._lock:
            for change in changes:
                try:
                    result = self._apply_migration(change)
                    results.append(result)
                except Exception as e:
                    error_msg = (
                        f"[ERROR] Migration failed for {change.operation}: {str(e)}"
                    )
                    logger.error(error_msg)
                    results.append(error_msg)

        return results

    def _apply_migration(self, change: SchemaChange) -> str:
        """Apply a single migration change."""
        op = change.operation
        table = change.table_name

        if op == "add_column":
            return self._add_column(table, change.column_name, change.column_def)
        elif op == "drop_column":
            return self._drop_column(table, change.column_name)
        elif op == "modify_column":
            return self._modify_column(table, change.column_name, change.column_def)
        elif op == "create_index":
            return self._create_index(table, change.index_name, change.column_name)
        elif op == "drop_index":
            return self._drop_index(table, change.index_name)
        elif op == "rename_column":
            return self._rename_column(table, change.column_name, change.new_name)
        else:
            return f"[ERROR] Unknown operation: {op}"

    def _add_column(self, table: str, column: str, definition: Dict) -> str:
        """Add a column to a table."""
        col_type = definition.get("type", "TEXT")
        nullable = "NULL" if not definition.get("not_null") else "NOT NULL"
        default = f"DEFAULT {definition['default']}" if "default" in definition else ""

        sql = f"ALTER TABLE {table} ADD COLUMN {column} {col_type} {nullable} {default}"
        result = self.query(sql)

        if definition.get("index"):
            idx_name = f"idx_{table}_{column}"
            self._create_index(table, idx_name, column)

        return f"[OK] Added column '{column}' to '{table}'"

    def _drop_column(self, table: str, column: str) -> str:
        """Drop a column from a table."""
        if self.db_type == DatabaseType.SQLITE:
            # SQLite doesn't support DROP COLUMN directly
            return self._sqlite_drop_column(table, column)

        sql = f"ALTER TABLE {table} DROP COLUMN {column}"
        self.query(sql)
        return f"[OK] Dropped column '{column}' from '{table}'"

    def _sqlite_drop_column(self, table: str, column: str) -> str:
        """SQLite-specific column drop using table recreation."""
        schema = self.get_schema(table)

        # Get current columns excluding the one to drop
        columns = [col for col in schema[table]["columns"].keys() if col != column]

        # Create temp table
        temp_table = f"{table}_temp"
        col_defs = []
        for col in columns:
            col_info = schema[table]["columns"][col]
            col_defs.append(f"{col} {col_info['type']}")

        self.query(f"CREATE TABLE {temp_table} ({', '.join(col_defs)})")
        self.query(f"INSERT INTO {temp_table} SELECT {', '.join(columns)} FROM {table}")
        self.query(f"DROP TABLE {table}")
        self.query(f"ALTER TABLE {temp_table} RENAME TO {table}")

        return f"[OK] Dropped column '{column}' from '{table}' (SQLite workaround)"

    def _modify_column(self, table: str, column: str, definition: Dict) -> str:
        """Modify an existing column."""
        # SQLite requires table recreation for column modifications
        if self.db_type == DatabaseType.SQLITE:
            return self._sqlite_modify_column(table, column, definition)

        col_type = definition.get("type", "TEXT")
        sql = f"ALTER TABLE {table} ALTER COLUMN {column} TYPE {col_type}"
        self.query(sql)
        return f"[OK] Modified column '{column}' in '{table}'"

    def _sqlite_modify_column(self, table: str, column: str, definition: Dict) -> str:
        """SQLite-specific column modification."""
        # Get current schema
        schema = self.get_schema(table)

        # Build new column definitions
        new_columns = {}
        for col, info in schema[table]["columns"].items():
            if col == column:
                new_columns[col] = definition
            else:
                new_columns[col] = {"type": info["type"]}

        # Recreate table with new schema
        temp_table = f"{table}_temp"
        self.create_table(temp_table, new_columns, if_not_exists=False)

        # Copy data
        cols = list(new_columns.keys())
        self.query(f"INSERT INTO {temp_table} SELECT {', '.join(cols)} FROM {table}")

        # Replace old table
        self.query(f"DROP TABLE {table}")
        self.query(f"ALTER TABLE {temp_table} RENAME TO {table}")

        return f"[OK] Modified column '{column}' in '{table}' (SQLite workaround)"

    def _create_index(self, table: str, index_name: str, column: str) -> str:
        """Create an index on a table."""
        sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table} ({column})"
        self.query(sql)
        return f"[OK] Created index '{index_name}' on '{table}.{column}'"

    def _drop_index(self, table: str, index_name: str) -> str:
        """Drop an index from a table."""
        sql = f"DROP INDEX IF EXISTS {index_name}"
        self.query(sql)
        return f"[OK] Dropped index '{index_name}' from '{table}'"

    def _rename_column(self, table: str, old_name: str, new_name: str) -> str:
        """Rename a column."""
        if self.db_type == DatabaseType.SQLITE:
            # SQLite doesn't support RENAME COLUMN directly (until 3.25.0)
            schema = self.get_schema(table)

            # Build new column definitions
            new_columns = {}
            for col, info in schema[table]["columns"].items():
                col_name = new_name if col == old_name else col
                new_columns[col_name] = {"type": info["type"]}

            # Recreate table
            temp_table = f"{table}_temp"
            self.create_table(temp_table, new_columns, if_not_exists=False)

            # Copy data
            old_cols = list(schema[table]["columns"].keys())
            new_cols = [new_name if col == old_name else col for col in old_cols]
            self.query(
                f"INSERT INTO {temp_table} ({', '.join(new_cols)}) SELECT {', '.join(old_cols)} FROM {table}"
            )

            self.query(f"DROP TABLE {table}")
            self.query(f"ALTER TABLE {temp_table} RENAME TO {table}")

            return f"[OK] Renamed column '{old_name}' to '{new_name}' in '{table}'"

        sql = f"ALTER TABLE {table} RENAME COLUMN {old_name} TO {new_name}"
        self.query(sql)
        return f"[OK] Renamed column '{old_name}' to '{new_name}' in '{table}'"

    def backup(self, backup_dir: Optional[str] = None) -> Union[BackupInfo, str]:
        """
        Create a backup of the database.

        Args:
            backup_dir: Directory to store backup (default: data/backups)

        Returns:
            BackupInfo or str: Backup information or error message

        Example:
            >>> backup = manager.backup()
            >>> print(f"Backup created: {backup.backup_path}")
        """
        try:
            if backup_dir is None:
                backup_dir = Path("data/backups")
            else:
                backup_dir = Path(backup_dir)

            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if self.db_type == DatabaseType.SQLITE:
                # Backup SQLite by copying the file
                if not self.database_path:
                    return "[ERROR] No database path specified for SQLite backup"

                original_path = Path(self.database_path)
                backup_filename = f"mrverma_backup_{timestamp}.db"
                backup_path = backup_dir / backup_filename

                # Create backup
                shutil.copy2(original_path, backup_path)

                # Calculate checksum
                with open(backup_path, "rb") as f:
                    checksum = hashlib.sha256(f.read()).hexdigest()

                # Get table list
                tables = list(self.get_schema().keys())

                backup_info = BackupInfo(
                    backup_path=str(backup_path),
                    original_path=str(original_path),
                    timestamp=datetime.now(),
                    size_bytes=backup_path.stat().st_size,
                    checksum=checksum,
                    tables=tables,
                )

                msg = f"[OK] Backup created: {backup_path} ({backup_info.size_bytes} bytes)"
                console.print(f"[green]{msg}[/green]" if RICH_AVAILABLE else msg)

                return backup_info

            elif self.db_type == DatabaseType.POSTGRESQL:
                # For PostgreSQL, use pg_dump
                backup_filename = f"mrverma_backup_{timestamp}.sql"
                backup_path = backup_dir / backup_filename

                # Extract connection details from connection string
                # This is a simplified version - in production, parse properly
                cmd = [
                    "pg_dump",
                    "--no-owner",
                    "--no-acl",
                    "-f",
                    str(backup_path),
                    self.connection_string,
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    return f"[ERROR] PostgreSQL backup failed: {result.stderr}"

                with open(backup_path, "rb") as f:
                    checksum = hashlib.sha256(f.read()).hexdigest()

                tables = list(self.get_schema().keys())

                backup_info = BackupInfo(
                    backup_path=str(backup_path),
                    original_path=self.connection_string,
                    timestamp=datetime.now(),
                    size_bytes=backup_path.stat().st_size,
                    checksum=checksum,
                    tables=tables,
                )

                msg = f"[OK] PostgreSQL backup created: {backup_path}"
                console.print(f"[green]{msg}[/green]" if RICH_AVAILABLE else msg)

                return backup_info

        except Exception as e:
            error_msg = f"[ERROR] Backup failed: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def restore(self, backup_path: str, confirm: bool = False) -> str:
        """
        Restore database from backup.

        Args:
            backup_path: Path to backup file
            confirm: Must be True to perform restore (safety measure)

        Returns:
            str: Success or error message

        Example:
            >>> result = manager.restore('data/backups/mrverma_backup_20240101_120000.db', confirm=True)
        """
        if not confirm:
            return "[ERROR] Restore requires confirm=True parameter for safety"

        try:
            backup_file = Path(backup_path)

            if not backup_file.exists():
                return f"[ERROR] Backup file not found: {backup_path}"

            if self.db_type == DatabaseType.SQLITE:
                # Close current connections
                self.engine.dispose()

                # Restore by copying backup over current database
                if not self.database_path:
                    return "[ERROR] No database path specified for SQLite restore"

                shutil.copy2(backup_path, self.database_path)

                # Reinitialize engine
                self._initialize_engine()

                msg = f"[OK] Database restored from: {backup_path}"
                console.print(f"[green]{msg}[/green]" if RICH_AVAILABLE else msg)
                return msg

            elif self.db_type == DatabaseType.POSTGRESQL:
                # Close current connections
                self.engine.dispose()

                # Use psql to restore
                cmd = ["psql", "-f", backup_path, self.connection_string]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    return f"[ERROR] PostgreSQL restore failed: {result.stderr}"

                # Reinitialize engine
                self._initialize_engine()

                msg = f"[OK] PostgreSQL database restored from: {backup_path}"
                console.print(f"[green]{msg}[/green]" if RICH_AVAILABLE else msg)
                return msg

        except Exception as e:
            error_msg = f"[ERROR] Restore failed: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # ═══════════════════════════════════════════════════════════════════════════════
    # VECTOR METADATA METHODS
    # ═══════════════════════════════════════════════════════════════════════════════

    def store_vector_metadata(
        self,
        document_id: str,
        vector_location: str,
        embedding_dimension: int,
        metadata: Optional[Dict[str, Any]] = None,
        search_tags: Optional[List[str]] = None,
        category: Optional[str] = None,
    ) -> str:
        """
        Store metadata for a vector embedding.

        This integrates with VectorStore for document embeddings.

        Args:
            document_id: Unique document identifier
            vector_location: Storage location (file path, index ID, etc.)
            embedding_dimension: Dimension of the embedding vector
            metadata: Additional metadata dictionary
            search_tags: Tags for search optimization
            category: Document category

        Returns:
            str: Success or error message

        Example:
            >>> manager.store_vector_metadata(
            ...     document_id='doc_001',
            ...     vector_location='vectors/index_001.bin',
            ...     embedding_dimension=384,
            ...     metadata={'title': 'Sample Document'},
            ...     search_tags=['ai', 'ml'],
            ...     category='research'
            ... )
        """
        try:
            metadata = metadata or {}
            search_tags = search_tags or []

            # Insert or update vector metadata
            sql = """
                INSERT INTO _vector_metadata 
                (document_id, vector_location, embedding_dimension, metadata, updated_at)
                VALUES (:doc_id, :location, :dim, :meta, :updated)
                ON CONFLICT(document_id) DO UPDATE SET
                vector_location = excluded.vector_location,
                embedding_dimension = excluded.embedding_dimension,
                metadata = excluded.metadata,
                updated_at = excluded.updated_at
            """

            # Use SQLite-compatible syntax
            if self.db_type == DatabaseType.SQLITE:
                sql = """
                    INSERT OR REPLACE INTO _vector_metadata 
                    (document_id, vector_location, embedding_dimension, metadata, updated_at)
                    VALUES (:doc_id, :location, :dim, :meta, :updated)
                """

            self.query(
                sql,
                {
                    "doc_id": document_id,
                    "location": vector_location,
                    "dim": embedding_dimension,
                    "meta": json.dumps(metadata),
                    "updated": datetime.now().isoformat(),
                },
            )

            # Update search index
            sql_index = """
                INSERT OR REPLACE INTO _vector_search_index
                (document_id, search_tags, category, last_accessed)
                VALUES (:doc_id, :tags, :cat, :accessed)
            """

            self.query(
                sql_index,
                {
                    "doc_id": document_id,
                    "tags": json.dumps(search_tags),
                    "cat": category,
                    "accessed": datetime.now().isoformat(),
                },
            )

            msg = f"[OK] Vector metadata stored for document '{document_id}'"
            console.print(f"[green]{msg}[/green]" if RICH_AVAILABLE else msg)
            return msg

        except Exception as e:
            error_msg = f"[ERROR] Failed to store vector metadata: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def get_vector_metadata(self, document_id: str) -> Union[VectorMetadata, str]:
        """
        Retrieve vector metadata for a document.

        Args:
            document_id: Document identifier

        Returns:
            VectorMetadata or str: Metadata object or error message
        """
        try:
            sql = """
                SELECT vm.*, vsi.search_tags, vsi.category
                FROM _vector_metadata vm
                LEFT JOIN _vector_search_index vsi ON vm.document_id = vsi.document_id
                WHERE vm.document_id = :doc_id
            """

            result = self.query(sql, {"doc_id": document_id}, fetch_all=False)

            if isinstance(result, str) or not result:
                return f"[ERROR] No metadata found for document '{document_id}'"

            return VectorMetadata(
                document_id=result["document_id"],
                vector_location=result["vector_location"],
                embedding_dimension=result["embedding_dimension"],
                metadata=json.loads(result["metadata"])
                if result.get("metadata")
                else {},
                created_at=datetime.fromisoformat(result["created_at"])
                if result.get("created_at")
                else datetime.now(),
                updated_at=datetime.fromisoformat(result["updated_at"])
                if result.get("updated_at")
                else None,
            )

        except Exception as e:
            error_msg = f"[ERROR] Error retrieving vector metadata: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def search_vector_metadata(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Union[List[Dict[str, Any]], str]:
        """
        Search vector metadata by category and tags.

        Args:
            category: Filter by category
            tags: Filter by tags (any match)
            limit: Maximum results

        Returns:
            list or str: List of matching metadata or error message
        """
        try:
            conditions = []
            params = {"limit": limit}

            if category:
                conditions.append("vsi.category = :category")
                params["category"] = category

            if tags:
                # This is a simplified tag search
                # In production, use a proper JSON search
                tag_conditions = []
                for i, tag in enumerate(tags):
                    tag_conditions.append(f"vsi.search_tags LIKE :tag{i}")
                    params[f"tag{i}"] = f'%"{tag}"%'
                conditions.append(f"({' OR '.join(tag_conditions)})")

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            sql = f"""
                SELECT vm.*, vsi.search_tags, vsi.category, vsi.last_accessed
                FROM _vector_metadata vm
                JOIN _vector_search_index vsi ON vm.document_id = vsi.document_id
                {where_clause}
                ORDER BY vm.created_at DESC
                LIMIT :limit
            """

            return self.query(sql, params)

        except Exception as e:
            error_msg = f"[ERROR] Error searching vector metadata: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def delete_vector_metadata(self, document_id: str) -> str:
        """
        Delete vector metadata for a document.

        Args:
            document_id: Document identifier

        Returns:
            str: Success or error message
        """
        try:
            # Delete from search index first (foreign key)
            self.query(
                "DELETE FROM _vector_search_index WHERE document_id = :doc_id",
                {"doc_id": document_id},
            )

            # Delete from metadata
            result = self.query(
                "DELETE FROM _vector_metadata WHERE document_id = :doc_id",
                {"doc_id": document_id},
            )

            msg = f"[OK] Vector metadata deleted for document '{document_id}'"
            console.print(f"[green]{msg}[/green]" if RICH_AVAILABLE else msg)
            return msg

        except Exception as e:
            error_msg = f"[ERROR] Error deleting vector metadata: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # ═══════════════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════════════

    def _reflect_table(self, table_name: str) -> None:
        """Reflect a table from the database."""
        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            self.tables[table_name] = table
        except Exception as e:
            logger.warning(f"Could not reflect table '{table_name}': {e}")

    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return []

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        try:
            inspector = inspect(self.engine)
            return table_name in inspector.get_table_names()
        except Exception:
            return False

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table."""
        try:
            schema = self.get_schema(table_name)

            # Get row count
            count_result = self.query(
                f"SELECT COUNT(*) as count FROM {table_name}", fetch_all=False
            )
            row_count = (
                count_result.get("count", 0) if isinstance(count_result, dict) else 0
            )

            return {
                "name": table_name,
                "schema": schema.get(table_name, {}),
                "row_count": row_count,
                "exists": True,
            }
        except Exception as e:
            return {"name": table_name, "exists": False, "error": str(e)}

    def close(self) -> None:
        """Close all database connections."""
        try:
            self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def get_status(self) -> Dict[str, Any]:
        """Get current database status and statistics."""
        try:
            tables = self.list_tables()

            status = {
                "db_type": self.db_type.value,
                "connected": True,
                "tables_count": len(tables),
                "tables": tables,
                "connection_pool": {
                    "size": self.pool_size,
                    "max_overflow": self.max_overflow,
                },
            }

            if self.db_type == DatabaseType.SQLITE and self.database_path:
                db_path = Path(self.database_path)
                if db_path.exists():
                    status["database_size"] = db_path.stat().st_size
                    status["database_path"] = str(db_path)

            return status

        except Exception as e:
            return {"db_type": self.db_type.value, "connected": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION CLASSES
# ═══════════════════════════════════════════════════════════════════════════════


class DocumentSchemaManager(SchemaManager):
    """
    Specialized SchemaManager for DocumentAgent integration.

    Pre-configured with document-related tables and methods.
    """

    def __init__(self, **kwargs):
        """Initialize with document-specific configuration."""
        super().__init__(**kwargs)
        self._setup_document_tables()

    def _setup_document_tables(self) -> None:
        """Create default document tables."""
        # Documents table
        if not self.table_exists("documents"):
            self.create_table(
                "documents",
                {
                    "id": {
                        "type": "INTEGER",
                        "primary_key": True,
                        "autoincrement": True,
                    },
                    "document_id": {
                        "type": "TEXT",
                        "unique": True,
                        "not_null": True,
                        "index": True,
                    },
                    "title": {"type": "TEXT"},
                    "content_type": {"type": "TEXT", "index": True},
                    "file_path": {"type": "TEXT"},
                    "file_size": {"type": "INTEGER"},
                    "created_at": {"type": "DATETIME", "default": "CURRENT_TIMESTAMP"},
                    "updated_at": {"type": "DATETIME"},
                    "metadata": {"type": "JSON"},
                },
            )

        # Document chunks table (for vector storage)
        if not self.table_exists("document_chunks"):
            self.create_table(
                "document_chunks",
                {
                    "id": {
                        "type": "INTEGER",
                        "primary_key": True,
                        "autoincrement": True,
                    },
                    "document_id": {"type": "TEXT", "not_null": True, "index": True},
                    "chunk_index": {"type": "INTEGER", "not_null": True},
                    "chunk_text": {"type": "TEXT"},
                    "vector_id": {"type": "TEXT", "index": True},
                    "embedding_model": {"type": "TEXT"},
                    "created_at": {"type": "DATETIME", "default": "CURRENT_TIMESTAMP"},
                },
            )


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════


def example_usage():
    """Demonstrate SchemaManager usage."""
    print("\n" + "=" * 70)
    print("MR.VERMA Schema Manager - Example Usage")
    print("=" * 70 + "\n")

    # Initialize Schema Manager
    manager = SchemaManager(db_type="sqlite")

    # Define schema
    schema = {
        "users": {
            "id": {"type": "INTEGER", "primary_key": True, "autoincrement": True},
            "name": {"type": "TEXT", "not_null": True},
            "email": {"type": "TEXT", "unique": True, "index": True},
            "created_at": {"type": "DATETIME", "default": "CURRENT_TIMESTAMP"},
        }
    }

    # Create table
    print("1. Creating table 'users'...")
    result = manager.create_table("users", schema["users"])
    print(f"   Result: {result}\n")

    # Insert data
    print("2. Inserting data...")
    users_data = [
        {"name": "Alice Johnson", "email": "alice@example.com"},
        {"name": "Bob Smith", "email": "bob@example.com"},
        {"name": "Carol White", "email": "carol@example.com"},
    ]

    for user in users_data:
        result = manager.insert_data("users", user)
        print(f"   {result}")
    print()

    # Query data
    print("3. Querying data...")
    results = manager.query("SELECT * FROM users WHERE email LIKE '%@example.com'")
    print(f"   Found {len(results)} users:")
    for row in results:
        print(f"   - {row['name']} ({row['email']})")
    print()

    # Get schema
    print("4. Getting schema...")
    current_schema = manager.get_schema("users")
    print(f"   Schema: {json.dumps(current_schema, indent=2, default=str)}\n")

    # Store vector metadata
    print("5. Storing vector metadata...")
    result = manager.store_vector_metadata(
        document_id="doc_001",
        vector_location="vectors/embeddings_001.npy",
        embedding_dimension=384,
        metadata={"title": "Research Paper", "author": "Dr. Smith"},
        search_tags=["ai", "ml", "research"],
        category="academic",
    )
    print(f"   {result}\n")

    # Retrieve vector metadata
    print("6. Retrieving vector metadata...")
    metadata = manager.get_vector_metadata("doc_001")
    if isinstance(metadata, VectorMetadata):
        print(f"   Document: {metadata.document_id}")
        print(f"   Location: {metadata.vector_location}")
        print(f"   Dimension: {metadata.embedding_dimension}")
        print(f"   Metadata: {metadata.metadata}\n")

    # Migration example
    print("7. Performing schema migration...")
    changes = [
        SchemaChange(
            operation="add_column",
            table_name="users",
            column_name="age",
            column_def={"type": "INTEGER", "index": True},
        )
    ]
    results = manager.migrate_schema(changes)
    for result in results:
        print(f"   {result}")
    print()

    # Backup example
    print("8. Creating backup...")
    backup = manager.backup()
    if isinstance(backup, BackupInfo):
        print(f"   Backup created: {backup.backup_path}")
        print(f"   Size: {backup.size_bytes} bytes")
        print(f"   Tables: {', '.join(backup.tables)}\n")

    # Get database status
    print("9. Database status:")
    status = manager.get_status()
    print(f"   Type: {status['db_type']}")
    print(f"   Connected: {status['connected']}")
    print(f"   Tables: {status['tables_count']}")
    print(f"   Table List: {', '.join(status['tables'])}\n")

    # Close connection
    manager.close()
    print("[OK] Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    example_usage()
