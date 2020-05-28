import dataset
import os


mydb = 'mysql://root:'+os.environ['IC_DBPassword']+'@intercom-db/'+os.environ['IC_Database']

def create_table():
    db = dataset.connect(mydb,engine_kwargs={'pool_recycle': 3600})
    addtable = db['ic_users']
    addtable.create_column('Token', db.types.string(25))
    addtable.create_column('LastLogin', db.types.datetime)
    addtable.create_column('Role', db.types.string(6))

    addtable2 = db['ic_chat']
    addtable2.create_column('fromid', db.types.string(25))
    addtable2.create_column('toid', db.types.string(25))
    addtable2.create_column('text', db.types.text)
    addtable2.create_column('created', db.types.datetime)

    addtable3 = db['ic_files']
    addtable3.create_column('Filename', db.types.string(100))
    addtable3.create_column('Folder', db.types.string(100))
    addtable3.create_column('Created', db.types.datetime)
    addtable3.create_column('Uploaded_by', db.types.integer)

    db.executable.close()
    return
