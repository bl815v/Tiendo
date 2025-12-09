from typing import List

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from data.database import get_db
from model.cliente import ClienteCreateDTO, ClienteDAO, ClienteDTO

router = APIRouter(prefix="/clientes", tags=["clientes"])

def hash_contrasena(contrasena: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(contrasena.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verificar_contrasena(contrasena: str, hashed: str) -> bool:
    """Verifica si una contraseña coincide con su hash"""
    return bcrypt.checkpw(contrasena.encode('utf-8'), hashed.encode('utf-8'))

@router.post("/", response_model=ClienteDTO, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: ClienteCreateDTO, db: Session = Depends(get_db)):
    # Verificar si el correo ya existe
    existing_cliente = (
        db.query(ClienteDAO).filter(ClienteDAO.correo == cliente.correo).first()
    )
    if existing_cliente:
        raise HTTPException(
            status_code=400, 
            detail="El correo ya está registrado"
        )
    
    # Crear diccionario con los datos del cliente
    cliente_data = cliente.model_dump()
    
    # Hashear la contraseña antes de almacenarla
    if 'contrasena' in cliente_data:
        cliente_data['contrasena'] = hash_contrasena(cliente_data['contrasena'])
    
    # Crear el objeto ClienteDAO
    db_cliente = ClienteDAO(**cliente_data)
    
    try:
        # Agregar a la base de datos
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        
        # Convertir a DTO para respuesta (excluye contraseña)
        return ClienteDTO.from_orm(db_cliente)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al crear cliente: {str(e)}"
        )

@router.get("/", response_model=List[ClienteDTO])
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clientes = db.query(ClienteDAO).offset(skip).limit(limit).all()
    return clientes

@router.get("/{cliente_id}", response_model=ClienteDTO)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDAO).filter(ClienteDAO.id_cliente == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@router.put("/{cliente_id}", response_model=ClienteDTO)
def actualizar_cliente(
    cliente_id: int, 
    cliente_update: ClienteCreateDTO, 
    db: Session = Depends(get_db)
):
    db_cliente = (
        db.query(ClienteDAO).filter(ClienteDAO.id_cliente == cliente_id).first()
    )
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Verificar si el nuevo correo ya existe (excepto si es el mismo cliente)
    if cliente_update.correo != db_cliente.correo:
        existing_cliente = (
            db.query(ClienteDAO)
            .filter(ClienteDAO.correo == cliente_update.correo)
            .first()
        )
        if existing_cliente:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # Actualizar campos
    for key, value in cliente_update.model_dump().items():
        if key == 'contrasena' and value:
            # Hashear nueva contraseña
            setattr(db_cliente, key, hash_contrasena(value))
        elif value is not None:
            setattr(db_cliente, key, value)
    
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.delete("/{cliente_id}")
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = (
        db.query(ClienteDAO).filter(ClienteDAO.id_cliente == cliente_id).first()
    )
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db.delete(db_cliente)
    db.commit()
    return {"message": "Cliente eliminado"}

# Endpoint para login (opcional, pero útil)
@router.post("/login")
def login_cliente(correo: str, contrasena: str, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDAO).filter(ClienteDAO.correo == correo).first()
    if not cliente:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if not verificar_contrasena(contrasena, cliente.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Aquí podrías generar un token JWT
    return {
        "message": "Login exitoso",
        "cliente_id": cliente.id_cliente,
        "nombre": cliente.nombre,
        "correo": cliente.correo
    }