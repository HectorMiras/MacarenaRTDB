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
from matplotlib.ticker import MaxNLocator
import openpyxl



def main():
    client = MongoClient('mongodb://10.233.42.60:27017') # Establece una conexión a MongoDB
    db = client['local'] # Seleccionamos la base de datos "local".
    pacientes = db['PacientesRT'] # Seleccionamos la colección "PacientesRT", que está dentro de la base de datos local

    start_date = datetime.datetime(2019, 10, 1, 0, 0, 0)
    end_date = datetime.datetime(2020, 7, 9, 0, 0, 0)

    excelfilename = "ConsultaBD.xlsx"

    df_simulaciones = pandas.DataFrame(FuncRepo.consulta_simulaciones(pacientes, start_date, end_date))
    tabla_demoras_consulta_ct = pandas.pivot_table(df_simulaciones,
                                            index=['Patologia'],
                                            values=["Demora_PrimeraConsulta_Simulacion"],
                                            aggfunc=np.mean,
                                            fill_value=0,
                                            margins=True).round(2)


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
                       margins=True).round(2)

    df_prescripciones = pandas.DataFrame(FuncRepo.consulta_prescripciones(pacientes, start_date, end_date))
    tabla_patologia_IntencionTto = pandas.pivot_table(df_prescripciones,
                             index=['Patologia','ProtocoloTto'],
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
                            margins=True).round(2)

    tabla_inicios_por_semana = pandas.pivot_table(df_sesiones,
                                           index=['Semana'],
                                           values=["Numero"],
                                           aggfunc=np.sum,
                                           fill_value=0,
                                           margins=True)

    lista_problemas = FuncRepo.consulta_pacientes_problemas(pacientes, start_date, end_date)

    # Exportamos resultados a excel
    # Escribe el DF en una hoja de excel
    df_planificaciones.to_excel(excelfilename,
                                sheet_name='All',
                                index=False)
    with pandas.ExcelWriter(excelfilename, engine="openpyxl") as writer:
        # above: I use openpyxl, you can change this
        writer.book = openpyxl.load_workbook(excelfilename)
        tabla_planis.to_excel(writer, "Planificaciones")
        tabla_patologia_IntencionTto.to_excel(writer, "Patologias-Protocolos")
        tabla_demoras_plan.to_excel(writer, "DemorasPlan")
        tabla_demora_ttos.to_excel(writer, "DemorasTto")
        tabla_inicios_por_semana.to_excel(writer, "IniciosTtoPorSemana")

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

    ptext = f'Patologías y protocolos de tratamiento:'
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

    hist = df_simulaciones.groupby(['Semana']).sum()["Numero"]
    bins = hist.index.array
    fig, ax = plt.subplots(2,2,figsize=(7,7))
    bars = ax[0,0].bar(bins, hist, width=1, align='center')
    for bar in bars:
        text = bar.get_height()
        text_x = bar.get_x()
        text_y = bar.get_height() + 1
        ax[0,0].text(text_x, text_y, text, va='center', color='black', fontsize=6)
    x_ticks = np.arange(bins[0], bins[-1]+1, 2)
    ax[0,0].set(xticks=x_ticks, title='TACs por semana')
    for item in ([ax[0,0].title, ax[0,0].xaxis.label, ax[0,0].yaxis.label] +
                 ax[0,0].get_xticklabels() + ax[0,0].get_yticklabels()):
        item.set_fontsize(7)
    ax[0,0].get_yaxis().set_visible(False)

    hist = df_prescripciones.groupby(['Semana']).sum()["Numero"]
    bins = hist.index.array
    bars = ax[0, 1].bar(bins, hist, width=1, align='center')
    for bar in bars:
        text = bar.get_height()
        text_x = bar.get_x()
        text_y = bar.get_height() + 1
        ax[0, 1].text(text_x, text_y, text, va='center', color='black', fontsize=6)
    x_ticks = np.arange(bins[0], bins[-1] + 1, 2)
    ax[0, 1].set(xticks=x_ticks, title='Prescripciones por semana')
    for item in ([ax[0, 1].title, ax[0, 1].xaxis.label, ax[0, 1].yaxis.label] +
                 ax[0, 1].get_xticklabels() + ax[0, 1].get_yticklabels()):
        item.set_fontsize(7)
    ax[0, 1].get_yaxis().set_visible(False)

    hist = df_planificaciones.groupby(['Semana']).sum()["Numero"]
    bins = hist.index.array
    bars = ax[1, 0].bar(bins, hist, width=1, align='center')
    for bar in bars:
        text = bar.get_height()
        text_x = bar.get_x()
        text_y = bar.get_height() + 1
        ax[1, 0].text(text_x, text_y, text, va='center', color='black', fontsize=6)
    x_ticks = np.arange(bins[0], bins[-1] + 1, 2)
    ax[1, 0].set(xticks=x_ticks, title='Planificaciones por semana')
    for item in ([ax[1, 0].title, ax[1, 0].xaxis.label, ax[1, 0].yaxis.label] +
                 ax[1, 0].get_xticklabels() + ax[1, 0].get_yticklabels()):
        item.set_fontsize(7)
    ax[1, 0].get_yaxis().set_visible(False)

    #imgdata = BytesIO()
    #fig.savefig(imgdata, format='png')
    #imgdata.seek(0)
    #img_ = Image(imgdata)
    #Story.append(img_)

    # ptext = f'Inicios de tratamiento por semana:'
    # ptext = '<font size="12">' + ptext + '</font>'
    # Story.append(Paragraph(ptext, styles["Normal"]))
    # Story.append(Spacer(1, 25))

    hist = df_sesiones.groupby(['Semana']).sum()["Numero"]
    bins = hist.index.array
    #fig, ax = plt.subplots(figsize=(4, 4))
    bars = ax[1,1].bar(bins, hist, width=1, align='center')
    for bar in bars:
        text = bar.get_height()
        #text_x = bar.get_x() + bar.get_width() / 4
        text_x = bar.get_x()
        text_y = 1 + bar.get_height()
        ax[1,1].text(text_x, text_y, text, va='center', color='black', fontsize=6)
    x_ticks = np.arange(bins[0],bins[-1]+1,2)
    ax[1,1].set(xticks=x_ticks, title='Inicios por semana')
    for item in ([ax[1,1].title, ax[1,1].xaxis.label, ax[1,1].yaxis.label] +
                 ax[1,1].get_xticklabels() + ax[1,1].get_yticklabels()):
        item.set_fontsize(7)
    ax[1,1].get_yaxis().set_visible(False)

    imgdata = BytesIO()
    fig.savefig(imgdata, format='png')
    imgdata.seek(0)
    img_ = Image(imgdata)
    Story.append(img_)

    ptext = f'Lista de problemas encontrados:'
    ptext = '<font size="12">' + ptext + '</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 25))
    for pac in lista_problemas:
        for prob in pac['Problemas']:
            ptext = '<font size="12">' + pac['ID'] +': ' + prob + '</font>'
            Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 25))


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
    elem = datalist[0][0]
    for i in np.arange(1,len(datalist)):
        if (datalist[i][0] is elem):
            datalist[i][0]= ""
        else:
            elem = datalist[i][0]

    return datalist, n

if __name__ == '__main__':
    main()
