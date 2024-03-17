import uvicorn
from fastapi import FastAPI, Request, File, UploadFile,Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import requests
import subprocess
from fastapi.responses import RedirectResponse
import psycopg2
from typing import Optional
import base64


conn = psycopg2.connect(
    dbname="blogdb",
    user="app",
    password="875GZ75iEz405xJl8xtlECl5",
    host="severely-pro-salmon.a1.pgedge.io",
    port="5432"
)



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "static"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

login_username=""
login_password=""

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/sports')
def index(request: Request):
    return templates.TemplateResponse("sports.html", {"request": request})

@app.get('/hackathon')
def index(request: Request):
    return templates.TemplateResponse("hackathon.html", {"request": request})
@app.get('/clubs')
def index(request: Request):
    return templates.TemplateResponse("clubs.html", {"request": request})
@app.get('/fests')
def index(request: Request):
    return templates.TemplateResponse("fests.html", {"request": request})
@app.get('/culturals')
def index(request: Request):
    return templates.TemplateResponse("culturals.html", {"request": request})

@app.get('/create')
def index(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.get('/index1')
def index(request: Request):
    cur = conn.cursor()
    cur.execute("SELECT * FROM details WHERE name = %s AND password1 = %s", (login_username, login_password))
    fetched_data = cur.fetchone()  # Assuming you expect only one row
    print(fetched_data)
    cur.close()

    return templates.TemplateResponse("index1.html", {"request": request})

@app.get('/about')
def about(request: Request):

    print(login_username + "res")
    print(login_password + "res")
     
    context = {
        "request": request,
        "name":login_username,
        "password":login_password,
    } 

    return templates.TemplateResponse("about.html", context)


@app.get('/login')
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get('/sign')
def sign(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/sign")
async def signup(
    request: Request, username: str = Form(...), email: str = Form(...),password: str = Form(...),password1:str = Form(...) 
):
   
    cur = conn.cursor()
    cur.execute("INSERT INTO details (name,email,password1,password2) VALUES (%s, %s,%s, %s)", (username,email,password,password1))
    conn.commit()
    cur.close() 
 
    return RedirectResponse("/login", status_code=303)



@app.post("/create")
async def create_post(request: Request, title: str = Form(...), category: str = Form(...), content: str = Form(...),image: UploadFile = File(...)):
    # Store the data in the PostgreSQL database
    cur = conn.cursor()
    cur.execute("INSERT INTO postdetail (category, title, matter) VALUES (%s, %s, %s)", (category, title, content))
    conn.commit()
    cur.close()


    with open(f"images/{image.filename}", "wb") as f:
        f.write(image.file.read())

    

    # Encode the image as base64 to include it in the context
    with open(f"images/{image.filename}", "rb") as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")


    # Construct the template filename based on the category
    template_filename = f"{category}.html"
    

    context = {
        "request": request,
        "title": title,
        "category": category,
        "content": content,
        "image_data": image_base64
    }

    return templates.TemplateResponse(template_filename, context)



@app.post("/login")
async def do_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    login_username=username
    login_password=password

    cur = conn.cursor()
    cur.execute("SELECT * FROM details WHERE name=%s and password1=%s", (username,password))
    existing_user = cur.fetchone()
    cur.close()
    
    if existing_user:
        print(existing_user)
        return RedirectResponse("/index1", status_code=303)
    
    else:
        return JSONResponse(status_code=401, content={"message": "Wrong credentials"})
    
    
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)