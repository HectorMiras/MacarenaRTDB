import datetime
import numpy as np
import matplotlib.pyplot as plt

def encuentra_problemas(p):
    hoy = datetime.datetime.today()
    problemas = []
    an = p['ID']
    nombre = p['Nombre']
    mensajes = []
    for c in p['Casos']:
        fecha_caso = c['FechaInicio']
        if 'Trials' in c:
            for t in c['Trials']:
                if('Planificaciones' in t):
                    for plan in t['Planificaciones']:
                        if 'Motivo' not in plan:
                            mensaje = 'Planificación sin motivo.'
                            mensajes.append(mensaje)
                        if 'Acelerador' not in plan:
                            mensaje = 'Planificación sin acelerador.'
                            mensajes.append(mensaje)
                        if 'Tecnica' not in plan:
                            mensaje = 'Planificación sin tecnica de tratamiento.'
                            mensajes.append(mensaje)
                        #if 'Radiofisico' not in plan:
                            #mensaje = f'{nombre}. Planificación sin radiofisico.'
                            #problemas.append({an: mensaje})
                if('Prescripciones' in t):
                    for pres in t['Prescripciones']:
                        if 'Motivo' not in pres:
                            mensaje = 'Prescripción sin motivo.'
                            mensajes.append(mensaje)
                        if 'DosisPTV1' not in pres:
                            mensaje = 'Prescripción sin dosis a PTV1.'
                            mensajes.append(mensaje)
                if('Simulaciones' in t):
                    for sim in t['Simulaciones']:
                        if 'Motivo' not in sim:
                            mensaje = 'Simulación sin motivo.'
                            mensajes.append(mensaje)
                        if 'Orientacion' not in sim:
                            mensaje = 'Simulación sin orientación.'
                            mensajes.append(mensaje)
                if('Planificaciones' in t) and ('Prescripciones' not in t):
                    mensaje = 'Planificación sin prescripcion.'
                    mensajes.append(mensaje)
                if('Prescripciones' in t) and ('Simulaciones' not in t):
                    mensaje = 'Prescripción sin simulación.'
                    mensajes.append(mensaje)
                if ('Planificaciones' in t) and ('Prescripciones' in t) and ('Simulaciones' in t):
                    for pl in t['Planificaciones']:
                        # encuentra prescripcion y simulacion correspondiente. La de fecha más cercana
                        delta = datetime.datetime(2100, 12, 25, 0, 0, 0) - datetime.datetime(2000, 12, 25, 0, 0, 0)
                        for s in t['Simulaciones']:
                            if abs((pl['FechaInicio'] - s['FechaInicio']).days) < delta.days:
                                delta = pl['FechaInicio'] - s['FechaInicio']
                                sim = s
                        delta = datetime.datetime(2100, 12, 25, 0, 0, 0) - datetime.datetime(2000, 12, 25, 0, 0, 0)
                        for pr in t['Prescripciones']:
                            if abs((pl['FechaInicio'] - pr['FechaInicio']).days) < delta.days:
                                delta = pl['FechaInicio'] - pr['FechaInicio']
                                pres = pr
                        delta = pres['FechaInicio'] - sim['FechaInicio']
                        if delta.days > 30:
                            mensaje = f'Demora simulacion-prescripcion de {delta.days}'
                            mensajes.append(mensaje)
                        if delta.days < 0:
                            mensaje = f'Fecha de prescripción anterior a la simulación, {delta.days} días'
                            mensajes.append(mensaje)

                        delta = pl['FechaInicio'] - pres['FechaInicio']
                        if delta.days > 30:
                            mensaje = f'Demora prescripcion-planificación de {delta.days}'
                            mensajes.append(mensaje)
                        if delta.days < 0:
                            mensaje = f'Fecha de planificación anterior a la prescripción, {delta.days} días'
                            mensajes.append(mensaje)

                    if 'SesionesTto' in t:
                        delta = t['SesionesTto'][0]['FechaInicio'] - t['Planificaciones'][-1]['FechaInicio']
                        if delta.days > 60:
                            mensaje = f'Demora planificación-inicio de {delta.days}'
                            mensajes.append(mensaje)
                        if delta.days < 0:
                            mensaje = f'Fecha de inicio de tratamiento a' \
                                      f'nterior a la planificación {delta.days} días'
                            mensajes.append(mensaje)
                        delta = t['SesionesTto'][0]['FechaInicio'] - c['FechaInicio']
                        if delta.days > 120:
                            mensaje = f'Demora primera consulta-inicio tratamiento de {delta.days}'
                            mensajes.append(mensaje)
                    else:
                        # Busca pacientes con planificación pero sin sesiones de tto
                        delta = hoy - pl['FechaInicio']
                        fecha_plan = pl['FechaInicio'].strftime("%d/%m/%Y")
                        mensaje = f'La planificacion {fecha_plan} no tiene sesiones de tratamiento, {delta.days} días'
                        #mensajes.append(mensaje)
    if len(mensajes) > 0:
        problemas.append({'ID': an, 'Nombre': nombre, 'Problemas': mensajes})
    return problemas

def consulta_pacientes_problemas(pacientes, start_date, end_date):
    str_fecha_inicio = start_date.strftime("%d/%m/%Y")
    str_fecha_fin = end_date.strftime("%d/%m/%Y")

    # consulta
    consulta = pacientes.find(
        {'Casos.Trials.Planificaciones':
             {'$elemMatch': {'FechaInicio': {'$gt': start_date, '$lt': end_date}}}})

    print('')
    print(f'Consulta: Pacientes con alguna planificación entre {str_fecha_inicio} y {str_fecha_fin}')
    list_consulta = [x for x in consulta]  # Volcamos el cursor en una lista que podamos manipular
    ncon = len(list_consulta)
    print(f'Numero de pacientes que cumplen la consulta: {ncon}')
    print('')

    print('Problemas encontrados:')
    lista_pacientes_problemas = []
    for p in list_consulta:
        problemas = encuentra_problemas(p)
        if len(problemas) > 0:
            lista_pacientes_problemas.append(problemas)
            print(problemas)
    print('')
    print(f'Pacientes con problemas: {len(lista_pacientes_problemas)}')

    return list_consulta


def consulta_estadisticas_planificaciones(pacientes, start_date, end_date):
    str_fecha_inicio = start_date.strftime("%d/%m/%Y")
    str_fecha_fin = end_date.strftime("%d/%m/%Y")
    consulta = pacientes.find(
        {'Casos.Trials.Planificaciones': {'$elemMatch': {'FechaInicio': {'$gt': start_date, '$lt': end_date}}}})
    print('')
    print(f'Consulta: Pacientes con alguna planificación entre {str_fecha_inicio} y {str_fecha_fin}')
    list_consulta = [x for x in consulta]  # Volcamos el cursor en una lista que podamos manipular
    ncon = len(list_consulta)
    print(f'Numero de pacientes que cumplen la consulta: {ncon}')
    print('')

    cont_planis = 0
    cont_tecnica = {'2D Simple': 0, '3DCRT': 0, 'IMRT Step & Shoot': 0, 'Siemens mArc': 0, 'VMAT': 0, 'SC': 0}
    cont_tecnica0 = {'2D Simple': 0, '3DCRT': 0, 'IMRT Step & Shoot': 0, 'Siemens mArc': 0, 'VMAT': 0, 'SC': 0}
    cont_tecnica1 = {'2D Simple': 0, '3DCRT': 0, 'IMRT Step & Shoot': 0, 'Siemens mArc': 0, 'VMAT': 0, 'SC': 0}
    cont_tecnica2 = {'2D Simple': 0, '3DCRT': 0, 'IMRT Step & Shoot': 0, 'Siemens mArc': 0, 'VMAT': 0, 'SC': 0}
    cont_ALES = {'Siemens Primus': 0, 'Siemens Oncor': 0, 'Elekta Versa': 0}
    cont_ALESsTecnicas = {'Siemens Primus': cont_tecnica0, 'Siemens Oncor': cont_tecnica1,
                          'Elekta Versa': cont_tecnica2}
    fecha_str = ''
    for p in list_consulta:
        nuhsa = p['ID']
        nombre = p['Nombre']
        # print(nuhsa + ' ' + nombre)
        for c in p['Casos']:
            if 'Trials' in c:
                for t in c['Trials']:
                    if 'Planificaciones' in t:
                        for pl in t['Planificaciones']:
                            if start_date <= pl['FechaInicio'] <= end_date:
                                if 'Motivo' in pl:
                                    cont_planis = cont_planis + 1
                                    if 'Acelerador' in pl:
                                        cont_ALES[pl['Acelerador']] = cont_ALES[pl['Acelerador']] + 1
                                        if 'Tecnica' in pl:
                                            cont_ALESsTecnicas[pl['Acelerador']][pl['Tecnica']] = \
                                            cont_ALESsTecnicas[pl['Acelerador']][pl['Tecnica']] + 1
                                        else:
                                            cont_ALESsTecnicas[pl['Acelerador']]['SC'] = \
                                            cont_ALESsTecnicas[pl['Acelerador']]['SC'] + 1
                            else:
                                fecha_str = pl['FechaInicio']
                                # print(f'NO cumple criterio: {fecha_str}')
    print(f'Numero total de planificaciones: {cont_planis}')
    print('')
    print(f'Planificaciones por acelerador:')
    for x in cont_ALES:
        y = cont_ALES[x]
        print(f'   {x}: {y}')
    print('')
    print(f'Planificaciones por acelerador y tecnica:')
    for ale in cont_ALESsTecnicas:
        print(f'{ale}:')
        for tec in cont_ALESsTecnicas[ale]:
            num = cont_ALESsTecnicas[ale][tec]
            print(f'    {tec}: {num}')

    return list_consulta


# Esta clasificación por patologías no queda clara. Faltaría incluir metástasis en la lista de patologías?
# Por ejemplo, aparecen SBRT asociadas a patología MAMA, pero que en realidad se trattan metástasis vertebrales
def consulta_SBRTs(pacientes, start_date, end_date):
    str_fecha_inicio = start_date.strftime("%d/%m/%Y")
    str_fecha_fin = end_date.strftime("%d/%m/%Y")
    consulta = pacientes.find({'Casos.Trials.Prescripciones':
                                   {'$elemMatch':
                                        {'FechaInicio':
                                             {'$gt': start_date, '$lt': end_date}, 'ProtocoloTto': 'SBRT'
                                         }
                                    }
                               })
    print('')
    print(f'Consulta: Pacientes con alguna prescripción de SBRT entre {str_fecha_inicio} y {str_fecha_fin}')
    list_consulta = [x for x in consulta]  # Volcamos el cursor en una lista que podamos manipular
    ncon = len(list_consulta)
    print(f'Numero de pacientes que cumplen la consulta: {ncon}')
    print('')
    cont_patologias = {'Adenocarcinomas': 0, 'Carcinomas': 0, 'Cervix': 0, 'Cabeza y cuello': 0, 'Glioma': 0,
                       'Linfomas': 0, 'Mama': 0, 'Pulmón': 0, 'Próstata': 0, 'Recto': 0}
    for p in list_consulta:
        for c in p['Casos']:
            if 'Trials' in c:
                for t in c['Trials']:
                    if 'Prescripciones' in t:
                        for pres in t['Prescripciones']:
                            if 'ProtocoloTto' in pres:
                                if pres['ProtocoloTto'] == 'SBRT':
                                    cont_patologias[c['Patologia']] = cont_patologias[c['Patologia']] + 1

    for pat in cont_patologias:
        num = cont_patologias[pat]
        print(f'{pat}: {num}')

    return list_consulta

def consulta_iniciosTto(pacientes, start_date, end_date):
    str_fecha_inicio = start_date.strftime("%d/%m/%Y")
    str_fecha_fin = end_date.strftime("%d/%m/%Y")
    consulta = pacientes.find(
        {
            'Casos.Trials.SesionesTto.0.FechaInicio':
                {
                    '$gt':start_date,'$lt':end_date
                }
        })
    print('')
    print(f'Consulta: Pacientes con fecha de inicio entre {str_fecha_inicio} y {str_fecha_fin}')
    list_consulta = [x for x in consulta]  # Volcamos el cursor en una lista que podamos manipular
    ncon = len(list_consulta)
    print(f'Numero de pacientes que cumplen la consulta: {ncon}')
    print('')

    cont_ALES = {'Siemens Primus': 0, 'Siemens Oncor': 0, 'Elekta Versa': 0, 'Sin Acelerador': 0}
    for p in list_consulta:
        for c in p['Casos']:
            if 'Trials' in c:
                for t in c['Trials']:
                    if 'SesionesTto' in t:
                        fecha = t['SesionesTto'][0]['FechaInicio']
                        if start_date <= fecha <= end_date:
                            if 'Acelerador' in t['Planificaciones'][-1]:
                                maquina = t['Planificaciones'][-1]['Acelerador']
                                cont_ALES[maquina] = cont_ALES[maquina] + 1
                            else:
                                cont_ALES['Sin Acelerador'] = cont_ALES['Sin Acelerador'] + 1
    print('Inicios de tratamiento por máquina:')
    for x in cont_ALES:
        y = cont_ALES[x]
        print(f'   {x}: {y}')

    return list_consulta

def calculo_demoras(pacientes, start_date, end_date):
    str_fecha_inicio = start_date.strftime("%d/%m/%Y")
    str_fecha_fin = end_date.strftime("%d/%m/%Y")
    consulta = pacientes.find(
        {'Casos.Trials.Planificaciones': {'$elemMatch': {'FechaInicio': {'$gt': start_date, '$lt': end_date}}}})
    print('')
    print(f'Consulta: Pacientes con alguna planificación entre {str_fecha_inicio} y {str_fecha_fin}')
    list_consulta = [x for x in consulta]  # Volcamos el cursor en una lista que podamos manipular
    ncon = len(list_consulta)
    print(f'Numero de pacientes que cumplen la consulta: {ncon}')
    print('')
    demora_ct_pres = []
    demora_pres_plan = []
    demora_plan_ses = []
    demora_primeraconsulta_ses = []
    problemas = []
    bool_problema = False

    for p in list_consulta:
        an = p['ID']
        nombre = p['Nombre']
        bool_problema = False
        for c in p['Casos']:
            if 'Trials' in c:
                for t in c['Trials']:
                    if ('Planificaciones' in t) and ('Prescripciones' in t) and ('Simulaciones' in t):
                        for pl in t['Planificaciones']:
                            if start_date <= pl['FechaInicio'] <= end_date:
                                # encuentra prescripcion y simulacion correspondiente. La de fecha más cercana
                                delta = datetime.datetime(2100, 12, 25, 0, 0, 0) - datetime.datetime(2000, 12, 25, 0, 0,
                                                                                                     0)
                                for s in t['Simulaciones']:
                                    if abs((pl['FechaInicio'] - s['FechaInicio']).days) < delta.days:
                                        delta = pl['FechaInicio'] - s['FechaInicio']
                                        sim = s
                                delta = datetime.datetime(2100, 12, 25, 0, 0, 0) - datetime.datetime(2000, 12, 25, 0, 0,
                                                                                                     0)
                                for pr in t['Prescripciones']:
                                    if abs((pl['FechaInicio'] - pr['FechaInicio']).days) < delta.days:
                                        delta = pl['FechaInicio'] - pr['FechaInicio']
                                        pres = pr

                                delta = pres['FechaInicio'] - sim['FechaInicio']
                                if delta.days > 30:
                                    mensaje = f'{nombre}. Demora simulacion-prescripcion de {delta.days}'
                                    problemas.append({an: mensaje})
                                    bool_problema = True
                                if delta.days < 0:
                                    mensaje = f'{nombre}. Fecha de prescripción anterior a la simulación, {delta.days} días'
                                    problemas.append({an: mensaje})
                                    bool_problema = True
                                if bool_problema == False:
                                    demora_ct_pres.append(delta.days)
                                else:
                                    bool_problema = False

                                delta = pl['FechaInicio'] - pres['FechaInicio']
                                if delta.days > 30:
                                    mensaje = f'{nombre}. Demora prescripcion-planificación de {delta.days}'
                                    problemas.append({an: mensaje})
                                    bool_problema = True
                                if delta.days < 0:
                                    mensaje = f'{nombre}. Fecha de planificación anterior a la prescripción, {delta.days} días'
                                    problemas.append({an: mensaje})
                                    bool_problema = True
                                if bool_problema == False:
                                    demora_pres_plan.append(delta.days)
                                else:
                                    bool_problema = False

                                if 'SesionesTto' in t:
                                    delta = t['SesionesTto'][0]['FechaInicio'] - t['Planificaciones'][-1]['FechaInicio']
                                    if delta.days > 120:
                                        mensaje = f'{nombre}. Demora planificación-inicio de {delta.days}'
                                        problemas.append({an: mensaje})
                                        bool_problema = True
                                    if delta.days < 0:
                                        mensaje = f'{nombre}. Fecha de inicio de tratamiento a' \
                                                  f'nterior a la planificación {delta.days} días'
                                        problemas.append({an: mensaje})
                                        bool_problema = True
                                    if bool_problema == False:
                                        demora_plan_ses.append(delta.days)
                                    else:
                                        bool_problema = False
                                    delta = t['SesionesTto'][0]['FechaInicio'] - c['FechaInicio']
                                    if delta.days > 120:
                                        mensaje = f'{nombre}. Demora primera consulta-inicio tratamientode {delta.days}'
                                        problemas.append({an: mensaje})
                                        bool_problema = True
                                    if bool_problema == False:
                                        demora_primeraconsulta_ses.append(delta.days)
                                    else:
                                        bool_problema = False


    print(f'Numero de pacientes con problemas: {len(problemas)}')
    for prob in problemas:
        print(prob)
    print('')
    print('Demoras simulación-prescripción')
    demora_ct_pres = np.array(demora_ct_pres)
    print(f'Demora media (días): {np.mean(demora_ct_pres)}')
    print(f'Desviación estándar en la demora: {np.std(demora_ct_pres)}')
    print('')
    print('Demoras prescripción-planificación')
    demora_pres_plan = np.array(demora_pres_plan)
    print(f'Demora media (días): {np.mean(demora_pres_plan)}')
    print(f'Desviación estándar en la demora: {np.std(demora_pres_plan)}')
    print('')
    print('Demoras planificación-inicio tratamiento')
    demora_plan_ses = np.array(demora_plan_ses)
    print(f'Demora media (días): {np.mean(demora_plan_ses)}')
    print(f'Desviación estándar en la demora: {np.std(demora_plan_ses)}')
    print('')
    print('Demoras primera consulta-inicio tratamiento')
    demora_primeraconsulta_ses = np.array(demora_primeraconsulta_ses)
    print(f'Demora media (días): {np.mean(demora_primeraconsulta_ses)}')
    print(f'Desviación estándar en la demora: {np.std(demora_primeraconsulta_ses)}')

    fig, axs = plt.subplots(2,2)
    axs[0, 0].hist(demora_ct_pres, bins=np.max(demora_ct_pres))
    axs[0, 0].set_title('Simulación-prescripción')
    axs[0, 1].hist(demora_pres_plan, bins=np.max(demora_pres_plan))
    axs[0, 1].set_title('Prescripción-planificación')
    axs[1, 0].hist(demora_plan_ses, bins=np.max(demora_plan_ses))
    axs[1, 0].set_title('Planificación-inicio tratamiento')
    axs[1, 1].hist(demora_primeraconsulta_ses, bins=np.max(demora_primeraconsulta_ses))
    axs[1, 1].set_title('Primera consulta-inicio tratamiento')

    axs[0, 0].set(ylabel='Frecuencia')
    axs[1, 0].set(ylabel='Frecuencia')
    axs[1, 0].set(xlabel='Días')
    axs[1, 1].set(xlabel='Días')

    fig.suptitle(f'Demoras entre las fechas {str_fecha_inicio} y {str_fecha_fin}')
    plt.show()
