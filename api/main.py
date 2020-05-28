from fastapi import FastAPI, Depends, Header, HTTPException, File, Form, UploadFile, Response
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
import dataset
import datetime
from pydantic import BaseModel
import time
import tempfile, shutil, os
from app.db.dbmodel import create_table


app = FastAPI()

app.mount("/files", StaticFiles(directory="files"), name="static")

mydb = 'mysql://root:'+os.environ['IC_DBPassword']+'@intercom-db/'+os.environ['IC_Database']

create_table()



class Users(BaseModel):
    Token: str
    Role: str



"""token check"""
async def verify_token(request: Request, token: str = Header(...)):
    if not request.state.db['ic_users'].find_one(Token = token):
        raise HTTPException(status_code=400, detail="X-Token header invalid")
"""init"""

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    request.state.db = dataset.connect(mydb,engine_kwargs={'pool_recycle': 3600})
    response = await call_next(request)
    request.state.db.executable.close()
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response



"""get routes"""



@app.get("/list_users", dependencies=[Depends(verify_token)])
async def list_users(request: Request):
    result = request.state.db['ic_users'].all()
    return {'result': [dict(row) for row in result]}


@app.get("/list_chat", dependencies=[Depends(verify_token)])
async def list_chat(request: Request):
    result = request.state.db['ic_chat'].all()
    return {'result': [dict(row) for row in result]}

@app.get("/list_files", dependencies=[Depends(verify_token)])
async def list_files(request: Request):
    result = request.state.db['ic_files'].all()
    return {'result': [dict(row) for row in result]}

"""post routes"""

@app.post("/add_token")
async def add_usr(request: Request, item: Users):
    if request.state.db['ic_users'].find_one(Token = item.Token):
        return {"error": str(item.Token)+' allready exists ...'}
    tokenid = request.state.db['ic_users'].insert(dict(
        Token = item.Token,
        Role = item.Role))
    return {"id" : tokenid}



@app.post("/upload_file/", dependencies=[Depends(verify_token)])
async def create_file(request: Request,file: UploadFile = File(...), token: str = Header(...)):
    res = request.state.db['ic_users'].find_one(Token = token)
    user_id = res['id']
    if request.state.db['ic_files'].find_one(Filename = file.filename):
        return {"error": str(file.filename)+' allready exists ...'}
    folder = datetime.datetime.now()
    folder = str(folder.year)+'-'+str(folder.month)+'/'
    upload_folder = "files/"+folder
    request.state.db['ic_files'].insert(dict(
            Folder = upload_folder,
            Filename = file.filename,
            Created = datetime.datetime.now(),
            Uploaded_by= user_id))
    file_object = file.file
    os.makedirs(os.path.dirname(upload_folder), exist_ok=True)
    upload_folder = open(os.path.join(upload_folder, file.filename), 'wb+')
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    return {"fileurl": 'https://'+os.environ['VIRTUAL_HOST']+'/files/'+ folder+ file.filename}

"""put routes"""

