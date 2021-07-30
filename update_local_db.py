#pip install mysql-connector-python
import mysql.connector

#pip install requests
import requests

import urllib 
import gzip
import shutil
import ftplib
from datetime import datetime, timedelta
import os

def dd(misc):
    print(misc)
    input("\nPress any key to exit...")
    exit()


def clearDB():
    cursor.execute("SHOW TABLES")
    tables = [v for v in cursor]

    for x in tables:
        cursor.execute("DROP TABLE " + x[0])

def unzip(zip, output):
    with gzip.open(zip, 'rb') as f_in:
        with open(output, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def executeScriptsFromFile(filename):
    fd = open(filename, 'r', encoding="utf-8")
    sqlFile = fd.read()
    fd.close()
    
    sqlCommands = sqlFile.split(';')
    
    for command in sqlCommands:
        if command.rstrip() != '':
            cursor.execute(command)
        


def changeUsers(exceptionUsers):
    # make standard password for all users
    # the password is 'password'
    password = "$2y$10$Z1wC1ZrN.xb8WaZie861zu1u6bLkUXWdPuGaIZbhvFZIDuW2OQEz6"
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    i = 0
    for user in users:
        userEmail = user[3]
        userId = user[0]

        sql = "UPDATE users SET password = '" + password + "' WHERE id = '" + str(userId) + "'"
        cursor.execute(sql)

        if userEmail not in exceptionUsers:
            sql = "UPDATE users SET email = 'asd" + str(i) + "@asdasd.asdad', discord_user_id = NULL, discord_private_channel_id = NULL WHERE id = '" + str(userId) + "'"
            cursor.execute(sql)

        i += 1

def downloadDb(ftp, dbDir, username, passowrd):
    print("Downloading DB from server...")

    try:
        ftp = ftplib.FTP(ftp)
        ftp.login(username, passowrd)
        ftp.cwd(dbDir)

        files = ftp.nlst()

        dbToDownload = ''
        for file in files:
            if 'TMP' in file:
                dbToDownload = file

        ftp.retrbinary("RETR " + dbToDownload ,open(dbToDownload, 'wb').write)
    except:
        dd("Login rejected, please try again later.")

    print("Download finished.")
    return dbToDownload

# this will ask the server to make an updated DB backup file
def prepareRemoteDb(secretToken):
    print("Making temporary DB backup...")
    url = 'https://www.yourdomain.com/path/to/preparescript'
    myobj = {'secretToken': secretToken}

    response = requests.post(url, data = myobj)
    
    if response.text == "{\"data\":\"Resource not found\"}":
        dd("Fail to make remote DB, please try again later.")

    print("Done.")



#---------- all the good stuff start here ----------#

# sql connection and cursor init
try:
    mydb = mysql.connector.connect(
        host="hostname",
        user="username",
        password="password",
        database="database_name"
    )
    cursor = mydb.cursor()
except:
    dd("Error - cannot connect to local database.")


# options
sqlFileName = 'output.sql'
exceptionUsers = ['example1@example.com', 'example2@example.com', 'example2@example.com']


# prepare remote db Token
secretToken = ''


# ftp server info
ftp = 'yourdomain.com'
dbDir = '/path/to/db'
username = 'user@name.com'
passowrd = 'password'


# prepare remote DB
prepareRemoteDb(secretToken)


# download today's db and get it name
zipFile = downloadDb(ftp, dbDir, username, passowrd)


# unzip it and name it
unzip(zipFile, sqlFileName)


# drop all tables from db
clearDB()


# import the unzipped db
executeScriptsFromFile(sqlFileName)


# fake users emails, remove all discord info and change password with no exceptions
changeUsers(exceptionUsers)


# remove sql and zip file
os.remove(zipFile)
os.remove(sqlFileName)


dd('All have been done, now you can work without interrupt')




