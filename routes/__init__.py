from fastapi import HTTPException


def get_record(db, Model, _id, model_name):
    record = db.query(Model).filter(Model.id == _id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"{model_name} not found")
    return record