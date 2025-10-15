from datetime import datetime, timezone
import uuid
from typing import Any, TypeVar, Generic, Type
from sqlmodel import Session, select
from sqlalchemy import func, or_

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
PatchSchemaType = TypeVar("PatchSchemaType")


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType, PatchSchemaType]):
    def get_multi_with_pagination(
        self,
        *,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        search_field: str | None = None,
        search_fields: list[str] | None = None,
        **filters
    ) -> tuple[list[ModelType], dict]:
        """Get paginated records and pagination info"""
        statement = select(self.model)
        count_statement = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                column = getattr(self.model, key)
                statement = statement.where(column == value)
                count_statement = count_statement.where(column == value)

        # Apply search filter if provided against single or multiple fields
        if search:
            # Determine fields to search: prefer provided list, else single field
            candidate_fields: list[str] = []
            if search_fields:
                candidate_fields = [f for f in search_fields if hasattr(self.model, f)]
            elif search_field and hasattr(self.model, search_field):
                candidate_fields = [search_field]

            if candidate_fields:
                conditions = []
                for field in candidate_fields:
                    column = getattr(self.model, field)
                    try:
                        conditions.append(column.ilike(f"%{search}%"))
                    except AttributeError:
                        # Fallback for case-insensitive match
                        conditions.append(func.lower(column).like(f"%{search.lower()}%"))

                if conditions:
                    or_clause = or_(*conditions)
                    statement = statement.where(or_clause)
                    count_statement = count_statement.where(or_clause)
        total = session.exec(count_statement).one()
        statement = statement.offset(skip).limit(limit)
        result = session.exec(statement).all()
        has_next = skip + limit < total
        has_prev = skip > 0
        pagination = {
            "total": total,
            "offset": skip,
            "limit": limit,
            "count": len(result),
            "has_next": has_next,
            "has_prev": has_prev
        }
        return result, pagination
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def create(self, *, session: Session, obj_in: CreateSchemaType, org_id: uuid.UUID | None = None) -> ModelType:
        # Attach organization id if provided and model supports it
        update_dict = {"org_id": org_id} if org_id is not None else {}
        db_obj = self.model.model_validate(obj_in, update=update_dict)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_multi(
        self, 
        *, 
        session: Session, 
        skip: int = 0, 
        limit: int = 100, 
        **filters
    ) -> list[ModelType]:
        """Get multiple records with pagination and optional filters"""
        statement = select(self.model)
        # Apply filters dynamically
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                column = getattr(self.model, key)
                statement = statement.where(column == value)
        
        statement = statement.offset(skip).limit(limit)
        result = session.exec(statement)
        return result.all()

    def patch(
        self, 
        *, 
        session: Session, 
        db_obj: ModelType, 
        obj_in: PatchSchemaType
    ) -> ModelType:
        """Partially update a record with a dictionary of fields"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_by_id(self, *, session: Session, obj_id: uuid.UUID, is_deleted: bool = False) -> ModelType | None:
        statement = select(self.model).where(self.model.uid == obj_id)
        db_obj = session.exec(statement).first()
        return db_obj

    def update(self, *, session: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> Any:
        update_data = obj_in.model_dump(exclude_unset=True)
        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete(self, *, session: Session, db_obj: ModelType):
        if getattr(db_obj, "is_deleted", False):
            raise ValueError("Item already deleted.")
        db_obj.is_deleted = True
        db_obj.deleted_at = datetime.now(timezone.utc)
        session.add(db_obj)
        session.commit()
    
    def hard_delete(self, *, session: Session, db_obj: ModelType):
        session.delete(db_obj)
        session.commit()
