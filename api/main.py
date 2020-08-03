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

class resources(BaseModel):
    guid: str
    category: str
    url: str
    project: str

class keyid(BaseModel):
    id: int

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

@app.get("/get_users", dependencies=[Depends(verify_token)])
async def get_users(request: Request):
    result = request.state.db['wiki_users'].all()
    return {'result': [dict(row) for row in result]}

@app.get("/get_groups", dependencies=[Depends(verify_token)])
async def get_groups(request: Request):
    result = request.state.db['wiki_groups'].all()
    return {'result': [dict(row) for row in result]}

@app.get("/get_resources", dependencies=[Depends(verify_token)])
async def get_res(request: Request, item: resources):
    if item.guid == "0":
        result = request.state.db['ic_resources'].find(project = item.project)
    else:
        result = request.state.db['ic_resources'].find(guid = item.guid)
    res = []
    for row in result:
        res.append({'id':row['id'],
                'guid':row['guid'],
                'category':row['category'],
                'url':row['url'],
                'project':row['project']
                })
    return res


@app.get("/get_res_by_guid/{xguid}", dependencies=[Depends(verify_token)])
async def get_resi_by_guid(request: Request, xguid: str):
    result = request.state.db['ic_resources'].find(guid = xguid)
    res = []
    for row in result:
        res.append({'id':row['id'],
                'guid':row['guid'],
                'category':row['category'],
                'url':row['url'],
                'project':row['project']
                })
    return res

@app.get("/get_res_by_project/{xproject}", dependencies=[Depends(verify_token)])
async def get_resi_by_project(request: Request, xproject: str):
    result = request.state.db['ic_resources'].find(project = xproject)
    res = []
    for row in result:
        res.append({'id':row['id'],
                'guid':row['guid'],
                'category':row['category'],
                'url':row['url'],
                'project':row['project']
                })
    return res

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


@app.post("/add_res/", dependencies=[Depends(verify_token)])
async def add_res(request: Request, item: resources):
    resid = request.state.db['ic_resources'].insert(dict(
            guid = item.guid,
            category = item.category,
            url = item.url,
            project = item.project))
    print(resid)
    return {"resource added": resid}

@app.post("/del_res/", dependencies=[Depends(verify_token)])
async def del_res(request: Request, item: keyid):
    resid = request.state.db['ic_resources'].delete(
            id = item.id)
    print(resid)
    return {"resource removed": resid}

@app.post("/upload_file/", dependencies=[Depends(verify_token)])
async def create_file(request: Request,file: UploadFile = File(...)):
    folder = datetime.datetime.now()
    folder = str(folder.year)+'-'+str(folder.month)+'/'
    upload_folder = "files/"+folder
    latest_folder = "files/latest/"
    file_object = file.file
    os.makedirs(os.path.dirname(upload_folder), exist_ok=True)
    fullpath = os.path.join(latest_folder, file.filename)
    print(fullpath)
    upload_first = open(fullpath, 'wb+')
    shutil.copyfileobj(file_object, upload_first)
    upload_first.close()
    hist_filename = str(datetime.datetime.now().strftime("%d-%H-%M-")) + file.filename
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
            Folder = latest_folder,
            Filename = file.filename,
            Created = datetime.datetime.now(),
            Uploaded_by= 1))
    return {"file": 'https://'+os.environ['VIRTUAL_HOST']+'/files/latest'+ file.filename, "status":"newfile"}


@app.post("/files/", dependencies=[Depends(verify_token)])
async def create_file(file: bytes = File(...)):
        return {"file_size": len(file)}

@app.post("/post_ifc/{theproject}", dependencies=[Depends(verify_token)])
async def post_ifc(request: Request,theproject: str):
    folder = datetime.datetime.now()
    folder = str(folder.year)+'-'+str(folder.month)+'/'
    upload_folder = "files/"+folder
    latest_folder = "files/latest/"
    os.makedirs(os.path.dirname(upload_folder), exist_ok=True)
    fullpath = os.path.join(latest_folder, theproject)
    print(fullpath)
    with open(fullpath, 'wb') as up:
        file_object = await request.body()
        up.write(file_object)
    #shutil.copyfileobj(file_object, upload_first)
    hist_filename = str(datetime.datetime.now().strftime("%d-%H-%M-")) + theproject
    hist_fullpath = os.path.join(upload_folder, hist_filename)
    shutil.copyfile(fullpath,hist_fullpath)
    if not os.path.exists(fullpath) and os.path.exists(hist_fullpath):
        return {"file": "error while upload"}
    fileexists = request.state.db['ic_files'].find_one(Filename = theproject)
    if fileexists is not None:
        request.state.db['ic_file_history'].insert(dict(
                Orig_File = fileexists['id'],
                Folder = upload_folder,
                Filename = hist_filename,
                Created = datetime.datetime.now(),
                Uploaded_by= 1))
        return {"file": 'https://'+os.environ['VIRTUAL_HOST']+'/'+ upload_folder + hist_filename, "status":"updated"}
    request.state.db['ic_files'].insert(dict(
            Folder = latest_folder,
            Filename = theproject,
            Created = datetime.datetime.now(),
            Uploaded_by= 1))
    return {"file": 'https://'+os.environ['VIRTUAL_HOST']+'/files/latest/'+ theproject, "status":"newfile"}
"""put routes"""

