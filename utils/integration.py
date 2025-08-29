import requests
import os
from dotenv import load_dotenv
from datetime import datetime

URL = 'https://api.clinicorp.com/rest/v1/'

load_dotenv()
TOKEN = os.getenv('TOKEN')
USER = os.getenv('USER')
CODE_LINK = os.getenv('CODE_LINK')
ID_CLINICA = os.getenv('id_clinica')
STR_CLINICA = os.getenv('str_clinica')
ID_LOJA = os.getenv('ID_LOJA')


headers = {
    'accept': 'application/json',
    'Authorization': f'Basic {TOKEN}',
    'Content-Type': 'application/json'
}


def get_patient(phone):
    url_get_procedures = URL+'/patient/get'

    payload = {
        'subscriber_id': ID_CLINICA,
        'Phone': phone
    }

    response = requests.get(url=url_get_procedures, headers=headers, params=payload)

    dados = response.json()
    if isinstance(dados, list) and dados:
        return dados[0]

    if isinstance(dados, dict):
        return dados

    return None


def list_all_professionals():
    url_get_procedures = URL+'/professional/list_all_professionals'

    response = requests.get(url=url_get_procedures, headers=headers)

    dados = response.json()
    if isinstance(dados, list) and dados:
        return dados


def post_patient_create(name=str, birth_date=str, sex=str,  email=str, phone=int, rg=int, cpf=int):
    url_get_procedures = URL+'/patient/create'

    params = {
        "subscriber_id": STR_CLINICA,
        "Name": name,
        "BirthDate": birth_date,
        "Sex": sex,
        "Email": email,
        "MobilePhone": phone,
        "DocumentId": rg,
        "OtherDocumentId": cpf,
        "Notes": "",
        "IgnoreSameName": "X",
        "IgnoreSameDoc": "X"
    }

    response = requests.post(url=url_get_procedures, headers=headers, json=params)

    if response.status_code == 200:
        return True
    else:
        return False


def day_week(date):
    day_week = {
        0: 'segunda',
        1: 'terça',
        2: 'quarta',
        3: 'quinta',
        4: 'sexta',
        5: 'sabado',
        6: 'domingo'
    }

    day = datetime.strptime(date, '%Y-%m-%d')  # Exemplo: '2025/08/30'
    return day_week[day.weekday()]


def horario_dentro_limite(inicio, dia):
    """
    Verifica se o horário está dentro do limite aceito para o dia
    """
    if dia in ['segunda', 'quarta', 'sexta']:
        return '09:15' <= inicio <= '20:00'
    elif dia in ['terça', 'quinta']:
        return '13:30' <= inicio <= '20:00'
    else:
        return False  # sabado, domingo ou outro


def get_avaliable_days(date):
    print(date)
    day = day_week(date)

    if day == 'domingo':
        return 'Infelizmente não trabalhamos aos domingos.'

    url_get_procedures = URL + '/appointment/get_avaliable_days'

    payload = {
        'subscriber_id': STR_CLINICA,
        'code_link': CODE_LINK,
        'from': date,
        'to': date,
        'includeHolidays': 'X',
        'showAvailableTimes': 'X'
    }

    response = requests.get(url=url_get_procedures, headers=headers, params=payload)
    dates = response.json()

    def process_times(dates_free):
        times_free = []
        for dic in dates_free:
            inicio = dic["from"]
            fim = dic["to"]

            if not horario_dentro_limite(inicio, day):
                continue

            horario = inicio + '-' + fim
            free = {
                'horario': horario,
                'proficional': dic['professionalId']
            }
            times_free.append(free)
        return times_free

    if isinstance(dates, list) and dates:
        return process_times(dates[0].get('AvaliableTimes', []))

    if isinstance(dates, dict):
        return process_times(dates.get('AvaliableTimes', []))

    return None


def create_online_scheduling(name, consultation, phone, cpf_3, email, obs, from_time, to_time, date, personId):
    url = f"{URL}/appointment/create_online_scheduling"

    payload = {
        "CodeLink": CODE_LINK,
        "PatientName": name,
        "SchedulingReason": consultation,
        "MobilePhone": phone,
        "OtherPhones": phone,
        "OtherDocumentId": cpf_3,
        "Email": email,
        "NotesPatient": obs,
        "fromTime": from_time,
        "toTime": to_time,
        "IsOnlineScheduling": True,
        "date": date,
        "Type": "CLOUDIA",
        "Dentist_PersonId": personId,
        "Clinic_BusinessId": ID_LOJA,
        "AlreadyPatient": True
    }

    try:
        response = requests.post(url=url, headers=headers, json=payload)
        response.raise_for_status()
        print("[✅] Agendamento enviado com sucesso!")
        print("Resposta:", response.text)
        return True

    except requests.exceptions.RequestException as e:
        print("[❌] Erro ao enviar agendamento:", e)
        return False
