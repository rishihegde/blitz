from sqlalchemy.orm import Session
from . import models, schemas

def acquire_resource_lock(db: Session, lock: schemas.Locks):
    lock_db = models.Locks(name=lock.name)
    db.add(lock_db)
    db.commit()
    db.refresh(lock_db)
    return lock_db

def release_resource_lock(db: Session, lock: schemas.Locks):
    lock_db = db.query(models.Locks).filter(models.Locks.name == lock.name).first()
    db.delete(lock_db)
    db.commit()
    return lock_db

def get_network(db: Session, network_name: str):
    return db.query(models.Networks).filter(models.Networks.name == network_name).first()

def get_networks(db: Session):
    return db.query(models.Networks).all()

def create_network(db: Session, network: schemas.NetworksCreate):
    network_db = models.Networks(name=network.name, vpc_id=network.vpc_id, plan_id=123, plan_state='', tf_state=network.tf_state, payload=network.payload)
    db.add(network_db)
    db.commit()
    db.refresh(network_db)
    return network_db

def delete_network(db: Session, network_name: str):
    network_db = get_network(db, network_name)
    if network_db:
        db.delete(network_db)
        db.commit()
        return network_db