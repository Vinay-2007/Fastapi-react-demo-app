from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import product
from database import SessionLocal,engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)

database_models.Base.metadata.create_all(bind=engine)

@app.get("/")
def greet():
    return "This is my demo project for fastapi learning"

products=[
    product(id=1, name="Laptop", description="This is a laptop", price=1000.0, quantity=10),
    product(id=2, name="Phone", description="This is a phone", price=500.0, quantity=20),
    product(id=3, name="Tablet", description="This is a tablet", price=300.0, quantity=15),
    product(id=4, name="Monitor", description="This is a monitor", price=200.0, quantity=5)
]

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    db=SessionLocal()
    count=db.query(database_models.product).count()
    if count==0:
        for product in products:
            db.add(database_models.product(**product.model_dump()))
        db.commit() 
init_db()

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    db_products = db.query(database_models.product).all()

    #no need of this as we are using in memory data
    #db connection
    #db=SessionLocal()
    #writing query
    #db.query()

    return db_products

@app.get("/products/{id}")
def get_product_by_id(id: int,db: Session = Depends(get_db)):
    db_products=db.query(database_models.product).filter(database_models.product.id==id).first()
    if db_products:
            return db_products
    return "Product not found"

@app.post("/products")
def add_product(product: product,db: Session = Depends(get_db)):
    db.add(database_models.product(**product.model_dump()))
    db.commit()
    return product

@app.put("/products/{id}")
def update_product(id:int,product: product,db: Session = Depends(get_db)):
    db_product = db.query(database_models.product).filter(database_models.product.id == id).first()
    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return "Product updated successfully"
    else:
        return "Product not found"

@app.delete("/products/{id}")
def delete_product(id:int,db: Session = Depends(get_db)):
    product = db.query(database_models.product).filter(database_models.product.id == id).first()
    if product:
        db.delete(product)
        db.commit()
        return "Product deleted successfully"
    else:
        return "Product not found"