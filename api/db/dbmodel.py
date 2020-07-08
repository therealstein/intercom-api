import dataset
import os


mydb = 'mysql://root:'+os.environ['IC_DBPassword']+'@intercom-db/'+os.environ['IC_Database']

def create_table():
    db = dataset.connect(mydb,engine_kwargs={'pool_recycle': 3600})
    addtable = db['apiKeys']
    addtable.create_column('Name', db.types.string(25))
    addtable.create_column('Key', db.types.text)
    addtable.create_column('LastLogin', db.types.datetime)
    addtable.create_column('Expiration', db.types.datetime)

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

    addtable4 = db['ic_file_history']
    addtable4.create_column('Orig_File', db.types.integer)
    addtable4.create_column('Filename', db.types.string(100))
    addtable4.create_column('Folder', db.types.string(100))
    addtable4.create_column('Created', db.types.datetime)
    addtable4.create_column('Uploaded_by', db.types.integer)

    addtable5 = db['wiki_users']
    addtable5.create_column('wiki_id', db.types.integer)
    addtable5.create_column('email', db.types.string(250))
    addtable5.create_column('name', db.types.string(250))

    addtable6 = db['wiki_groups']
    addtable6.create_column('wiki_id', db.types.integer)
    addtable6.create_column('name', db.types.string(250))

    addtable7 = db['ic_resources']
    addtable7.create_column('guid', db.types.integer)
    addtable7.create_column('category', db.types.string(250))
    addtable7.create_column('url', db.types.string(2500))
    addtable7.create_column('project', db.types.string(250))

    db.executable.close()
    return
