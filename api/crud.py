from sqlalchemy.orm import Session

import models


def get_config_by_id(db: Session, id: int):
    return db.query(models.Configuration).filter(
        models.Configuration.id == id
    ).first()


def get_config_by_filename(db: Session, filename: str):
    return db.query(models.Configuration).filter(
        models.Configuration.filename == filename
    ).first()


def get_configs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Configuration).offset(skip).limit(limit).all()


def del_config(db: Session, config_id: int):
    print('config_id', config_id)
    query = db.query(models.Configuration).filter(
        models.Configuration.id == config_id
    ).delete()
    db.commit()
    return query


def create_config(db: Session, filename: str):
    db_config = models.Configuration(filename=filename)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config
