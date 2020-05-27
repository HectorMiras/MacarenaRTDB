from pymongo import MongoClient
import datetime
import FuncRepo
import pandas
import numpy as np

def main():
    client = MongoClient('mongodb://10.233.42.60:27017') # Establece una conexión a MongoDB
    db = client['local'] # Seleccionamos la base de datos "local".
    pacientes = db['PacientesRT'] # Seleccionamos la colección "PacientesRT", que está dentro de la base de datos local

    start_date = datetime.datetime(2020, 1, 1, 0, 0, 0)
    end_date = datetime.datetime(2020, 3, 31, 0, 0, 0)

    lista_pacientes_problemas = FuncRepo.consulta_pacientes_problemas(pacientes, start_date, end_date)
    pd_problemas = pandas.DataFrame(lista_pacientes_problemas)
    print(pandas.pivot_table(pd_problemas, index=["Nombre"], aggfunc='first'))
    print('')

    lista_pacientes_estadistica_planis = FuncRepo.consulta_estadisticas_planificaciones(pacientes, start_date, end_date)
    #print(lista_pacientes_estadistica_planis)
    df_pacientes_ales_tecnica = pandas.DataFrame(lista_pacientes_estadistica_planis)
    #print(pandas.pivot_table(df_pacientes_ales_tecnica, index='ID'))
    print(pandas.pivot_table(df_pacientes_ales_tecnica,
                             index=["Tecnica"],
                             values=["Numero"],
                             aggfunc=np.sum))
    print(pandas.pivot_table(df_pacientes_ales_tecnica,
                             index=["Acelerador", "Tecnica"],
                             values=["Numero"],
                             aggfunc=len))
    print(pandas.pivot_table(df_pacientes_ales_tecnica,
                             index=["Acelerador"],
                             values=["Numero"],
                             columns=["Tecnica"],
                             aggfunc=np.sum,
                             fill_value=0,
                             margins=True))

    lista_pacientes_SBRT = FuncRepo.consulta_SBRTs(pacientes, start_date, end_date)
    df_pacientes_SBRT = pandas.DataFrame([lista_pacientes_SBRT])
    print(df_pacientes_SBRT)
    print('')

    lista_iniciosTto = FuncRepo.consulta_iniciosTto(pacientes, start_date, end_date)
    df_iniciospormaquina = pandas.DataFrame([lista_iniciosTto])
    print(df_iniciospormaquina)
    print('')

    FuncRepo.calculo_demoras(pacientes, start_date, end_date)


    df_patologias = pandas.DataFrame(FuncRepo.consulta_patologias(pacientes, start_date, end_date))
    print(pandas.pivot_table(df_patologias,
                             index=['Patologia','IntencionTto'],
                             values=["Numero"],
                             aggfunc=np.sum,
                             fill_value=0,
                             margins=True))

if __name__ == '__main__':
    main()