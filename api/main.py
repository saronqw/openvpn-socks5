from fastapi import Depends, FastAPI, File, Response, UploadFile, \
    HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import models
from database import SessionLocal, engine
from schemas import ConfigurationBase, Configuration, Container
import utils

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/configs/{config_id}/",
    response_model=Configuration,
    responses={
        404: {"description": "Config Not Found"}
    }
)
async def read_config(config_id: int, db: Session = Depends(get_db)):
    db_config = crud.get_config_by_id(db, config_id)
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config with id equals {config_id} does not exist"
        )
    config = crud.get_config_by_id(db, config_id)
    return config


@app.get("/configs/", response_model=List[Configuration], )
async def read_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    configs = crud.get_configs(db, skip=skip, limit=limit)
    return configs


@app.post(
    "/configs/",
    status_code=status.HTTP_201_CREATED,
    responses={400: {}}
)
async def create_config(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):
    configs = crud.get_configs(db)
    for config in configs:
        if config.filename == file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Such config already exists"
            )

    if file.filename.split('.')[-1] != 'ovpn':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension"
        )

    db_config = crud.get_config_by_filename(db, filename=file.filename)
    if db_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Config already created"
        )

    utils.create_config_file(file)
    return crud.create_config(db=db, filename=file.filename)


@app.delete(
    "/configs/{config_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Config Not Found"}
    }
)
async def delete_config(config_id: int, db: Session = Depends(get_db)):
    config: Configuration = crud.get_config_by_id(db, config_id)
    completed = crud.del_config(db, config_id)

    if not completed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config with id equal {config_id} does not exist"
        )

    utils.delete_config_file(config)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@app.get(
    "/containers/{container_id}/",
    response_model=Container,
    responses={
        404: {"description": "Container Not Found"}
    }
)
async def read_container(container_id: str):
    container = utils.get_info_container_by_id(container_id)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container with id {container_id} does not exist"
        )
    return container


@app.get("/containers/", response_model=List[Container])
async def read_containers():
    return utils.get_info_containers()


@app.post(
    "/containers/",
    response_model=Container,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Config Not Found"}
    }
)
async def create_container(
    config: ConfigurationBase,
    db: Session = Depends(get_db),
):
    db_config = crud.get_config_by_filename(db, filename=config.filename)
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config with filename {config.filename} does not exist"
        )

    return utils.create_containter(config.filename)


@app.delete(
    "/containers/{container_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Container Not Found"}
    }
)
async def delete_container(container_id: str, db: Session = Depends(get_db)):
    container = utils.get_info_container_by_id(container_id)

    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container with id equal {container_id} does not exist"
        )

    utils.delete_container_by_id(container_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
