from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    source_type = Column(String)  # "file", "url", "api"
    source_path = Column(String)  # file path or URL
    row_count = Column(Integer)
    column_count = Column(Integer)
    schema_json = Column(JSON)    # {col_name: dtype, ...}
    sample_json = Column(JSON)    # first 5 rows
    cleaning_log = Column(JSON)   # list of cleaning actions taken
    created_at = Column(DateTime, default=datetime.utcnow)
    sqlite_table_name = Column(String)  # the table this data lives in


class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    dataset_id = Column(String)
    preset = Column(String)        # "executive", "operational", "trend", "comparison"
    layout_json = Column(JSON)     # react-grid-layout positions
    tiles_json = Column(JSON)      # list of tile configs
    filters_json = Column(JSON)    # active filters
    role = Column(String)          # "ceo", "analyst", "marketing"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QueryMemory(Base):
    __tablename__ = "query_memory"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String)
    query_text = Column(Text)
    response_json = Column(JSON)
    embedding_id = Column(String)   # ID in FAISS index
    created_at = Column(DateTime, default=datetime.utcnow)


class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    action_type = Column(String)    # "chart_type_change", "axis_swap", "filter_add"
    from_value = Column(String)
    to_value = Column(String)
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String)
    target_column = Column(String)
    algorithm = Column(String)
    r2_score = Column(Float)
    mae = Column(Float)
    rmse = Column(Float)
    feature_importance = Column(JSON)  # {feature: importance_score}
    model_path = Column(String)        # path to pickled model
    created_at = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String, unique=True, nullable=False)  # report_YYYYMMDD_HHMMSS
    dashboard_id = Column(String, nullable=False)
    dataset_id = Column(String, nullable=False)
    format = Column(String)  # "pdf", "pptx", or "both"
    pdf_path = Column(String)
    pptx_path = Column(String)
    metadata_json = Column(JSON)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)


class DBConnection(Base):
    __tablename__ = "db_connections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    db_type = Column(String, nullable=False)  # "postgresql", "mysql", "sqlite"
    host = Column(String)
    port = Column(Integer)
    database = Column(String, nullable=False)
    username = Column(String)
    password = Column(String)  # In production, encrypt this!
    ssl = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
