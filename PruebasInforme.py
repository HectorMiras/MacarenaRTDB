from pymongo import MongoClient
import datetime
import FuncRepo
import pandas
import numpy as np
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import pandas_profiling
import matplotlib.pyplot as plt
from io import BytesIO
from io import StringIO
from reportlab.lib.utils import ImageReader



def main():
    client = MongoClient('mongodb://10.233.42.60:27017') # Establece una conexión a MongoDB
    db = client['local'] # Seleccionamos la base de datos "local".
    pacientes = db['PacientesRT'] # Seleccionamos la colección "PacientesRT", que está dentro de la base de datos local

    start_date = datetime.datetime(2020, 4, 1, 0, 0, 0)
    end_date = datetime.datetime(2020, 6, 30, 0, 0, 0)

    df_planificaciones = pandas.DataFrame(FuncRepo.consulta_planificaciones(pacientes, start_date, end_date))
    #report = pandas_profiling.ProfileReport(df_planificaciones)
    #report.to_file("report_planificaciones.html")
    tabla_planis = pandas.pivot_table(df_planificaciones,
                             index=["Acelerador"],
                             values=["Numero"],
                             columns=["Tecnica"],
                             aggfunc=np.sum,
                             fill_value=0,
                             margins=True)
    tabla_demoras_plan = pandas.pivot_table(df_planificaciones,
                       index=['Patologia'],
                       values=["Demora_Prescripcion-Plan"],
                       columns=["Verificacion"],
                       aggfunc=np.mean,
                       fill_value=0,
                       margins=True)

    df_prescripciones = pandas.DataFrame(FuncRepo.consulta_prescripciones(pacientes, start_date, end_date))
    tabla_patologia_IntencionTto = pandas.pivot_table(df_prescripciones,
                             index=['Patologia','IntencionTto'],
                             values=["Numero"],
                             aggfunc=np.sum,
                             fill_value=0,
                             margins=True)

    df_sesiones = pandas.DataFrame(FuncRepo.consulta_sesiones(pacientes, start_date, end_date))
    tabla_demora_ttos =pandas.pivot_table(df_sesiones,
                             index=['Patologia'],
                             values=["Demora_PrimeraConsulta-Inicio", "Demora_Plan-Inicio", "Numero"],
                             aggfunc={"Demora_PrimeraConsulta-Inicio": np.mean,
                                      "Demora_Plan-Inicio": np.mean,
                                      "Numero": np.sum},
                            fill_value=0,
                            margins=True)

    tabla_inicios_por_semana = pandas.pivot_table(df_sesiones,
                                           index=['Semana'],
                                           values=["Numero"],
                                           aggfunc=np.sum,
                                           fill_value=0,
                                           margins=True)





    # Generamos informe

    doc = SimpleDocTemplate("Informe_Consulta_BD.pdf", pagesize=letter,
                            rightMargin=18, leftMargin=18,
                            topMargin=18, bottomMargin=18)
    Story = []
    styles = getSampleStyleSheet()

    ptext = '<font size="16">Informe de estadísticas de los ' \
            'servicios de RF y RT del Hospital Virgen Macarena.</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 25))

    ptext = f'Fecha de elaboración del informe: {datetime.date.today()}'
    ptext = '<font size="12">' + ptext + '</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 25))

    ptext = f'Intervalo de fechas de la consulta desde {start_date.date()} hasta {end_date.date()}'
    ptext = '<font size="12">' + ptext + '</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 25))
    #colwidths = 50
    #GRID_STYLE = TableStyle()

    ptext = f'Planificaciones por técnica y máquina de tratamiento:'
    ptext = '<font size="12">' + ptext + '</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 25))
    listatabla, n = prepare_pivot_table_for_reportlab(tabla_planis)
    table1 = Table(listatabla, repeatRows=n)
    Story.append(table1)
    Story.append(Spacer(1, 25))

    ptext = f'Demoras prescripción-planificación:'
    ptext = '<font size="12">' + ptext + '</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 25))
    listatabla, n = prepare_pivot_table_for_reportlab(tabla_demoras_plan)
    table1 = Table(listatabla, repeatRows=n)
    Story.append(table1)
    Story.append(Spacer(1, 25))

    ptext = f'Patologías e intención de tratamiento:'
    ptext = '<font size="12">' + ptext + '</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 25))
    listatabla, n = prepare_pivot_table_for_reportlab(tabla_patologia_IntencionTto)
    table1 = Table(listatabla, repeatRows=n)
    Story.append(table1)
    Story.append(Spacer(1, 25))

    ptext = f'Demoras inicios de tratamiento:'
    ptext = '<font size="12">' + ptext + '</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 25))
    listatabla, n = prepare_pivot_table_for_reportlab(tabla_demora_ttos)
    table1 = Table(listatabla, repeatRows=n)
    Story.append(table1)
    Story.append(Spacer(1, 25))

    ptext = f'Inicios de tratamiento por semana:'
    ptext = '<font size="12">' + ptext + '</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 25))
    listatabla, n = prepare_pivot_table_for_reportlab(tabla_inicios_por_semana)
    table1 = Table(listatabla, repeatRows=n)
    Story.append(table1)
    Story.append(Spacer(1, 25))

    fig = plt.figure()
    ax = df_sesiones.hist('Semana')
    ax = ax[0]
    imgdata = BytesIO()
    fig.savefig(imgdata, format='png')
    imgdata.seek(0)
    img_ = ImageReader(imgdata)
    Story.append(img_)

    doc.build(Story)

def prepare_df_for_reportlab(df):
    lista = [df.columns[:, ].values.astype(str).tolist()] + df.values.tolist()
    return lista

def prepare_pivot_table_for_reportlab(df):
    df2 = df.reset_index() # reset the index so row labels show up in the reportlab table
    n = df2.columns.nlevels # number of table header rows to repeat
    if n > 1:
        labels1 = [list(val) for val in df2.columns.values]
        labels1 = [list(i) for i in zip(*labels1)]  #transponemos la lista
        labels = [labels1[:][n-1]]  # nos quedamos con el último nivel de columnas
        print(labels[0])
        #labels = map(list, zip(*df2.columns.values[1]))
    else:
        labels = [df2.columns[:,].values.astype(str).tolist()]
    values = df2.values.tolist()
    datalist = labels + values
    return datalist, n

if __name__ == '__main__':
    main()
