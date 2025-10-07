
from dateutil import parser
from datetime import datetime, timedelta
from utils.integration import get_patient, post_patient_create, create_online_scheduling, get_avaliable_days, list_all_professionals

scheduling_state = {}
scheduling_data = {}

state_registration = {}
registration_data = {}


def hello():
    time = datetime.now().time().replace(second=0, microsecond=0)
    day = '12:00'
    six = '18:00'
    midday = datetime.strptime(day, '%H:%M').time().replace(second=0, microsecond=0)
    afternoon = datetime.strptime(six, '%H:%M').time().replace(second=0, microsecond=0)

    if afternoon < time:
        return 'Boa noite'
    elif midday < time:
        return 'Boa tarde'
    else:
        return 'Bom dia'


def home_menu(text, phone, name):

    msg = f'''Olá  👋
{hello()} {name if name else 'tudo bem'}! Como posso te ajudar hoje?

                        Para  voltar ao menu incial digite X'''
    optionList = [
                {"id": '2.1', "description": "", "title": "Procedimentos"},
                {
                    "id": "1",
                    "description": "Agendamento de consulta ou retorno",
                    "title": "Agendamento"
                },
                {
                    "id": "6",
                    "description": "",
                    "title": "Promoções"
                },
                {
                    "id": "3",
                    "description": "Nossa atendente virtual",
                    "title": "Duda"
                },
                {
                    "id": "4",
                    "description": "Você esta sendo encaminhado para um atendente humano, Caso não tenha um retorno até 20 minutos retorna para o  chat",
                    "title": "Atendente"
                },
                {
                    "id": "5",
                    "description": "",
                    "title": "Localização"
                },{
                    "id": "2",
                    "description": "Duvidas, contra indicações e detalhes sobre procedimentos",
                    "title": "Mais informações"
                }
            ]

    return {"msg": msg,
            "optionList": {
                "title": "Opções disponíveis",
                "buttonLabel": "Lista de opções",
                "options": optionList
            }}


def format_date(data_str):
    day_current = datetime.now()

    try:
        data_obj = parser.parse(data_str, dayfirst=True)  # dayfirst=True para interpretar dia/mês/ano
        if data_obj > day_current:
            return data_obj.strftime("%Y-%m-%d")
        else:
            return None
    except (ValueError, OverflowError):
        return None


def start_registration(phone):
    state_registration[phone] = "nome"
    registration_data[phone] = {}
    return '''Olá! Para agendar, preciso fazer seu cadastro. Qual seu nome completo? 
    
    
    Para cancelar, digite X
    '''


def continue_registration(phone, mensagem):
    mensagem_format = mensagem.lower()

    if 'x' in mensagem_format:
        return None

    estado = state_registration.get(phone)
    dados = registration_data.get(phone, {})

    if estado == "nome":
        dados["nome"] = mensagem
        state_registration[phone] = "data_nascimento"
        registration_data[phone] = dados
        return "Qual sua data de nascimento? (formato: DD/MM/AAAA)"

    elif estado == "data_nascimento":
        dados["data_nascimento"] = mensagem
        state_registration[phone] = "sexo"
        registration_data[phone] = dados
        return "Qual seu sexo? (Masculino/Feminino)"

    elif estado == "sexo":
        dados["sexo"] = mensagem
        state_registration[phone] = "email"
        registration_data[phone] = dados
        return "Qual seu e-mail?"

    elif estado == "email":
        dados["email"] = mensagem
        dados["telefone"] = phone

        state_registration[phone] = "cpf"
        registration_data[phone] = dados
        return "Qual seu CPF?"

    elif estado == "cpf":
        dados["cpf"] = mensagem

        # Finalizar cadastro
        state_registration.pop(phone, None)
        registration_data.pop(phone, None)

        # Chamar a API para criar paciente
        sucesso = post_patient_create(
            name=dados["nome"],
            birth_date=dados["data_nascimento"],
            sex=dados["sexo"],
            email=dados["email"],
            phone=dados["telefone"],
            rg="",  # RG não coletado aqui, pode adaptar
            cpf=dados["cpf"]
        )

        if sucesso:
            return "Cadastro realizado com sucesso! Agora podemos agendar sua consulta." + start_scheduling(phone)
        else:
            return "Houve um problema no cadastro. Por favor, tente novamente."

    else:
        return "Erro no fluxo de cadastro. Vamos reiniciar. Qual seu nome completo?"


def procedures_professional(procedures_chosen):
    if isinstance(procedures_chosen, int):
        if procedures_chosen in [ 1, 2,3,6]:
            return ['Bruna', 'Karoline']
        elif procedures_chosen in [4, 5]:
            return ['Bruna']
        elif procedures_chosen in [7,8 ,9,10,11,13,14,15,16]:
            return ['Karoline']
        elif procedures_chosen in [17, 18, 19, 20, 21, 22]:
            return ['Paola']
        elif procedures_chosen == [12]:
            return ['Karoline', 'Paola']
    else:
        chosen = procedures_chosen.lower()

        if chosen in ['botox', 'preenchimento', 'bioestimulador de colágeno',
        'peelings']:
            return ['Bruna', 'Karoline']
        elif chosen in ['fios pdo', 'fios tração']:
            return ['Bruna']
        elif chosen in ['microvasos', 'microagulhamento', 'pdrn', 
        'nctf', 'skinbooster', 'lavieen', 'tratamentos corporais','crio skinner',
        'enzimas']:
            return ['Karoline']
        elif chosen in ['tratamentos gordura localizada', 'tratamentos celulite',
        'tratamento flacidez corporal radiofrequência', 'massagem drenagem',
        'massagem relaxante', 'massagem modeladora']:
            return ['Paola']
        elif chosen in ['depilação a laser']:
            return ['Karoline', 'Paola']


def is_registering(phone):
    return phone in state_registration


def start_scheduling(phone):
    #scheduling_state[phone] = "reason"
    scheduling_state[phone] = "tipe_scheduling"
    scheduling_data[phone] = {}
    return '''Você deseja realizar um novo agendamento ou é um retorno?
    
    1- Novo procedimento
    2- Retorno
    
                                             Digite 'X' para sair!'''


def continue_scheduling(phone, mensagem):

    mensagem_forma = mensagem.lower()

    if 'x  ' in mensagem_forma:
        scheduling_state.pop(phone, None)
        scheduling_data.pop(phone, None)
        return None

    estado = scheduling_state.get(phone)
    dados = scheduling_data.get(phone, {})

    if estado == "tipe_scheduling":
        if mensagem_forma in ['1', 'procedimento', 'novo', 'procedimento novo']:
            scheduling_state[phone] = "reason"

            global procedures
            
            procedures = [(1,'Botox'), (2,'Preenchinento'), (3,'Bioestimulador De colágeno'), (4,'Fios PDO'), (5,'Fios tração'), (6,'Peelings'), 
                    (7,'Microvasos'), (8,'Microagulhamento'), (9,'PDRN'), (10,'NCTF'), (11,'Skinbooster'), (12,'Depilação a laser'), (13,'Lavieen'),
                    (14,'Tratamentos Corporais'), (15,'Crio Skinner'), (16,'Enzimas'),  (17,'Tratamentos Gordura Localizada'),
                    (18,'Tratamentos Celulite'), (19,'Tratamento flacidez corporal Radiofrequência'), 
                    (20,'Massagem Drenagem'), (21,'Massagem Relaxante'), (22,'Massagem modeladora')]
            
            proces = "\n" + "\n ".join([f' {proc[0]}- {proc[1]}'for proc in procedures])

            return f''' Certo! Qual procedimento você deseja realizar? \n{proces}'''
        elif mensagem_forma in ['2', 'retorno']:
            scheduling_state[phone] = "profissional"
            profissionais = list_all_professionals()

            nomes = "\n " + "\n ".join([f' {idx+1}- {prof["name"]}' for idx, prof in enumerate(profissionais)])
            return f" Com qual profissional foi seu último atendimento? \n{nomes}"
        else:
            return "Por favor, responda com 1️⃣ para atendimento novo ou 2️⃣ para retorno."

    if estado == "reason":
        if isinstance(mensagem, str):
            mensagem = mensagem.title()
            if any(mensagem in i for _, i in procedures):
                professional_chosen = procedures_professional(mensagem)
            else:
                mensagem = int(mensagem)

        if isinstance(mensagem, int):
            if any(mensagem == idx for idx, _ in procedures):    
                professional_chosen = procedures_professional(mensagem)

            else:
                return 'procedimento invalido'
        dados["reason"] = mensagem
        scheduling_state[phone] = "profissional"
        if not isinstance(professional_chosen, list):
            professional_chosen = [professional_chosen]
        
        profissionais_formatados = "\n- " + "\n- ".join(f'{prof}' for prof in professional_chosen)
        return f'Digite o primeiro nome do profissional com quem deseja agendar o procedimento:{profissionais_formatados}'

    elif estado == 'profissional':
        profissionais = list_all_professionals()
        global nome_digitado
        nome_digitado = mensagem.strip().lower()

        profissional_encontrado = next(
            (prof for prof in profissionais if prof["name"].lower().split(' ')[0] in nome_digitado or prof for prof in profissionais if prof["name"].lower().split(' ')[0] == nome_digitado ),
            None
        )

        if nome_digitado == 'x':
            scheduling_data.pop(phone)
            scheduling_state.pop(phone)
            estado = None
            dados = None
            return start_scheduling(phone)

        if not profissional_encontrado:
            nomes_disponiveis = "\n- " + "\n- ".join([prof["name"] for prof in profissionais])
            return f"Profissional não encontrado. Por favor, digite um nome válido. Veja os disponíveis:{nomes_disponiveis}"

        dados["profissional"] = profissional_encontrado["name"]
        dados["profissional_id"] = profissional_encontrado["id"]
        scheduling_state[phone] = "day"
        scheduling_data[phone] = dados

        return "Qual o dia preferido? (Ex: DD/MM/AAAA)"

    elif estado == "day":
        msg = mensagem.lower()
        data_formatada = format_date(mensagem)

        if 'x' in msg:
            return None

        if data_formatada is None:
            return "Formato de data inválido. Por favor, envie no formato DD/MM/AAAA."

        dados["day"] = data_formatada
        time_free = get_avaliable_days(dados['day'], nome_digitado)      

        if not time_free:
            return "⚠️ Para Agendamentos os sabados fale com atendente humano. Caso queira continuar por aqui informe uma data valida. DD/MM/AAAA \n"\
            "Menu inicial digite X"

        profissional_id = dados.get("profissional_id")

        horarios_filtrados = [item['horario'] for item in time_free if item['proficional'] == profissional_id]
        if not horarios_filtrados:
            return f"⚠️ Não há horários disponíveis para esse profissional neste dia. Por favor escola outra data"

        dados["horarios_disponiveis"] = horarios_filtrados
        scheduling_data[phone] = dados

        lista_horarios = "\n- " + "\n- ".join(horarios_filtrados)
        scheduling_state[phone] = "hora"  # só avança aqui depois que já tem os horários

        return f"Horários disponíveis para este dia e profissional:\n{lista_horarios}"

    elif estado == "hora":
        msg = mensagem.lower()
        if 'x' in msg:
            return None
        dados["hora"] = msg
        scheduling_state[phone] = "observacao"
        return "Deseja adicionar alguma observação? Se não, responda 'não'."

    elif estado == "observacao":
        msg = mensagem.lower()
        if 'x' in msg:
            return None
        dados["observacao"] = msg if msg != "não" else ""

        scheduling_state.pop(phone, None)
        info = scheduling_data.pop(phone, {})

        # Aqui você chamaria sua função real de agendamento, por exemplo:
        # resposta_agendamento = agendar_com_api(info, phone)

        resumo = f"""✅ Agendamento solicitado:
- Procedimento: {info['reason']}
- Profissional: {info['profissional']}
- Data: {info['day']}
- Hora: {info['hora']}
- Observação: {info['observacao'] or 'Nenhuma'}"""

        dados = get_patient(phone)

        desired_time = info.get("hora", "")

        if "-" in desired_time:
            from_time, to_time = desired_time.split("-", 1)
        elif 'x' in desired_time:
            return ''
        else:
            try:
                dt = datetime.strptime(desired_time, "%H:%M")
                dt_fim = dt + timedelta(minutes=30)  # duração padrão
                from_time = dt.strftime("%H:%M")
                to_time = dt_fim.strftime("%H:%M")
            except ValueError:
                return "⚠️ Horário inválido. Use o formato HH:MM ou HH:MM-HH:MM"

        cpf = str(dados.get('OtherDocumentId', '')[:3])

        confirmation_date = create_online_scheduling(
            name=dados.get('Name'),
            consultation=info["reason"],
            phone=phone,
            cpf_3=cpf,
            email=dados.get("Email"),
            obs=info["observacao"],
            from_time=from_time,
            to_time=to_time,
            date=info["day"],
            personId=info['profissional_id']
        )

        if confirmation_date:
            return resumo + "\n\nVocê recebera a confirmação do agendamento via sms."
        else:
            return resumo + "\n\nNão foi possivel realizar o agendamento, tente novamente ou escolha a opção flar com atendente."

    return "Algo deu errado no processo. Vamos reiniciar. Qual o motivo do atendimento?"


def is_scheduling(phone):
    return phone in scheduling_state


control_procedures = []

def procedures(phone, texto):
    from app import send

    if texto:
        msg_lower = texto.lower()

        if "enzimas" in msg_lower:
            resposta1 = '''São ativos que vão ser injetados na região, com a função de tratar ( gordura localizada ou celulite ou flacidez ), vai depender da queixa do paciente. 
A aplicação é feita semanalmente, aplicação é tranquila e de fácil recuperação.'''
            send(resposta1, phone)

            resposta2 = '''Resultados são a partir da 3 semana.
Em média são feito de 5 a 10 sessões por protocolo. A ampola de 10ml é utilizada por região ( abdômen ou flancos ou costas ou interno de coxa entre outros). 
Os ativos escolhidos são feitos personalizados para cada paciente.'''
            send(resposta2, phone)

            resposta3 = '''Valor: 5 sessões R$600,00 em até 6x no cartão de crédito. 
10 sessões R$ 999,90 em até 6x no cartão de crédito.'''
            send(resposta3, phone)

            return ''

        elif "toxina botulínica" in msg_lower:
            resposta1 = '''A toxina botulínica é ideal para quem busca suavizar rugas de expressão e prevenir marcas futuras, promovendo um aspecto mais leve, descansado e rejuvenescido.
_______________________________________________
💉 Benefícios:
• Suaviza rugas e linhas de expressão
• Previne o surgimento de novas marcas
• Procedimento rápido e minimamente invasivo
• Retorno imediato às atividades
• Resultados naturais e progressivos'''
            send(resposta1, phone)

            resposta2 = '''⚠️ Contraindicações:
• Gestantes ou lactantes
• Doenças neuromusculares
• Alergia a componentes da fórmula
• Infecção ativa na área de aplicação
🔬 Marca utilizada: Dysport®️ – referência mundial em segurança, eficácia e durabilidade.
_______________________________________________
📍 Áreas tratadas:
• Terço Superior Completo: testa, glabela (entre as sobrancelhas), olhos (pés de galinha) e nariz ("bunny lines")
• Full Face: rosto completo + pescoço
⏱️ O procedimento é rápido, indolor e com retorno imediato à sua rotina.'''
            send(resposta2, phone)

            resposta3 = '''💰 Investimento:
• Terço Superior Completo com retoque:
 6x de R$ 133,33 no cartão ou 6% de desconto à vista no PIX ou dinheiro
• Full Face (rosto completo + pescoço):
 10x de R$ 160,00 no cartão ou 8% de desconto à vista no PIX ou dinheiro
Agende sua avaliação e descubra como a toxina botulínica pode valorizar ainda mais a sua beleza! 💖'''
            send(resposta3, phone)

            return 

        elif "preenchimento labial" in msg_lower:
            resposta1 = '''💋 Preenchimento Labial com Ácido Hialurônico – Realce o que você tem de mais lindo! 💋
O preenchimento labial com ácido hialurônico é ideal para quem deseja lábios mais volumosos, definidos e com contorno harmônico, sem perder a naturalidade.
_______________________________________________
✨ Benefícios:
• Aumenta o volume com naturalidade
• Define o contorno e melhora a simetria
• Corrige pequenas assimetrias e linhas ao redor da boca
• Resultado imediato e com acabamento ainda mais bonito nos dias seguintes
🧪 Substância utilizada: Ácido hialurônico, seguro e biocompatível com o organismo.
👩‍⚕️ Realizado pela Dra. Bruna, referência em preenchimento labial!
Com domínio de mais de 15 técnicas diferentes, ela escolhe a abordagem perfeita para cada tipo de lábio e desejo da paciente, sempre com olhar estético refinado e resultado sofisticado.'''
            send(resposta1, phone)

            resposta2 = '''💉 Procedimento tranquilo:
Utilizamos anestésico injetável, o que proporciona muito mais conforto durante toda a aplicação.
_______________________________________________
⚠️ Contraindicações:
• Gestantes ou lactantes
• Pacientes com doenças autoimunes ou infecções ativas na região'''
            send(resposta2, phone)

            resposta3 = '''💰 Investimento:
• 1ml por 10x de R$ 99,99 no cartão
• Ou com 8% de desconto à vista no PIX ou dinheiro
Agende sua avaliação e venha conquistar os lábios que você sempre sonhou — com segurança, bom gosto e um resultado encantador! 💖'''
            send(resposta3, phone)

            return

        elif "corrente russa" in msg_lower:
            resposta1 = '''A corrente russa é um tratamento estético que utiliza estímulos elétricos para provocar a contração dos músculos, promovendo tonificação, melhora da flacidez e aumento da firmeza muscular.
_______________________________________________
Como é feito?
Eletrodos são posicionados sobre a pele, nas regiões escolhidas, para estimular os músculos por meio de contrações controladas. O procedimento é confortável, e a intensidade é ajustada conforme a sensibilidade de cada paciente.

Principais regiões tratadas:
➡ Abdômen
➡ Glúteos
➡ Pernas
➡ Braços
➡ Interno de coxas'''
            send(resposta1, phone)

            resposta2 = '''Benefícios:
✅ Fortalece a musculatura
✅ Melhora a flacidez
✅ Auxilia na definição corporal
✅ Estimula a circulação sanguínea
✅ Pode ser associada a outros tratamentos estéticos

Sessões indicadas:
📅 De 5 a 10 sessões, conforme a avaliação e objetivo.'''
            send(resposta2, phone)

            resposta3 = '''Investimento:
💳 5 sessões por R$ 200,00 em até 2x
💳 10 sessões por R$ 400,00 em até 4x

Tratamento não invasivo, eficaz e com resultados progressivos. Agende sua avaliação e fortaleça seu corpo com tecnologia! 💪✨'''
            send(resposta3, phone)

            return

#--------------------------------------------------------------------------------------------------------------------------------------------
        elif "intradermoterapia" in msg_lower:
            resposta1 = '''A intradermoterapia é um procedimento estético que consiste na aplicação de ativos diretamente na pele ou no tecido subcutâneo, de acordo com a necessidade de cada paciente. É um tratamento extremamente versátil, que pode ser utilizado para diversos fins estéticos com ótimos resultados.
_______________________________________________
Indicações:
✨ Gordura localizada
✨ Flacidez
✨ Celulite
✨ Estrias
✨ Emagrecimento
✨ Ganho de massa muscular (com ativos específicos)
_______________________________________________
Benefícios:
✅ Atua direto na região tratada
✅ Reduz medidas e melhora o contorno corporal
✅ Estimula colágeno e melhora a firmeza da pele
✅ Ajuda a combater celulite e melhorar a textura
✅ Pode ser personalizada conforme o objetivo'''
            send(resposta1, phone)

            resposta2 = '''Contraindicações:
🚫 Gestantes e lactantes
🚫 Alergia aos ativos utilizados
🚫 Infecções ou doenças de pele na área tratada
🚫 Doenças autoimunes ou em tratamento oncológico (com avaliação médica)
_______________________________________________
Frequência:
As sessões podem ser feitas a cada 7 a 15 dias, conforme a indicação e a resposta de cada organismo.
Número de sessões:
Mínimo de 5 sessões, podendo chegar a 20 sessões conforme o tratamento.'''
            send(resposta2, phone)

            resposta3 = '''Investimento:
💳 5 sessões por 6x de R$ 100,00
💳 10 sessões por 10x de R$ 100,00

Procedimento rápido, eficaz e com resultados progressivos. Agende sua avaliação e comece hoje mesmo seu protocolo personalizado! ✨'''
            send(resposta3, phone)

            return
        
        elif "tratamento para melasma" in msg_lower:
            resposta1 = '''🌿 Tratamento Personalizado para Melasma
Cuidar do melasma vai muito além de clarear a pele — é preciso tratar com estratégia, segurança e personalização.

Nosso protocolo é montado de forma individualizada após avaliação, podendo incluir:
✨ Laser Lavieen
✨ Peelings específicos
✨ Intradermoterapia clareadora
✨ Rotina de skincare personalizada para manutenção e regeneração da pele
_______________________________________________
Também incluímos uma preparação da pele com ativos, peeling ou laser, que potencializam os resultados desde a primeira sessão.

📆 São indicadas de 5 a 10 sessões, dependendo da resposta da pele e grau do melasma.'''
            send(resposta1, phone)

            resposta2 = '''Benefícios:
✅ Clareamento gradual e seguro
✅ Controle da inflamação da pele
✅ Renovação celular
✅ Ação antioxidante e uniformização do tom
✅ Prolongamento dos resultados com home care orientado

É necessário passar por avaliação, pois cada pele responde de forma única ao tratamento.'''
            send(resposta2, phone)

            resposta3 = '''💳 Investimento médio: de R$ 800,00 a R$ 1.800,00
📆 Parcelamento em até 10x sem juros

Agende sua avaliação e inicie um cuidado completo, seguro e duradouro para sua pele! ✨'''
            send(resposta3, phone)

            return
        
        elif "manta térmica" in msg_lower:
            resposta1 = '''A manta térmica é um procedimento estético que utiliza o calor para promover a queima de gordura localizada, estimular o metabolismo, melhorar a circulação sanguínea e proporcionar relaxamento muscular. É um excelente aliado em protocolos de emagrecimento e tratamentos corporais.
_______________________________________________
Como é feito?
O paciente é envolvido por uma manta que emite calor de forma controlada. A elevação da temperatura corporal provoca a dilatação dos vasos, acelera o metabolismo e potencializa a eliminação de toxinas e líquidos. Pode ser associada a cosméticos específicos para potencializar os resultados.

Regiões tratadas:
Abdômen - Flancos - Coxas - Glúteos - Costas - Braços'''
            send(resposta1, phone)

            resposta2 = '''Benefícios:
✅ Auxilia na queima de gordura localizada
✅ Estimula a circulação sanguínea e linfática
✅ Ajuda na eliminação de toxinas
✅ Promove relaxamento muscular
✅ Potencializa resultados de outros procedimentos
_______________________________________________
Quantidade de sessões:
De 5 a 10 sessões, conforme avaliação e objetivo do paciente.'''
            send(resposta2, phone)

            resposta3 = '''Investimento:
💳 5 sessões por R$ 200,00 em até 2x no cartão
💳 10 sessões por R$ 400,00 em até 4x no cartão

Um tratamento confortável, acessível e eficaz para cuidar do seu corpo e bem-estar. Agende sua avaliação e venha experimentar! ✨'''
            send(resposta3, phone)

            return
        
        elif "preenchimento de olheiras" in msg_lower:
            resposta1 = '''Preenchimento de Olheiras com Ácido Hialurônico 💉✨
Quer se livrar do aspecto de cansaço e conquistar um olhar mais descansado ? O preenchimento de olheiras com ácido hialurônico é a solução ideal!

✅ Ameniza o aspecto profundidade e cansaço das olheiras
✅ Realizado em 2 sessões para evitar o surgimento de bolsas
✅ Procedimento seguro, com recuperação rápida
✅ Resultados naturais e durabilidade média de 12 meses'''
            send(resposta1, phone)

            resposta2 = '''Investimento acessível:
💳 10x de R$ 99,90
💰 ou 8% de desconto no PIX ou dinheiro

Agende sua avaliação e transforme seu olhar! ✨'''
            send(resposta2, phone)

            return
        
        elif "radiofrequência" in msg_lower:
            resposta1 = '''A radiofrequência é um tratamento estético não invasivo que utiliza ondas eletromagnéticas para aquecer as camadas mais profundas da pele, estimulando a produção de colágeno e elastina. O resultado é uma pele mais firme, rejuvenescida e com melhor textura.
______________________________________________
Como é feito?
Um aparelho emite ondas de calor controladas na pele, promovendo aquecimento profundo de forma confortável e segura. Esse calor ativa o colágeno existente e estimula a produção de novas fibras, melhorando a flacidez e a qualidade da pele.

Regiões tratadas:
Rosto (face, pescoço e colo) - Abdômen - Coxas - Glúteos - Braços - Flancos'''
            send(resposta1, phone)

            resposta2 = '''Benefícios:
✅ Melhora da firmeza e elasticidade da pele
✅ Redução da flacidez
✅ Estímulo à produção de colágeno
✅ Melhora na textura e aparência da pele
✅ Procedimento indolor e sem tempo de recuperação

Quantidade de sessões:
De 5 a 10 sessões, conforme avaliação e objetivo individual.'''
            send(resposta2, phone)

            resposta3 = '''Investimento:
💳 5 sessões por 3x de R$ 133,33
💳 10 sessões por 5x de R$ 120,00

A radiofrequência também pode ser associada a outros procedimentos para potencializar os resultados, como drenagem ou corrente russa (em casos corporais).

Agende sua avaliação e garanta uma pele mais firme, bonita e rejuvenescida! ✨'''
            send(resposta3, phone)

            return
        
        elif "preenchimento facial" in msg_lower:
            resposta1 = '''Preenchimento Facial com Ácido Hialurônico ✨
O preenchimento facial é ideal para quem deseja realçar a beleza natural com mais harmonia e definição no contorno do rosto. As regiões podem ser tratadas:

🔹 Malar (maçãs do rosto)
🔹 Mento (queixo)
🔹 Pré-maxila
🔹 Mandíbula
🔹 Têmporas
🔹 Código de barras (linhas ao redor dos lábios)
🔹 Bigode chinês (sulcos nasogenianos)'''
            send(resposta1, phone)

            resposta2 = '''Com o uso do ácido hialurônico, conseguimos promover um verdadeiro embelezamento facial, valorizando seus traços com naturalidade e sofisticação.
_______________________________________________
✅ Procedimento com anestesia injetável
✅ Recuperação tranquila
✅ Resultados imediatos e progressivos

💡 É necessária uma avaliação para definir a quantidade ideal de seringas para o seu caso.'''
            send(resposta2, phone)

            resposta3 = '''💰 Investimento:
• 1ml por 10x de R$ 99,99 no cartão
• Ou com 8% de desconto à vista no PIX ou dinheiro
Agende sua avaliação e venha conquistar os lábios que você sempre sonhou — com segurança, bom gosto e um resultado encantador! 💖'''
            send(resposta3, phone)

            return
        
        elif "rinomodelação" in msg_lower:
            resposta1 = '''A rinomodelação é um procedimento não cirúrgico indicado para:

🔹 Deixar o dorso do nariz mais reto
🔹 Corrigir a ponta caída
🔹 Harmonizar o contorno nasal de forma natural
_______________________________________________
O tratamento é feito com 1ml de ácido hialurônico, dividido em duas sessões para maior segurança.

✅ Recuperação rápida
✅ Pode retomar as atividades normalmente (12 horas )
✅ Resultados com durabilidade média de 12 meses'''
            send(resposta1, phone)

            resposta2 = '''❗ Contraindicações: não é indicado para quem deseja reduzir o tamanho do nariz ou tratar a aba nasal. Também não é recomendado para gestantes, lactantes ou pessoas com doenças autoimunes sem liberação médica.'''
            send(resposta2, phone)

            resposta3 = '''Investimento:
💳 10x de R$ 99,99 por seringa
💰 Ou 8% de desconto no PIX ou dinheiro

Agende sua avaliação e veja como pequenos ajustes podem fazer uma grande diferença no seu perfil! 👃✨'''
            send(resposta3, phone)

            return
        
        elif "laser lavieen" in msg_lower:
            resposta1 = '''O Lavieen é um laser de thulium que trata manchas, poros dilatados, linhas finas e melhora a textura da pele com pouco ou nenhum tempo de recuperação.
_______________________________________________
✅ Pode causar vermelhidão e leve inchaço por até 48h
✅ Pode usar maquiagem após 48h
✅ Pouca ou nenhuma descamação
✅ Atividades físicas liberadas após 24h
✅ A paciente recebe uma preparação da pele para otimizar os resultados'''
            send(resposta1, phone)

            resposta2 = '''💉 📌 A quantidade de sessões varia de 1 a 4, dependendo da pele e do objetivo.
❗Contraindicações: gestantes, lactantes, uso de isotretinoína recente, doenças autoimunes sem liberação médica ou infecções ativas na pele.'''
            send(resposta2, phone)

            resposta3 = '''Investimento:
💳 Sessão avulsa: 4x de R$ 99,99
💳 Pacote com 3 sessões: 6x de R$ 150,00

Agende sua avaliação e venha conquistar a pele dos sonhos com segurança e resultados reais! 💫'''
            send(resposta3, phone)

            return
        
        elif "depilação a laser" in msg_lower:
            resposta1 = '''A depilação a laser com a máquina Ácrus oferece mais eficácia e conforto no tratamento dos pelos, sendo indicada para todos os tipos de pele.
_______________________________________________
Benefícios:
✅ Redução duradoura dos pelos
✅ Diminui foliculite e pelos encravados
✅ Procedimento rápido e praticamente indolor
✅ Pele mais lisa e livre de agressões de lâmina ou cera'''
            send(resposta1, phone)

            resposta2 = '''📌 São recomendadas 10 sessões para melhores resultados, e o tratamento pode ser pago por sessão.'''
            send(resposta2, phone)

            resposta3 = '''Valores por sessão:
🔹 1 região: R$ 89,90
🔹 A partir da 2ª região: R$ 69,90 cada
🔹 Buço: R$ 39,90

Combos por sessão:
💥 Buço + Axila: R$ 75,00
💥 Axila + Virilha Completa + Buço: R$ 125,00
💥 Axila + Virilha Completa + Meia Perna: R$ 175,00
💥 Axila + Virilha Completa + Meia Perna + Buço: R$ 200,00
💥 Barba + Peito: R$ 125,00
💥 Peito + Abdômen + Costas: R$ 175,00
_______________________________________________
📅 Laser Day: toda segunda quinta-feira do mês com atendimentos especiais!

Agende sua sessão e comece sua jornada para uma pele mais livre, leve e lisa! 💖'''
            send(resposta3, phone)

            return
        
        elif "tratamento de microvasos" in msg_lower:
            resposta1 = '''A aplicação de glicose a 75% é uma técnica eficaz, segura e minimamente invasiva para o tratamento de microvasos (vasinhos finos nas pernas).
_______________________________________________
Benefícios:
✅ Melhora a aparência dos vasos visíveis
✅ Procedimento não cirúrgico e com recuperação rápida
✅ Estimula a circulação e melhora o aspecto da pele'''
            send(resposta1, phone)

            resposta2 = '''📌 São indicadas de 3 a 10 sessões, conforme avaliação individual.
⏱ Sessões com duração de 30 a 60 minutos.

❗Contraindicações: gestantes, lactantes, pessoas com infecções ativas na pele ou problemas circulatórios graves.'''
            send(resposta2, phone)

            resposta3 = '''Investimento:
💳 Sessão avulsa: R$ 199,99
💳 Pacote com 3 sessões: R$ 450,00 (em até 4x no cartão)
💳 Pacote com 10 sessões: 10x de R$ 130,00

Agende sua avaliação e diga adeus aos vasinhos com segurança e resultados reais! ✨'''
            send(resposta3, phone)

            return
        
        elif "microagulhamento" in msg_lower:
            resposta1 = '''O microagulhamento é um procedimento que utiliza microagulhas para estimular a produção natural de colágeno e promover uma renovação intensa da pele.

Benefícios:
✅ Melhora a textura e firmeza da pele
✅ Suaviza linhas finas e cicatrizes de acne
✅ Reduz poros dilatados
✅ Clareia manchas e uniformiza o tom da pele'''
            send(resposta1, phone)

            resposta2 = '''Na nossa clínica, o procedimento é potencializado com peeling associado, que otimiza os resultados e acelera o processo de renovação da pele.

📌 São indicadas de 1 até 5 sessões, conforme a necessidade e os objetivos de cada paciente.
⏱ Realizado com anestésico tópico para mais conforto.

❗Contraindicações: gestantes, lactantes, uso de isotretinoína nos últimos 6 meses, infecções ativas na pele ou doenças autoimunes sem liberação médica.'''
            send(resposta2, phone)

            resposta3 = '''Investimento:
💳 Sessão avulsa: R$ 400,00 (em até 4x no cartão)
💳 Pacote com 3 sessões: 10x de R$ 95,00

Agende sua avaliação e descubra como o microagulhamento pode transformar a saúde e aparência da sua pele! 💉💖'''
            send(resposta3, phone)

            return
        
        elif "peeling de ácido retinoico" in msg_lower:
            resposta1 = '''O peeling de ácido retinoico é um procedimento dermatológico que promove renovação celular profunda, sendo muito indicado para tratar manchas, acne e sinais de envelhecimento.

Como é feito?
O ácido retinoico é aplicado em consultório, de forma uniforme na pele limpa. Após a aplicação, o paciente vai para casa com o produto na pele, permanecendo com ele por algumas horas (de acordo com a orientação profissional), e depois faz a remoção. Nos dias seguintes pode ocorrer descamação leve a moderada, o que é esperado e faz parte do processo de renovação da pele.
_______________________________________________
Benefícios:
✅ Clareamento de manchas
✅ Melhora da textura e luminosidade da pele
✅ Controle da oleosidade e da acne
✅ Suaviza linhas finas
✅ Estimula a produção de colágeno'''
            send(resposta1, phone)

            resposta2 = '''Contraindicações:
❌ Gestantes e lactantes
❌ Pele sensibilizada ou com feridas ativas
❌ Uso recente de ácidos ou tratamentos agressivos
❌ Doenças de pele não controladas ou infecções locais'''
            send(resposta2, phone)

            resposta3 = '''Investimento:
💳 1 sessão: R$ 250,00 (em até 2x no cartão)
💳 Pacote com 3 sessões: R$ 450,00 (em até 4x no cartão)

O peeling de ácido retinoico é um excelente aliado no cuidado com a pele, proporcionando renovação, uniformização e rejuvenescimento com segurança.

Agende sua avaliação e veja se esse tratamento é indicado para o seu tipo de pele! 💛'''
            send(resposta3, phone)

            return
        
        elif "peeling de vitamina c" in msg_lower:
            resposta1 = '''O peeling de vitamina C da Cosmobeauty é um tratamento superficial que promove a renovação suave da pele, com ação antioxidante, clareadora e iluminadora. Ideal para quem busca uma pele mais radiante, uniforme e saudável, sem descamação intensa.
_______________________________________________
Como é feito?
O procedimento é realizado em consultório e segue etapas como:
Limpeza profunda da pele
Aplicação da vitamina C pura estabilizada com ativos renovadores
Finalização com protetor solar
É um peeling leve, sem dor e com retorno imediato às atividades, podendo ser feito em qualquer época do ano com os cuidados adequados com o sol.'''
            send(resposta1, phone)

            resposta2 = '''Benefícios:
✅ Ilumina e uniformiza o tom da pele
✅ Estimula o colágeno e melhora a firmeza
✅ Ação antioxidante que combate os radicais livres
✅ Suaviza manchas e melhora a textura
✅ Seguro e indicado para todos os tipos de pele

Contraindicações:
❌ Peles sensibilizadas ou com lesões ativas
❌ Alergia a componentes da fórmula
❌ Gestantes (necessário avaliação)'''
            send(resposta2, phone)

            resposta3 = '''💰 Investimento: R$ 150,00 por sessão

Realce a beleza natural da sua pele com o poder da vitamina C! Agende sua sessão e sinta a diferença desde a primeira aplicação. 🍊✨'''
            send(resposta3, phone)

            return
        
        elif "hydra limpeza" in msg_lower:
            resposta1 = '''O Hydra é um tratamento facial moderno, ideal para quem busca uma pele limpa, hidratada, viçosa e com glow imediato. É indicado para todos os tipos de pele e pode ser feito em qualquer época do ano.
_______________________________________________
Como é feito?
O procedimento é realizado em etapas, com produtos exclusivos da Cosmobeauty:
Higienização profunda da pele
Esfoliação física e/ou enzimática
Aplicação de ativos hidratantes e revitalizantes
Finalização com máscara e fotoproteção
O tratamento é indolor, não causa descamação e permite retorno imediato às atividades, sendo uma ótima opção para preparar a pele para eventos ou manter a saúde da pele em dia.'''
            send(resposta1, phone)

            resposta2 = '''Benefícios:
✅ Limpeza profunda e desobstrução dos poros
✅ Hidratação intensa e imediata
✅ Ação antioxidante e revitalizante
✅ Pele mais luminosa, macia e uniforme
✅ Pode ser associado a outros procedimentos estéticos'''
            send(resposta2, phone)

            resposta3 = '''💰 Investimento: R$ 89,90 por sessão

Realce o melhor da sua pele com o Hydra da Cosmobeauty! Agende sua sessão e conquiste uma pele saudável e iluminada! 💧✨'''
            send(resposta3, phone)

            return
        
        elif "pdrn com microagulhamento" in msg_lower:
            resposta1 = '''O PDRN (Polidesoxirribonucleotídeo) é um ativo biotecnológico extraído do DNA do salmão, altamente eficaz na regeneração celular e melhora global da pele. Ele estimula a produção de colágeno, melhora a textura e proporciona um efeito rejuvenescedor natural e progressivo.

Como é feito?
O tratamento é realizado em conjunto com o microagulhamento com Dermapen, o que aumenta significativamente a absorção do PDRN.
Aplicação de anestésico tópico
Realização do microagulhamento, criando microcanais na pele
Aplicação do PDRN, que penetra profundamente, agindo diretamente nas células'''
            send(resposta1, phone)

            resposta2 = '''Principais benefícios:
✅ Estimula a regeneração e reparação da pele
✅ Reduz rugas finas e melhora a firmeza
✅ Devolve o viço, brilho e hidratação
✅ Auxilia na cicatrização e melhora a textura
✅ Uniformiza o tom da pele

Contraindicações:
❌ Gestantes e lactantes
❌ Pele com infecção ativa ou feridas
❌ Doenças autoimunes (sem liberação médica)
❌ Alergia a componentes da fórmula
_______________________________________________
📌 A quantidade de sessões pode variar de acordo com a necessidade da pele e os objetivos desejados.'''
            send(resposta2, phone)

            resposta3 = '''💰 Investimento:
• 1 sessão: 5x de R$ 110,00
• Pacote com 3 sessões: 10x de R$ 141,00

Agende sua avaliação e experimente o poder do PDRN: pele mais jovem, renovada e saudável! 💧✨'''
            send(resposta3, phone)

            return
        
        elif "nctf 135 ha" in msg_lower:
            resposta1 = '''O NCTF 135 HA é um complexo nutritivo de origem francesa que contém ácido hialurônico + 55 ativos, incluindo vitaminas, aminoácidos, antioxidantes e minerais. Ele atua diretamente na revitalização profunda da pele, trazendo resultados visíveis em textura, firmeza e luminosidade.
_______________________________________________
Como é feito o procedimento?
O NCTF pode ser aplicado de duas formas, conforme a necessidade da pele:
✔️ Microagulhamento com Dermapen, para melhorar a absorção dos ativos
✔️ Ou aplicação ponto a ponto com microinjeções, direto na pele
O procedimento é realizado com anestésico tópico, garantindo conforto durante a sessão.'''
            send(resposta1, phone)

            resposta2 = '''Benefícios do NCTF:
✅ Hidratação profunda e duradoura
✅ Melhora da textura, elasticidade e viço da pele
✅ Estímulo de colágeno e ação antioxidante
✅ Redução de poros dilatados e linhas finas
✅ Mais luminosidade e aspecto de pele saudável
_______________________________________________
Indicado para: peles cansadas, opacas, com sinais iniciais de envelhecimento ou pós-procedimentos agressivos.

Contraindicações:
❌ Gestantes e lactantes
❌ Doenças de pele em atividade
❌ Alergia a algum componente da fórmula

📌 São indicadas de 3 a 5 sessões, conforme avaliação e objetivo.'''
            send(resposta2, phone)

            resposta3 = '''💰 Investimento – Pacote com 3 sessões:
🔹 10x de R$ 114,00 no cartão

Agende sua avaliação e descubra o poder do NCTF: nutrição intensa, hidratação e rejuvenescimento em um só tratamento! 💉✨'''
            send(resposta3, phone)

            return
        
        elif "skinbooster" in msg_lower:
            resposta1 = '''O Skinbooster é um tratamento estético que utiliza ácido hialurônico de baixa concentração para promover uma hidratação intensa e duradoura da pele, melhorando sua textura, elasticidade e viço natural.

Como é feito o procedimento?
O Skinbooster é aplicado por meio de microinjeções superficiais em toda a área a ser tratada, utilizando uma agulha fina ou cânula, com aplicação de anestésico tópico para maior conforto. O procedimento é rápido, seguro e permite retorno imediato às atividades.'''
            send(resposta1, phone)

            resposta2 = '''Benefícios do Skinbooster:
✅ Hidratação profunda e prolongada
✅ Melhora da firmeza e elasticidade da pele
✅ Suavização de linhas finas
✅ Aumento do viço e luminosidade natural
✅ Textura mais uniforme e pele mais macia

Contraindicações:
❌ Gestantes e lactantes
❌ Infecções ou inflamações ativas na área tratada
❌ Alergia a algum componente do produto
❌ Doenças autoimunes sem liberação médica
_______________________________________________
São indicadas de 3 a 5 sessões, conforme avaliação do profissional e necessidade da pele.'''
            send(resposta2, phone)

            resposta3 = '''💰 Pacote com 3 sessões:
🔹 10x de R$ 119,97 no cartão

Agende sua avaliação e proporcione à sua pele uma hidratação profunda e renovadora com o Skinbooster! 💧✨'''
            send(resposta3, phone)

            return
        
        elif "limpeza de pele profunda" in msg_lower:
            resposta1 = '''A limpeza de pele profunda é um procedimento essencial para remover impurezas, cravos, excesso de oleosidade e células mortas, promovendo uma pele mais saudável, limpa e revitalizada.

Como é feito?
Realizamos uma higienização completa, seguida de peeling de diamante para esfoliação suave e eficaz, extração manual dos cravos, aplicação de máscaras específicas para acalmar e nutrir a pele, finalizando com hidratação e proteção.

Tempo de duração: aproximadamente 1h30.'''
            send(resposta1, phone)

            resposta2 = '''Benefícios:
✅ Desobstrução dos poros
✅ Redução da oleosidade e acne
✅ Melhora da textura e aparência da pele
✅ Estímulo da renovação celular
✅ Pele mais fresca, limpa e radiante'''
            send(resposta2, phone)

            resposta3 = '''Investimento: R$ 139,90 por sessão

Agende sua limpeza de pele profunda e conquiste um rosto mais luminoso e saudável! 💆‍♀️✨'''
            send(resposta3, phone)

            return

        elif "crioskinner" in msg_lower:
            resposta1 = '''A CrioliSkinner é um procedimento moderno e eficaz para eliminar gordura localizada em diversas áreas do corpo, utilizando resfriamento controlado para congelar e eliminar as células de gordura sem agredir a pele ou tecidos ao redor.

Regiões tratadas:
Abdômen - Flancos - Costas - Braços - Pernas - Interno de coxa - Papada
_______________________________________________
Benefícios:
✅ Redução significativa da gordura localizada
✅ Procedimento não invasivo e seguro
✅ Resultados naturais e progressivos
✅ Sem necessidade de cirurgia ou tempo de recuperação prolongado
✅ Tratamento personalizado para diferentes áreas do corpo'''
            send(resposta1, phone)

            resposta2 = '''Como funciona o procedimento?

A sessão dura entre 6 a 14 horas, dependendo da área a ser tratada.
Pode ser realizada em até 2 dias consecutivos, com um intervalo máximo de 7 dias entre as sessões.
No dia do procedimento, o paciente recebe um tratamento VIP, com orientação alimentar especial para o dia e incentivo a descansar, aproveitar para relaxar e até assistir sua série favorita enquanto o tratamento age.
O procedimento é tranquilo, confortável e permite que você tire o dia para cuidar de si mesmo.
_______________________________________________
Contraindicações:
❌ Gravidez e lactação
❌ Doenças cardiovasculares graves
❌ Sensibilidade ao frio (como crioglobulinemia)
❌ Lesões ou inflamações na área a ser tratada
❌ Problemas circulatórios severos'''
            send(resposta2, phone)

            resposta3 = '''Investimento e Acompanhamento:
O valor do tratamento varia entre R$ 1.700,00 a R$ 3.000,00, dependendo da área e tempo necessário.
O pacote inclui:

Avaliação presencial para definir tempo e quantidade ideal de sessões
Acompanhamento com nutricionista
Detox corporal para potencializar os resultados
Pagamento facilitado em até 10x
Agende sua avaliação e viva a experiência de eliminar gordura localizada com conforto e cuidado completo! ❄️✨'''
            send(resposta3, phone)

            return