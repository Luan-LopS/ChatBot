import requests
import os
from threading import Timer
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from chat.ia import send_message
from utils.integration import get_patient
from chat.chat import home_menu, start_registration, continue_registration, is_registering, continue_scheduling, start_scheduling, is_scheduling, procedures, scheduling_state, scheduling_data, state_registration, registration_data


app = Flask(__name__)

load_dotenv()
Z_API = os.getenv('Z-API')
API = os.getenv('API')
CLIENT_TOKEN = os.getenv('CLIENT_TOKEN')
NOME = os.getenv('NOME')
EMDERECO = os.getenv('EMDERECO')
LATITUDE = os.getenv('LATITUDE')
LONGITUDE = os.getenv('LONGITUDE')


pending_messages = {}
timers = {}
active_session = {}
session_ia = {}
procedure = {}
human = {}


def end_human(phone):
    timer = active_session.pop(phone, None)
    if timer:
        timer.cancel()
    human.pop(phone, None)
    send("Sessão encerrada por inatividade. Digite qualquer coisa para começar novamente.", phone)


def start_human(phone):
    if phone in active_session:
        active_session[phone].cancel()
    timer = Timer(1200, end_human, [phone])
    active_session[phone] = timer
    timer.start()


def end_session(phone):
    timer = active_session.pop(phone, None)
    if timer:
        timer.cancel()
    procedure.pop(phone, None)
    session_ia.pop(phone, None)
    pending_messages.pop(phone, None)
    scheduling_state.pop(phone, None)
    scheduling_data.pop(phone, None)
    state_registration.pop(phone, None)
    registration_data.pop(phone, None)
    send("Sessão encerrada por inatividade. Digite qualquer coisa para começar novamente.", phone)


def start_session(phone):
    if phone in active_session:
        active_session[phone].cancel()
    timer = Timer(600, end_session, [phone])
    active_session[phone] = timer
    timer.start()


def process_conversation_ia(phone, texto):
    if session_ia.get(phone) == True:
        start_session(phone)
    pending_messages.pop(phone, None)

    texto_lower = texto.lower()
    if not texto_lower:
        patient = get_patient(phone)
        if isinstance(patient, list) and patient:
            name_patient = patient[0].get('Name')

        if isinstance(patient, dict):
            name_patient = patient.get('Name')
        resposta = home_menu(texto, phone, name_patient)
        msg = resposta.get("msg", "")
        optionList = resposta.get("optionList")
        send(msg, phone, optionList=optionList)
        return jsonify({'status': 'ok'}), 200
    if 'x' in texto_lower:
        session_ia.pop(phone, None)
        return None
    resposta = send_message(texto, phone)
    menu_resposta = f'''{resposta} \n\n 
    --------------------------------------
        Para sair, digite X'''
    send(menu_resposta, phone)


def process_conversation(phone, texto):
    msg = ' '.join(pending_messages.get(phone, []))
    pending_messages.pop(phone, None)
    timers.pop(phone, None)

    if human.get(phone) == True:
        start_human(phone)

    if is_registering(phone):
        resposta = continue_registration(phone, texto)
        if not resposta:
            patient = get_patient(phone)
            if isinstance(patient, list) and patient:
                name_patient = patient[0].get('Name')

            if isinstance(patient, dict):
                name_patient = patient.get('Name')

            resposta = home_menu(texto, phone, name_patient)
            msg = resposta.get("msg", "")
            optionList = resposta.get("optionList")
            send(msg, phone, optionList=optionList)
            return jsonify({'status': 'ok'}), 200
        send(resposta, phone)

        if 'x' in resposta.lower():
            return None
        resposta = send_message(texto, phone)
        menu_resposta = f'''{resposta} \n\n 
        --------------------------------------
            Para sair, digite X'''
        send(menu_resposta, phone)

    if is_scheduling(phone):
        resposta = continue_scheduling(phone, texto)

        if not resposta:
            patient = get_patient(phone)
            if isinstance(patient, list) and patient:
                name_patient = patient[0].get('Name')

            if isinstance(patient, dict):
                name_patient = patient.get('Name')

            resposta = home_menu(texto, phone, name_patient)
            msg = resposta.get("msg", "")
            optionList = resposta.get("optionList")
            send(msg, phone, optionList=optionList)
            return jsonify({'status': 'ok'}), 200

        if isinstance(resposta, dict):
            msg = resposta.get("msg", "")
            optionList = resposta.get("optionList")
            send(msg, phone, optionList=optionList)
        else:
            send(resposta, phone)


def _send(msg, phone, buttonButtons=None, optionList=None, location=None):
    headers = {
        "Client-Token": CLIENT_TOKEN,
        "Content-Type": "application/json"
    }

    if optionList:
        url = f"https://api.z-api.io/instances/{Z_API}/token/{API}/send-option-list"
        payload = {
            "phone": phone,
            "delayTyping": 5,
            "message": msg,
            "optionList": optionList
        }

    elif location:
        url = f"https://api.z-api.io/instances/{Z_API}/token/{API}/send-location"

        payload = {
            "phone": phone,
            "delayTyping": 5,
            "title": NOME,
            "address": EMDERECO,
            "latitude": LATITUDE,
            "longitude": LONGITUDE
        }

    else:
        url = f"https://api.z-api.io/instances/{Z_API}/token/{API}/send-text"

        payload = {
            "phone": phone,
            "message": msg,
            "delayTyping": 5,
        }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print("📤 Mensagem enviada")
        print("Resposta:", response.json())
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")


def send(msg, phone, buttonButtons=None, optionList=None, location=None):
    thread = Thread(target=_send, args=(msg, phone, buttonButtons, optionList, location))
    thread.daemon = True
    thread.start()


@app.route(f"/instancia/{Z_API}/receive", methods=["POST"])
def webhook():
    token = request.args.get("token")
    if token != os.getenv("WEBHOOK_SECRET"):
        return jsonify({"error": "Não autorizado"}), 401

    data = request.json
    raw_phone = data.get('phone')
    if not raw_phone:
        return jsonify({'error': 'Telefone não encontrado'}), 400

    if raw_phone.startswith('55') and len(raw_phone) == 12:
        phone = raw_phone[:4] + '9' + raw_phone[4:]
    else:
        phone = raw_phone

    if not phone:
        return jsonify({'error': 'Telefone não encontrado'}), 400

    if data.get("text"):
        group = data['isGroup']
        texto = data["text"].get("message", "")

        if group is False:
            start_session(phone)

            if human.get(phone) == True:
                process_conversation(phone, texto)
                return jsonify({'status': 'ok'}), 200

            if is_registering(phone):
                process_conversation(phone, texto)
                return jsonify({'status': 'ok'}), 200

            if is_scheduling(phone):
                process_conversation(phone, texto)
                return jsonify({"status": "ok"}), 200

            if phone not in pending_messages:
                pending_messages[phone] = []

            patient = get_patient(phone)
            if isinstance(patient, list) and patient:
                name_patient = patient[0].get('Name')

            if isinstance(patient, dict):
                name_patient = patient.get('Name')

            if session_ia.get(phone) == True:
                process_conversation_ia(phone, texto)

                return jsonify({'status': 'ok'}), 200
            else:
                resposta = home_menu(texto, phone, name_patient)
                msg = resposta.get("msg", "")
                optionList = resposta.get("optionList")
                send(msg, phone, optionList=optionList)
                return jsonify({'status': 'ok'}), 200

    elif data.get('audio'):
        send('Favor enviar texto', phone)
        return jsonify({'satus': 'ok'}), 200

    if data.get('listResponseMessage', {}).get('selectedRowId'):
        response_menu = data['listResponseMessage']['selectedRowId']

        if response_menu == '1':
            dados_patient = get_patient(phone)
            name = dados_patient.get('Name')

            if name:
                resposta = start_scheduling(phone)

                if isinstance(resposta, dict):
                    msg = resposta.get("msg", "")
                    optionList = resposta.get("optionList")
                    send(msg, phone, optionList=optionList)
                    return jsonify({"status": "ok"}), 200
                else:
                    send(resposta, phone)
                    return jsonify({"status": "ok"}), 200

            else:
                msg_inicial = start_registration(phone)
                send(msg_inicial, phone)
                return jsonify({"status": "ok"}), 200

        elif response_menu == '2':
            option_list = {
                "msg": "Estas são algumas dúvidas frequentes:",
                "optionList": {
                    "title": "Dúvidas frequentes",
                    "buttonLabel": "Qual a sua dúvidas",
                    "options": [
                        {"id": '2.2', "description": "Como cancelar um agendamento", "title": "Cancelamento"},
                        {"id": '2.3', "description": "Horario de atendimento", "title": "Horarios"},
                        {"id": '2.4', "description": "", "title": "Outra dúvida"}
                    ]
                }
            }

            send(option_list["msg"], phone, optionList=option_list["optionList"])
            return jsonify({"status": "ok"}), 200

        elif response_menu == '2.1':
            option_list = {
                "msg": "Escolha uma categoria para ver os tratamentos que temos para você",
                "optionList": {
                    "title": "Escolha uma categoria de procedimentos",
                    "buttonLabel": "Ver categorias",
                    "options": [
                        {"id": '2.1.1', "description": "Limpeza, preenchimento, toxina, etc..", "title": "Tratamentos Faciais"},
                        {"id": '2.1.2', "description": "Manta térmica, enzimas, crio, corrente russa...", "title": "Tratamentos Corporais"},
                        {"id": '2.1.3', "description": "Laser, microvasos, skinbooster, NCTF 135 HA...", "title": "Procedimentos Especiais"},
                    ]
                }
            }

            send(option_list["msg"], phone, optionList=option_list["optionList"])
            return jsonify({"status": "ok"}), 200

        elif response_menu == '2.1.1':
            option_list = {
                "msg": "Escolha o procediemento que deseja",
                "optionList": {
                    "title": "Escolha uma categoria de procedimentos",
                    "buttonLabel": "Ver categorias",
                    "options": [
                        {"id": '2.1.1.1', "description": "", "title": "Toxina Botulínica"},
                        {"id": '2.1.1.2', "description": "", "title": "Preenchimento Labial"},
                        {"id": '2.1.1.3', "description": "", "title": "Preenchimento Facial"},
                        {"id": '2.1.1.4', "description": "", "title": "Preenchimento de Olheiras"},
                        {"id": '2.1.1.5', "description": "", "title": "Rinomodelação"},
                        {"id": '2.1.1.6', "description": "", "title": "Limpeza de Pele Profunda"},
                        {"id": '2.1.1.7', "description": "", "title": "Hydra – Limpeza e Hidratação"},
                        {"id": '2.1.1.8', "description": "", "title": "Peeling de Ácido Retinoico"},
                        {"id": '2.1.1.9', "description": "", "title": "Peeling de Vitamina C"},
                    ]
                }
            }

            send(option_list["msg"], phone, optionList=option_list["optionList"])
            return jsonify({"status": "ok"}), 200

        elif response_menu == '2.1.2':
            duvidas = {
                "msg": "Estas são algumas dúvidas frequentes:",
                "optionList": {
                    "title": "Escolha uma categoria de procedimentos",
                    "buttonLabel": "Ver categorias",
                    "options": [
                        {"id": '2.1.2.1', "description": "", "title": "Enzimas"},
                        {"id": '2.1.2.2', "description": "", "title": "Manta Térmica"},
                        {"id": '2.1.2.3', "description": "", "title": "CrioSkinner (gordura localizada)"},
                        {"id": '2.1.2.4', "description": "", "title": "Intradermoterapia"}
                    ]
                }
            }

            send(duvidas["msg"], phone, optionList=duvidas["optionList"])
            return jsonify({"status": "ok"}), 200

        elif response_menu == '2.1.3':
            duvidas = {
                "msg": "Estas são algumas dúvidas frequentes:",
                "optionList": {
                    "title": "Escolha uma categoria de procedimentos",
                    "buttonLabel": "Ver categorias",
                    "options": [
                        {"id": '2.1.3.1', "description": "", "title": "Laser Lavieen"},
                        {"id": '2.1.3.2', "description": "", "title": "Depilação a Laser"},
                        {"id": '2.1.3.3', "description": "", "title": "Tratamento para Melasma"},
                        {"id": '2.1.3.4', "description": "", "title": "Tratamento de Microvasos"},
                        {"id": '2.1.3.5', "description": "", "title": "Radiofrequência"},
                        {"id": '2.1.3.6', "description": "", "title": "Microagulhamento"},
                        {"id": '2.1.3.7', "description": "", "title": "PDRN com Microagulhamento"},
                        {"id": '2.1.3.8', "description": "", "title": "Skinbooster"},
                        {"id": '2.1.3.9', "description": "", "title": "NCTF 135 HA"},
                    ]
                }
            }

            send(duvidas["msg"], phone, optionList=duvidas["optionList"])
            return jsonify({"status": "ok"}), 200

        elif response_menu == '2.2':
            send(f"o telefone de numero {phone} esta solicitando cancelamento", phone='41998184071')
            return jsonify({"status": "ok"}), 200

        elif response_menu == '2.3':
            send('Nosso de atendimento é de segunda a sexta das 12hs até as 19hs', phone)
            return jsonify({"status": "ok"}), 200

        elif response_menu == '2.4':
            send("Qual a sua duvida?", phone)
            return jsonify({"status": "ok"}), 200

        elif response_menu == '3':
            session_ia[phone] = True
            process_conversation_ia(phone, texto='Oi')
            return jsonify({"status": "ok"}), 200

        elif response_menu == '4':
            human[phone] = True
            process_conversation(phone, texto=None)
            send(f"o telefone de numero {phone} precisa de ajuda e deseja falar com um atendente humano", phone='41995145182')
            return jsonify({"status": "ok"}), 200

        elif response_menu == '5':
            send("Localização da estética 📍", phone, location=True)
            return jsonify({"status": "ok"}), 200

        elif response_menu == '6':
            human[phone] = True
            process_conversation(phone, texto=None)
            send(f"o telefone de numero {phone} quer saber mais informações sobre as promoções", phone='41995145182')
            return jsonify({"status": "ok"}), 200

        procedures_explanation = [
                    {"id": '2.1.1.1', "description": "", "title": "Toxina Botulínica"},
                    {"id": '2.1.1.2', "description": "", "title": "Preenchimento Labial"},
                    {"id": '2.1.1.3', "description": "", "title": "Preenchimento Facial"},
                    {"id": '2.1.1.4', "description": "", "title": "Preenchimento de Olheiras"},
                    {"id": '2.1.1.5', "description": "", "title": "Rinomodelação"},
                    {"id": '2.1.1.6', "description": "", "title": "Limpeza de Pele Profunda"},
                    {"id": '2.1.1.7', "description": "", "title": "Hydra – Limpeza e Hidratação"},
                    {"id": '2.1.1.8', "description": "", "title": "Peeling de Ácido Retinoico"},
                    {"id": '2.1.1.9', "description": "", "title": "Peeling de Vitamina C"},
                    {"id": '2.1.2.1', "description": "", "title": "Enzimas"},
                    {"id": '2.1.2.2', "description": "", "title": "Manta Térmica"},
                    {"id": '2.1.2.3', "description": "", "title": "CrioSkinner (gordura localizada)"},
                    {"id": '2.1.2.4', "description": "", "title": "Intradermoterapia"},
                    {"id": '2.1.3.1', "description": "", "title": "Laser Lavieen"},
                    {"id": '2.1.3.2', "description": "", "title": "Depilação a Laser"},
                    {"id": '2.1.3.3', "description": "", "title": "Tratamento para Melasma"},
                    {"id": '2.1.3.4', "description": "", "title": "Tratamento de Microvasos"},
                    {"id": '2.1.3.5', "description": "", "title": "Radiofrequência"},
                    {"id": '2.1.3.6', "description": "", "title": "Microagulhamento"},
                    {"id": '2.1.3.7', "description": "", "title": "PDRN com Microagulhamento"},
                    {"id": '2.1.3.8', "description": "", "title": "Skinbooster"},
                    {"id": '2.1.3.9', "description": "", "title": "NCTF 135 HA"},
                    ]

        for fac in procedures_explanation:
            if response_menu == fac['id']:
                procedures(phone, fac['title'])
                return jsonify({"status": "ok"}), 200

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=8000)
