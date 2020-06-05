from fastapi import FastAPI, Depends, Header, HTTPException, File, Form, UploadFile, Response
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
import dataset
import datetime
from pydantic import BaseModel
import time
import tempfile, shutil, os
from random import randrange
from app.db.dbmodel import create_table


app = FastAPI()

app.mount("/files", StaticFiles(directory="files"), name="static")

mydb = 'mysql://root:'+os.environ['IC_DBPassword']+'@intercom-db/'+os.environ['IC_Database']

create_table()



class apiKeys(BaseModel):
    Name: str
    Key: str

class getFilename(BaseModel):
    filename: str

"""token check"""
async def verify_token(request: Request, token: str = Header(...)):
    print(token)
    if not request.state.db['apiKeys'].find_one(Key = token):
        raise HTTPException(status_code=400, detail="X-Token header invalid")
"""init"""

@app.middleware("http")
async def add_process_time_header(request: Request,
                                    call_next,
                                    Authorization: str = Header(...) ):
    start_time = time.time()
    request.state.db = dataset.connect(mydb,engine_kwargs={'pool_recycle': 3600})
    response = await call_next(request)
    request.state.db.executable.close()
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response



"""get routes"""



@app.get("/list_apikeys", dependencies=[Depends(verify_token)])
async def list_apikeys(request: Request):
    result = request.state.db['apiKeys'].all()
    return {'result': [dict(row) for row in result]}


@app.get("/list_chat", dependencies=[Depends(verify_token)])
async def list_chat(request: Request):
    result = request.state.db['ic_chat'].all()
    return {'result': [dict(row) for row in result]}

@app.get("/get_files", dependencies=[Depends(verify_token)])
async def get_files(request: Request):
    result = request.state.db['ic_files'].all()
    f = []
    for row in result:
        f.append({'filename':row['Filename'],
                'fileurl':'https://'+os.environ['VIRTUAL_HOST']+'/'+row['Folder']+row['Filename']})
    return f

@app.get("/get_filehistory", dependencies=[Depends(verify_token)])
async def get_filehistory(request: Request, item: getFilename):
    fileexists = request.state.db['ic_files'].find_one(Filename = item.filename)
    if fileexists is not None:
        result = request.state.db['ic_file_history'].find(Orig_File = fileexists['id'])
        fh = []
        for row in result:
            fh.append({'Created':row['Created'],
                    'fileurl':'https://'+os.environ['VIRTUAL_HOST']+'/'+row['Folder']+row['Filename']})
        return fh
    return {'error' :'No filehistory for '+item.filename+' found'}
"""post routes"""

"""@app.post("/add_apikey")
async def add_apikey(request: Request, item: apiKeys):
    if request.state.db['apiKeys'].find_one(Key = item.Key):
        return {"error": str(item.Key)+' allready exists ...'}
    tokenid = request.state.db['apiKeys'].insert(dict(
        Key = item.Key,
        Name = item.Name))
    return {"id" : tokenid}"""



@app.post("/upload_file/", dependencies=[Depends(verify_token)])
async def create_file(request: Request,file: UploadFile = File(...)):
    folder = datetime.datetime.now()
    folder = str(folder.year)+'-'+str(folder.month)+'/'
    upload_folder = "files/"+folder
    file_object = file.file
    os.makedirs(os.path.dirname(upload_folder), exist_ok=True)
    fullpath = os.path.join(upload_folder, file.filename)
    print(fullpath)
    upload_first = open(fullpath, 'wb+')
    shutil.copyfileobj(file_object, upload_first)
    upload_first.close()
    hist_filename = str(datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S-")) + file.filename
    hist_fullpath = os.path.join(upload_folder, hist_filename)
    shutil.copyfile(fullpath,hist_fullpath)
    if not os.path.exists(fullpath) and os.path.exists(hist_fullpath):
        return {"file": "error while upload"}
    fileexists = request.state.db['ic_files'].find_one(Filename = file.filename)
    if fileexists is not None:
        request.state.db['ic_file_history'].insert(dict(
                Orig_File = fileexists['id'],
                Folder = upload_folder,
                Filename = hist_filename,
                Created = datetime.datetime.now(),
                Uploaded_by= 1))
        return {"file": 'https://'+os.environ['VIRTUAL_HOST']+'/files/'+ folder+ file.filename, "status":"updated"}
    print(file.filename)
    request.state.db['ic_files'].insert(dict(
            Folder = upload_folder,
            Filename = file.filename,
            Created = datetime.datetime.now(),
            Uploaded_by= 1))
    return {"file": 'https://'+os.environ['VIRTUAL_HOST']+'/files/'+ folder+ file.filename, "status":"newfile"}

"""put routes"""

