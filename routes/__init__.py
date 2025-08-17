from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, DatabaseError


def user_query(db, Model, current_user):
    """Create a query scoped to a specific user."""
    try:
        user_id = current_user.id
        if user_id is not None and hasattr(Model, 'user_id'):
            return db.query(Model).filter(Model.user_id == user_id)
        else:
            raise DatabaseError(statement="User ID is required for models with user_id field"
                                , params=None, orig=Exception("User ID validation failed"))
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

def get_record(db, Model, _id, current_user):
    record = None
    query = user_query(db, Model, current_user=current_user)
    if hasattr(Model, 'id'):
        record = query.filter(Model.id == _id).first()
    elif hasattr(Model, 'number'):
        record = query.filter(Model.number == _id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Record for {Model.__name__} not found.")
    return record

def get_buyer_by_name_phone(db, name: str, phone: str, current_user):
    """Buscar comprador por nombre-teléfono único"""
    from models.buyer import Buyer
    buyer = db.query(Buyer).filter(
        Buyer.user_id == current_user.id,
        Buyer.name == name,
        Buyer.phone == phone
    ).first()

    if not buyer:
        raise HTTPException(status_code=404, detail=f"Buyer with name '{name}' and phone '{phone}' not found")

    return buyer

def get_records(db, Model, current_user, limit: int, offset: int = 0, filters = None, joins = None):
    """Get multiple records with limit and offset support, including complex JOINs."""
    query = user_query(db, Model, current_user=current_user)

    # Handle complex JOINs if specified
    if joins:
        for join_config in joins:
            if isinstance(join_config, dict):
                # Join with filter: {'model': RaffleSet, 'condition': Raffle.set_id == RaffleSet.id, 'filter': {'project_id': value}}
                join_model = join_config.get('model')
                join_condition = join_config.get('condition')
                join_filter = join_config.get('filter')

                if join_model and join_condition:
                    query = query.join(join_model, join_condition)
                    if join_filter:
                        for field_name, value in join_filter.items():
                            if value is not None and hasattr(join_model, field_name):
                                field = getattr(join_model, field_name)
                                query = query.filter(field == value)
            else:
                # Simple join: just the model
                query = query.join(join_config)

    # Handle regular filters on the main model
    if filters:
        # Handle both dict and schema objects
        filter_dict = filters.model_dump() if hasattr(filters, 'model_dump') else filters
        for field_name, value in filter_dict.items():
            if value is not None and hasattr(Model, field_name):
                field = getattr(Model, field_name)
                query = query.filter(field == value)

    # Apply ordering for raffles specifically (by number for easy sorting)
    if Model.__name__ == 'Raffle':
        query = query.order_by(Model.number)

    if offset > 0:
        query = query.offset(offset)
    if limit > 0:
        query = query.limit(limit)
    return query.all()

def create_record(db, new_record):
    """Create a new record in the database."""
    try:
        Model = new_record.__class__
        if hasattr(Model, 'user_id') and new_record.user_id is None:
            raise HTTPException(status_code=400, detail="user_id is required for this record type")
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Record already exists or violates constraints")

def update_record(db, Model, schema, current_user):
    record = None
    if hasattr(Model, 'id'):
        record = get_record(db, Model, schema.id, current_user)
    elif hasattr(Model, 'number'):
        record = get_record(db, Model, schema.number, current_user)

    for field, value in schema.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record

def delete_record(db, record, current_user):
    if hasattr(record, 'user_id') and current_user.id != record.user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this record")
    try:
        db.delete(record)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Record cannot be deleted. Error: " + str(e)
        )
    return {"message": "Record deleted successfully"}
