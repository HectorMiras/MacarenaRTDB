# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 19:12:09 2021

@author: Usuario
"""


from pyorthanc import Orthanc
# from dicompylercore import dicomparser, dvh, dvhcalc
# import pydicom as dicom
import json
from datetime import datetime



def find_patient(orthanc_conect = None, patient_name = "", patient_id = "", study_date = ""):
    
    patients_identifiers = orthanc_conect.c_find({"Level" : "Patient", "Query" : {"PatientID" : patient_id, "PatientName":patient_name}})
    series_indentifiers = orthanc_conect.c_find({"Level" : "Study", "Query":{"StudyDate":study_date }})
    
    # paciente = Patient(orthanc_conect, '846fce0c-1dce6be6-381b8a21-d7e81af7-a3c5b231')
    #patient info = []
   

    
    for patient_identifier in patients_identifiers:
        patient_info=orthanc_conect.get_patient_information(patient_identifier)
        estudios=orthanc_conect.get_patient_studies_information(patient_identifier)
        paciente ={}
        paciente['ID'] = patient_info['ID']
        paciente['PatientID']= patient_info['MainDicomTags']['PatientID']
        paciente['PatientName']= patient_info['MainDicomTags']['PatientName']
        estudios_dat=[]
        for estudio in estudios:
            estudios_dic={}
            estudios_dic['ID'] = estudio['ID']
            estudios_dic['StudyDescription'] = estudio['MainDicomTags']['StudyDescription']
            estudios_dic['StudyInstanceUID'] = estudio['MainDicomTags']['StudyInstanceUID']
            estudios_dic['StudyDate'] = datetime.strptime((estudio['MainDicomTags']['StudyDate']),"%Y%m%d")
            
            series = orthanc_conect.get_study_series_information(estudio['ID'])
          
            series_dat =[]
            for serie in series:
                diccionario={}
                diccionario['serie_id'] = serie['ID']
                diccionario['modality'] = serie['MainDicomTags']['Modality']
                if serie['MainDicomTags']['Modality'] in ["RTDOSE","RTSTRUCT", "RTPLAN"]:
                    diccionario['Instance'] = serie['Instances']
                series_dat.append(diccionario)
            estudios_dic['series']= series_dat
        estudios_dat.append(estudios_dic)
    paciente['studies']= estudios_dat
    return paciente
            
orthanc = Orthanc('http://10.233.42.60:8042')   #'http://localhost:8042')
orthanc.setup_credentials('usuario', 'Radiofisica1')

# patient_id = 'AN0470990268'
# study_date = ""
# patient_name = ""

out = find_patient(orthanc_conect = orthanc, patient_name = '*BELLIDO*' )

# json_data = json.dumps(out,indent = 5)
# # print json data
# print("JSON Output with indentation: \n", json_data)
    
#estudios=paciente.information 846fce0c-1dce6be6-381b8a21-d7e81af7-a3c5b231
