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

def main():
    client = MongoClient('mongodb://10.233.42.60:27017') # Establece una conexión a MongoDB
    db = client['local'] # Seleccionamos la base de datos "local".
    pacientes = db['PacientesRT'] # Seleccionamos la colección "PacientesRT", que está dentro de la base de datos local

    start_date = datetime.datetime(2020, 1, 1, 0, 0, 0)
    end_date = datetime.datetime(2020, 3, 31, 0, 0, 0)


    lista_pacientes_estadistica_planis = FuncRepo.consulta_estadisticas_planificaciones(pacientes, start_date, end_date)
    #print(lista_pacientes_estadistica_planis)
    df_pacientes_ales_tecnica = pandas.DataFrame(lista_pacientes_estadistica_planis)
    t1 = pandas.pivot_table(df_pacientes_ales_tecnica,
                             index=["Acelerador"],
                             values=["Numero"],
                             columns=["Tecnica"],
                             aggfunc=np.sum,
                             fill_value=0,
                             margins=True)
    print(t1)



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
    listatabla, n = prepare_df_for_reportlab(t1)
    table1 = Table(listatabla, repeatRows=n)
    Story.append(table1)
    doc.build(Story)

def prepare_df_for_reportlab(df):
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
