"""
Database plugin for CMS using PostgreSQL
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.cms.plugins.base import BasePlugin
from app.db.models import Content as ContentModel
from app.db.base import SessionLocal


class DatabasePlugin(BasePlugin):
    """Plugin for database-based content storage using PostgreSQL"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.connected = False
        self.db: Optional[Session] = None
    
    async def connect(self) -> bool:
        """Connect to the database"""
        if not self.db:
            self.db = SessionLocal()
        self.connected = True
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from the database"""
        if self.db:
            self.db.close()
            self.db = None
        self.connected = False
        return True
    
    def _get_db(self) -> Session:
        """Get database session"""
        if not self.db:
            self.db = SessionLocal()
        return self.db
    
    async def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID from database"""
        if not self.connected:
            await self.connect()
        
        db = self._get_db()
        content = db.query(ContentModel).filter(ContentModel.id == content_id).first()
        if not content:
            return None
        
        return {
            "id": content.id,
            "title": content.title,
            "body": content.body,
            "metadata": content.metadata or {},
            "created_at": content.created_at.isoformat() if content.created_at else datetime.utcnow().isoformat(),
            "updated_at": content.updated_at.isoformat() if content.updated_at else datetime.utcnow().isoformat(),
            "plugin": content.plugin or "database"
        }
    
    async def create_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new content in database"""
        if not self.connected:
            await self.connect()
        
        db = self._get_db()
        content_id = content_data.get("id") or f"db_{datetime.utcnow().timestamp()}"
        
        db_content = ContentModel(
            id=content_id,
            title=content_data.get("title", ""),
            body=content_data.get("body", ""),
            metadata=content_data.get("metadata", {}),
            plugin="database"
        )
        db.add(db_content)
        db.commit()
        db.refresh(db_content)
        
        return {
            "id": db_content.id,
            "title": db_content.title,
            "body": db_content.body,
            "metadata": db_content.metadata or {},
            "created_at": db_content.created_at.isoformat() if db_content.created_at else datetime.utcnow().isoformat(),
            "updated_at": db_content.updated_at.isoformat() if db_content.updated_at else datetime.utcnow().isoformat(),
            "plugin": db_content.plugin or "database"
        }
    
    async def update_content(self, content_id: str, content_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing content in database"""
        if not self.connected:
            await self.connect()
        
        db = self._get_db()
        content = db.query(ContentModel).filter(ContentModel.id == content_id).first()
        if not content:
            return None
        
        if "title" in content_data:
            content.title = content_data["title"]
        if "body" in content_data:
            content.body = content_data["body"]
        if "metadata" in content_data:
            content.metadata = {**(content.metadata or {}), **content_data["metadata"]}
        
        db.commit()
        db.refresh(content)
        
        return {
            "id": content.id,
            "title": content.title,
            "body": content.body,
            "metadata": content.metadata or {},
            "created_at": content.created_at.isoformat() if content.created_at else datetime.utcnow().isoformat(),
            "updated_at": content.updated_at.isoformat() if content.updated_at else datetime.utcnow().isoformat(),
            "plugin": content.plugin or "database"
        }
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from database"""
        if not self.connected:
            await self.connect()
        
        db = self._get_db()
        content = db.query(ContentModel).filter(ContentModel.id == content_id).first()
        if not content:
            return False
        
        db.delete(content)
        db.commit()
        return True
    
    async def list_content(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all content from database with pagination"""
        if not self.connected:
            await self.connect()
        
        db = self._get_db()
        contents = db.query(ContentModel).offset(offset).limit(limit).all()
        
        return [
            {
                "id": content.id,
                "title": content.title,
                "body": content.body,
                "metadata": content.metadata or {},
                "created_at": content.created_at.isoformat() if content.created_at else datetime.utcnow().isoformat(),
                "updated_at": content.updated_at.isoformat() if content.updated_at else datetime.utcnow().isoformat(),
                "plugin": content.plugin or "database"
            }
            for content in contents
        ]
    
    async def search_content(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search content in database"""
        if not self.connected:
            await self.connect()
        
        db = self._get_db()
        contents = db.query(ContentModel).filter(
            (ContentModel.title.ilike(f"%{query}%")) | 
            (ContentModel.body.ilike(f"%{query}%"))
        ).limit(limit).all()
        
        return [
            {
                "id": content.id,
                "title": content.title,
                "body": content.body,
                "metadata": content.metadata or {},
                "created_at": content.created_at.isoformat() if content.created_at else datetime.utcnow().isoformat(),
                "updated_at": content.updated_at.isoformat() if content.updated_at else datetime.utcnow().isoformat(),
                "plugin": content.plugin or "database"
            }
            for content in contents
        ]
