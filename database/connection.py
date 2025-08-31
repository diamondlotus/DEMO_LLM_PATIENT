from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import os
import logging
from typing import Optional
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize database engine with connection pooling"""
        try:
            # Database configuration
            db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'database': os.getenv('DB_NAME', 'lotushealth'),
                'username': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'password'),
                'sslmode': os.getenv('DB_SSLMODE', 'prefer')
            }
            
            # Build connection string
            connection_string = (
                f"postgresql://{db_config['username']}:{db_config['password']}"
                f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
                f"?sslmode={db_config['sslmode']}"
            )
            
            # Create engine with connection pooling
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=10,  # Number of connections to maintain
                max_overflow=20,  # Additional connections when pool is full
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,  # Recycle connections after 1 hour
                echo=os.getenv('DB_ECHO', 'false').lower() == 'true'  # SQL logging
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a new database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    @contextmanager
    def get_db_session(self):
        """Context manager for database sessions with automatic cleanup"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def create_tables(self):
        """Create all database tables"""
        try:
            from .models import Base
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            from .models import Base
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    def get_connection_info(self) -> dict:
        """Get database connection information"""
        if not self.engine:
            return {"status": "not_initialized"}
        
        try:
            with self.engine.connect() as connection:
                # Get database info
                db_info = connection.execute(text("SELECT current_database(), current_user, version()"))
                db_name, db_user, db_version = db_info.fetchone()
                
                # Get connection pool info
                pool_info = {
                    "pool_size": self.engine.pool.size(),
                    "checked_in": self.engine.pool.checkedin(),
                    "checked_out": self.engine.pool.checkedout(),
                    "overflow": self.engine.pool.overflow()
                }
                
                return {
                    "status": "connected",
                    "database": db_name,
                    "user": db_user,
                    "version": db_version.split()[0] if db_version else "unknown",
                    "pool": pool_info
                }
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"status": "error", "error": str(e)}
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
def get_db() -> Session:
    """Get database session (for dependency injection)"""
    return db_manager.get_session()

def get_db_session():
    """Get database session context manager"""
    return db_manager.get_db_session()

def test_db_connection() -> bool:
    """Test database connection"""
    return db_manager.test_connection()

def create_db_tables():
    """Create database tables"""
    db_manager.create_tables()

def get_db_info() -> dict:
    """Get database information"""
    return db_manager.get_connection_info()
