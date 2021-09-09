import os
import shutil
import earthpy as et

def setHomeDirectory():
    if os.path.exists(et.io.HOME):
     et.io.HOME
    else:
        print("Home directory not found")
        
# Create the directory Staging for storage of pdfs
def CreateStagingDirectory():
    setHomeDirectory()
    stagingpath=os.path.join(os.getcwd(),'Staging')
    try: 
        os.mkdir(stagingpath)
    except OSError as error:    
        print(error) #Should include something else here to do if there is an error ? Maybe prompt user to rename the directory they have with the same name 

def setStagingDirectory():
    setHomeDirectory()
    stagingpath=os.path.join(os.getcwd(),'Staging')
    if os.path.exists(stagingpath):
     os.chdir(stagingpath)
    else:
        print("Staging directory not found")

def CreateStorageDirectory():
    setHomeDirectory()
    storagepath=os.path.join(os.getcwd(),'Storage')
    try: 
        os.mkdir(storagepath)
    except OSError as error:    
        print(error) #Should include something else here to do if there is an error ? Maybe prompt user to rename the directory they have with the same name 

def MoveFilesToStorage():
    setHomeDirectory()
    storagepath=os.path.join(os.getcwd(),'Storage')
    setStagingDirectory()
    files=os. listdir()
    for f in files:
        shutil.move(f, storagepath)
    
def DeleteStaggingFiles():
    setStagingDirectory()
    files=os.listdir()
    for f in files:
        os.remove(f)
    #Add a check here to see if all files were deleted using os.listdir()