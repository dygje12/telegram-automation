"""
Base CRUD operations with optimized queries
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import and_, asc, desc, or_
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session, joinedload, selectinload

ModelType = TypeVar("ModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class with optimized database operations
    """

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(
        self, db: Session, id: Any, eager_load: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """
        Get a single record by ID with optional eager loading
        """
        query = db.query(self.model)

        # Add eager loading if specified
        if eager_load:
            for relationship in eager_load:
                if hasattr(self.model, relationship):
                    query = query.options(selectinload(getattr(self.model, relationship)))

        return query.filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        eager_load: Optional[List[str]] = None,
    ) -> List[ModelType]:
        """
        Get multiple records with filtering, pagination, and eager loading
        """
        query = db.query(self.model)

        # Add eager loading if specified
        if eager_load:
            for relationship in eager_load:
                if hasattr(self.model, relationship):
                    query = query.options(selectinload(getattr(self.model, relationship)))

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, field).in_(value))
                    elif isinstance(value, dict):
                        # Support for range queries
                        if "gte" in value:
                            query = query.filter(getattr(self.model, field) >= value["gte"])
                        if "lte" in value:
                            query = query.filter(getattr(self.model, field) <= value["lte"])
                        if "like" in value:
                            query = query.filter(
                                getattr(self.model, field).like(f"%{value['like']}%")
                            )
                    else:
                        query = query.filter(getattr(self.model, field) == value)

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            if order_desc:
                query = query.order_by(desc(getattr(self.model, order_by)))
            else:
                query = query.order_by(asc(getattr(self.model, order_by)))

        return query.offset(skip).limit(limit).all()

    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering
        """
        query = db.query(self.model)

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, field).in_(value))
                    elif isinstance(value, dict):
                        if "gte" in value:
                            query = query.filter(getattr(self.model, field) >= value["gte"])
                        if "lte" in value:
                            query = query.filter(getattr(self.model, field) <= value["lte"])
                        if "like" in value:
                            query = query.filter(
                                getattr(self.model, field).like(f"%{value['like']}%")
                            )
                    else:
                        query = query.filter(getattr(self.model, field) == value)

        return query.count()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        Delete a record by ID
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def bulk_create(self, db: Session, *, objs_in: List[CreateSchemaType]) -> List[ModelType]:
        """
        Bulk create multiple records efficiently
        """
        db_objs = []
        for obj_in in objs_in:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db_objs.append(db_obj)

        db.bulk_save_objects(db_objs, return_defaults=True)
        db.commit()
        return db_objs

    def bulk_update(self, db: Session, *, updates: List[Dict[str, Any]]) -> None:
        """
        Bulk update multiple records efficiently
        """
        db.bulk_update_mappings(self.model, updates)
        db.commit()

    def exists(self, db: Session, *, filters: Dict[str, Any]) -> bool:
        """
        Check if a record exists with given filters
        """
        query = db.query(self.model)

        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)

        return query.first() is not None

    def get_or_create(
        self, db: Session, *, defaults: Optional[Dict[str, Any]] = None, **kwargs
    ) -> tuple[ModelType, bool]:
        """
        Get an existing record or create a new one
        Returns (object, created) tuple
        """
        obj = db.query(self.model).filter_by(**kwargs).first()

        if obj:
            return obj, False

        # Create new object
        create_data = {**kwargs}
        if defaults:
            create_data.update(defaults)

        obj = self.model(**create_data)
        db.add(obj)
        db.commit()
        db.refresh(obj)

        return obj, True
