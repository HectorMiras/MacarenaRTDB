from pymongo import MongoClient
import datetime
import FuncRepo
import pandas
import numpy as np
import pandas_profiling

def main():
    client = MongoClient('mongodb://10.233.42.60:27017') # Establece una conexión a MongoDB
    db = client['local'] # Seleccionamos la base de datos "local".
    pacientes = db['PacientesRT'] # Seleccionamos la colección "PacientesRT", que está dentro de la base de datos local

    start_date = datetime.datetime(2020, 4, 1, 0, 0, 0)
    end_date = datetime.datetime(2020, 7, 9, 0, 0, 0)

    #lista_pacientes_problemas = FuncRepo.consulta_pacientes_problemas(pacientes, start_date, end_date)
    #pd_problemas = pandas.DataFrame(lista_pacientes_problemas)
    #print(pandas.pivot_table(pd_problemas, index=["Nombre"], aggfunc='first'))
    print('')

    #lista_pacientes_estadistica_planis = FuncRepo.consulta_estadisticas_planificaciones(pacientes, start_date, end_date)
    #print(lista_pacientes_estadistica_planis)
    #df_pacientes_ales_tecnica = pandas.DataFrame(lista_pacientes_estadistica_planis)
    #print(df_pacientes_ales_tecnica.describe())

    df_simulaciones = pandas.DataFrame(FuncRepo.consulta_simulaciones(pacientes, start_date, end_date))
    report = pandas_profiling.ProfileReport(df_simulaciones)
    report.to_file("report_simulaciones.html")
    print(pandas.pivot_table(df_simulaciones,
                             index=["Motivo", "zonaAnatomica", "Inmovilizador"],
                             values=["Numero"],
                             aggfunc=np.sum,
                             fill_value=0,
                             margins=True))

    df_planificaciones = pandas.DataFrame(FuncRepo.consulta_planificaciones(pacientes,start_date,end_date))
    report = pandas_profiling.ProfileReport(df_planificaciones)
    report.to_file("report_planificaciones.html")
    print(pandas.pivot_table(df_planificaciones,
                             index=["Acelerador"],
                             values=["Numero"],
                             columns=["Tecnica"],
                             aggfunc=np.sum,
                             fill_value=0,
                             margins=True))
    print(pandas.pivot_table(df_planificaciones,
                             index=['Patologia', 'Verificacion'],
                             values=["Demora_Prescripcion-Plan"],
                             aggfunc=np.mean,
                             fill_value=0,
                             margins=True))

    df_prescripciones = pandas.DataFrame(FuncRepo.consulta_prescripciones(pacientes, start_date, end_date))
    report = pandas_profiling.ProfileReport(df_prescripciones)
    report.to_file("report_prescripciones.html")
    print(pandas.pivot_table(df_prescripciones,
                             index=['Patologia'],
                             values=["Demora_Simulacion_Prescripcion"],
                             aggfunc=np.mean,
                             fill_value=0,
                             margins=True))
    print(pandas.pivot_table(df_prescripciones,
                             index=['ProtocoloTto'],
                             values=["Numero"],
                             aggfunc=np.sum,
                             fill_value=0,
                             margins=True))

    df_sesiones = pandas.DataFrame(FuncRepo.consulta_sesiones(pacientes, start_date, end_date))
    print(pandas.pivot_table(df_sesiones,
                             index=['Patologia', 'Verificacion'],
                             values=["Demora_PrimeraConsulta-Inicio", "Demora_Plan-Inicio", "Numero"],
                             aggfunc={"Demora_PrimeraConsulta-Inicio": np.mean,
                                      "Demora_Plan-Inicio": np.mean,
                                      "Numero": np.sum}))
    print(df_sesiones.describe())
    report = pandas_profiling.ProfileReport(df_sesiones)
    report.to_file("report_iniciosTto.html")



if __name__ == '__main__':
    main()