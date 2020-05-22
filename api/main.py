from fastapi import FastAPI, File, Form, UploadFile, Response
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
import dataset
import datetime
from pydantic import BaseModel
import time
import os
from app.db.dbmodel import create_table


app = FastAPI()

app.mount("/files", StaticFiles(directory="files"), name="static")

mydb = os.environ['IC_DBPassword']+os.environ['IC_Database']

create_table()


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


@app.get("/status")
async def read_status(request: Request):
    return


"""post routes"""




@app.post("/upload_file/")
async def create_file(request: Request,file: UploadFile = File(...), token: str = Form(...)):
    if token != token:
        return {"error": 'bad token   ...'}
    if request.state.db['ic_files'].find_one(Filename = file.filename):
        return {"error": str(file.filename)+' allready exists ...'}
    folder = datetime.datetime.now()
    folder = str(folder.year)+'-'+str(folder.month)+'/'
    upload_folder = "files/"+folder
    request.state.db['ic_files'].insert(dict(
            s_Folder = upload_folder,
            s_Filename = file.filename,
            s_Created = datetime.datetime.now()))
    file_object = file.file
    os.makedirs(os.path.dirname(upload_folder), exist_ok=True)
    upload_folder = open(os.path.join(upload_folder, file.filename), 'wb+')
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    return {"fileurl": 'https://'+os.environ['VIRTUAL_HOST']+'/files/'+ folder+ file.filename}

"""put routes"""

