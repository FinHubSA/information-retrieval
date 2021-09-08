#Question: Do you want me to make this whole thing a module or lots of submodules ? 

#Import libaries
import os
import shutil
import earthpy as et

#Make a directory in any os system's home directory 
et.io.HOME
#os.path.exists(et.io.HOME) #a check to see if making it was successful 
aronspath=os.path.join(et.io.HOME, "arons-kit")#Make the main directory called arons-kit in home directory 

os.mkdir(aronspath)# need to do some conditional statements here if the directory already exists.
os.chdir(aronspath)#change path to this directory 
mainpath=os.getcwd()#fetches user's working directory 

#Could make this a function so its a bit cleaner ? 
# Create the sub-directory Staging
stagingpath=os.path.join(mainpath,'Staging') # staging directory path 
try: 
    os.mkdir(stagingpath)
except OSError as error: 
    print(error) #Should include something else here to do if there is an error ? Maybe prompt user to rename the directory they have with the same name 
  
storagepath = os.path.join(mainpath,"Storage")#Sotrage path - will be replaced later once connected to database 

try: 
    os.mkdir(storagepath) 
except OSError as error: 
    print(error) 
         
 #This is where it will then scrape and move files into staging 
 #Then we will check files against the database, so a query would go here 
 #Then if they meet a condition we move them across 

#os.chdir(stagingpath)

#files=os. listdir()
#for f in files:
    #Check if we need file 
    #if we do then move it, if not then don't (simple if else)
    #shutil.move(f, storagepath)       
        
os.chdir(stagingpath) #so we can delete the directory 
files=os.listdir()
for f in files:
    os.remove(f)

os.chdir(storagepath)#won't be necessary in future itterations
files=os.listdir()
for f in files:
    os.remove(f)
    
#Not letting me do this. Maybe it's okay if we don't delete the directory on the assumption that the user will help us again and thus won't mind having an empty directory, so we need to add an error check in the begining so that if the directory exists it won't make another one/ throw an error
#os.remove(stagingpath)
#os.remove(storagepath)
#os.remove(aronspath) #once all the files are gone, try delete the whole directory.