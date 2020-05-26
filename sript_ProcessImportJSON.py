# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient
import os
from datetime import datetime
import json
import re # regular expressions
import os.path

loglines = []

def procesajson(dic):
    format_str = '%d/%m/%Y' # The format
    strdate = ''
    for x in list(dic):
        y = dic[x]
        # Convierte edad a entero
        try:
            if(x.lower()=='edad'):
                dic[x] = int(y.split()[0])        
            if isinstance(y,str):
                # convierte los string que son dígitos a enteros
                if y.isdigit():
                    dic[x]=int(y)
                # Convierte numeros decimales con coma a float
                if re.search(r'\d+,\d+',y):
                    y = y.replace(",",".")
                    dic[x]=float(y)
                # convierte fechas a variable datetime
                if re.search(r'^\d{1,2}\/\d{1,2}\/\d{4}$',y):
                    y = datetime.strptime(y, format_str)
                    dic[x]=y 
        except:
            loglines.append(f'Error processing {x}:{y}')
        # Elimina elementos vacios
        if y == u"\xa0":
            dic.pop(x,None)
        elif isinstance(y,list):
            for z in y:
                procesajson(z)
        elif isinstance(y,dict):
            procesajson(y)


def readFileListDirectory(dirName):
    data = {}
    with os.scandir(path=dirName) as dir_entries:
        for entry in dir_entries:       
            extension = os.path.splitext(entry)[1].lower()
            if(('json' in extension) and (entry.name.startswith('AN'))):
                info = entry.stat()
                mod_timestamp = datetime.fromtimestamp(info.st_mtime)
                data.update({entry.name: mod_timestamp.strftime("%d/%m/%Y %H:%M:%S")})
    return data

def readFileListCache(path, jfile):
    d = {}
    with open(path + jfile) as json_data:
        d = json.load(json_data)
    return d

def loadJSONToMongo(jsfile,mycollection):
    with open(jsfile) as json_data:
        d = json.load(json_data)
        procesajson(d)
        #pprint(jsfile)
        AN = d['ID']
        mycollection.delete_one({'ID': AN})
        paciente_id = mycollection.insert_one(d).inserted_id
        loglines.append(f'Se ha añadido el documento {paciente_id} a la coleccion' )

def main():
    client = MongoClient('mongodb://10.233.42.60:27017')
    db = client['local']
    pacientesRT = db['PacientesRT']
    path = 'C:\\Datos\\MosaiqMacarenaMongoDB\\ImportJSONData\\'
    jfile = 'FileListCache.json'
    directory = '\\\\se00sap04\\mosaiq_data\\DB\\ESCRIBE\\WKGroup\\SEVM\\db\\'
    logfile = path + 'log_import.log'
    today = datetime.today()
    loglines.append(' ')
    loglines.append(f'Log de la importación con fecha {today}')
    logfile_obj = open(logfile,mode='a')
    cacheData = readFileListCache(path=path, jfile=jfile)
    newData = readFileListDirectory(directory) 
    if cacheData != newData:
        for key in newData:
            if key in cacheData.keys():
                if datetime.strptime(newData[key], "%d/%m/%Y %H:%M:%S") > datetime.strptime(cacheData[key], "%d/%m/%Y %H:%M:%S"):
                    loglines.append(f'Fichero modificado. Llama a carga a mongo {key}')
                    loadJSONToMongo(directory+key,pacientesRT)
            else:
                loglines.append(f'Nuevo fichero. Llama a carga a mongo {key}')
                loadJSONToMongo(directory+key,pacientesRT)
        loglines.append("Diferentes")
        with open(path + jfile, "w") as json_data:
            json.dump(newData, json_data)
    else:
        loglines.append('No existen cambios en los ficheros')
    for line in loglines:
        logfile_obj.write(line)
        logfile_obj.write('\n')
        

main()