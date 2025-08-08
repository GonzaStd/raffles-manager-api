from fastapi import HTTPException


def get_record(db, Model, _id, model_name, id_field="id"):
    """Get a record by ID or custom field name."""
    if id_field == "id":
        record = db.query(Model).filter(Model.id == _id).first()
    elif id_field == "number":
        record = db.query(Model).filter(Model.number == _id).first()
    else:
        # Generic approach for other field names
        field = getattr(Model, id_field)
        record = db.query(Model).filter(field == _id).first()

    if not record:
        raise HTTPException(status_code=404, detail=f"{model_name} not found")
    return record

def get_records(db, Model, limit: int):
    if limit > 0:
        return db.query(Model).order_by(Model.id.desc()).limit(limit).all().sort(reverse=True)
    elif limit == 0:
        return db.query(Model).all()
    else:
        raise HTTPException(
            status_code=400,
            detail="Limit must be a non-negative integer."
        )