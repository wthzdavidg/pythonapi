from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from database import SessionLocal,ExerciseDB

app = FastAPI(title="API")

class ExerciseCreate(BaseModel):
    name:str = Field(min_length=1,max_length=100)
    sets : int = Field(gt=0)
    reps : int = Field(gt=0)
    weight_kg:float = Field(ge=0)

###Método que inicializa las sesiones
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

###Comprobar estado
@app.get("/")
def health_check():
    return {"status":"ok","message":"API funcionando"}

###Añadir un ejercicio
@app.post("/exercises")
def add_exercise(exercise:ExerciseCreate,db:Session = Depends(get_db)):
    new_exercise = ExerciseDB(**exercise.model_dump())
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return {"message":"Ejercicio registrado","data":new_exercise}

###Ver todos los ejercicios
@app.get("/exercises")
def get_exercises(db:Session = Depends(get_db)):
    workouts = db.query(ExerciseDB).all()
    return {"total":len(workouts),"exercises":workouts}

###Ver un ejercicio
@app.get("/exercises/{id}")
def get_exercise(id:int,db:Session = Depends(get_db)):
    exercise = db.get(ExerciseDB,id)
    if exercise is None:
        raise HTTPException(status_code=404,detail="Ejercicio no encontrado")
    return {"exercise":exercise}

###Borrar un ejercicio
@app.delete("/exercises/{id}")
def delete_exercise(id:int, db:Session = Depends(get_db)):
    exercise = db.get(ExerciseDB,id)
    if exercise is None:
        raise HTTPException(status_code=404,detail="Ejercicio no encontrado")
    db.delete(exercise)
    db.commit()
    return {"message":f"Ejercicio {exercise.name} borrado correctamente"}

@app.put("/exercises/{id}")
def modify_exercise(id:int,data:ExerciseCreate, db:Session = Depends(get_db)):
    exercise = db.get(ExerciseDB,id)
    if exercise is None:
        raise HTTPException(status_code=404,detail="Ejercicio no encontrado")
    exercise.name = data.name
    exercise.reps = data.reps
    exercise.sets = data.sets
    exercise.weight_kg = data.weight_kg
    db.commit()
    return {"message":f"Ejercicio {exercise.name} modificado correctamente"}