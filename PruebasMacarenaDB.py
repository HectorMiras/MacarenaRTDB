from pymongo import MongoClient
import datetime
import FuncRepo

def main():
    client = MongoClient('mongodb://10.233.42.60:27017') # Establece una conexión a MongoDB
    db = client['local'] # Seleccionamos la base de datos "local".
    pacientes = db['PacientesRT'] # Seleccionamos la colección "PacientesRT", que está dentro de la base de datos local

    start_date = datetime.datetime(2020, 1, 1, 0, 0, 0)
    end_date = datetime.datetime(2020, 3, 31, 0, 0, 0)

    lista_pacientes_problemas = FuncRepo.consulta_pacientes_problemas(pacientes, start_date, end_date)

    lista_pacientes_estadistica_planis = FuncRepo.consulta_estadisticas_planificaciones(pacientes, start_date, end_date)

    lista_pacientes_SBRT = FuncRepo.consulta_SBRTs(pacientes, start_date, end_date)

    lista_iniciosTto = FuncRepo.consulta_iniciosTto(pacientes, start_date, end_date)

    FuncRepo.calculo_demoras(pacientes, start_date, end_date)

if __name__ == '__main__':
    main()