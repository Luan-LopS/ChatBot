
# Atendiemento Automatizado Whatsapp 

##Flask + Z-API + integração clincorp

Este é uma sistema de **automação inteligente para Whatsapp**, desenvolvido com Python, Flask, Z-API, e integrado com sistema da clincorp, ideal para clinicas de estéticas, dentitas e medicos. Consultório que desejam automatizar seus atendimentos com resposatas rápidas, agendamento de serviços, retirada de duvidas de procediementos, cancelamento de agendamento, verificação de proficional disponivel e data e hora para atendiemento, além de ter um atendente com inteligência artificial.

---

## 💼 Sobre o Projeto

> Este projeto foi desenvolvido com o objetivo de automatizar processos de atendimento, reduzindo a carga da equipe humana e melhorando a experiência do cliente final. 

---

## 🚀 Funcionalidades

- 📲 Recebimento automático de mensagens via WhatsApp (Z-API)
- 👤 Cadastro de pacientes/clientes
- 📅 Agendamento de procedimentos
- ❓ FAQ com respostas rápidas a dúvidas frequentes
- 📍 Envio de localização da empresa
- 💬 Chat com Inteligência Artificial (opcional)
- 🧑 Atendimento humano manual quando necessário
- 🔄 Sessão temporária com expiração automática por inatividade

---

## 🛠️ Tecnologias Utilizadas

- Python 3.8+
- Flask
- Z-API (WhatsApp Gateway)
- Requests
- dotenv
- Threads (Timers para controle de sessão)
- Arquitetura modular

---

## 📁 Estrutura do Projeto
    project/
    ├── chat/
    │ ├── chat.py # Menus e fluxo conversacional
    │ └── ia.py # Integração com IA
    │
    ├── utils/
    │ └── integration.py # Funções externas (API de pacientes, cancelamentos)
    │
    ├── .env # Variáveis de ambiente
    ├── main.py # Aplicação Flask principal
    ├── requirements.txt # Dependências
    └── README.md # Este documento







---------------------------------------------------------------------------------------------------
# 📌 Nome do Projeto
<!--
Escreva o nome do seu projeto de forma clara e profissional.
Exemplo: Sistema de Atendimento Inteligente via WhatsApp
-->

Uma descrição curta do que seu projeto faz ou qual problema ele resolve.
<!--
Exemplo: Este sistema automatiza o atendimento de clínicas via WhatsApp, permitindo cadastro, agendamento, envio de localização e integração com IA.
-->

---

## 📷 Demonstração (opcional)
<!--
Aqui você pode adicionar imagens, gifs ou vídeos do sistema em funcionamento.
Use um link de imagem ou arraste a imagem no GitHub para gerar o link automaticamente.
-->
![Demo](https://link-da-sua-imagem.gif)

---

## 🧰 Tecnologias Utilizadas
<!--
Liste aqui as principais ferramentas e tecnologias usadas no projeto.
Exemplo:
-->
- Python 3.8+
- Flask
- Z-API
- dotenv
- Requests
- Threading
- Integração com APIs externas

---

## 🚀 Funcionalidades
<!--
Liste as principais funcionalidades do sistema com uma checklist.
Exemplo:
-->
- [x] Recebimento automático de mensagens via WhatsApp
- [x] Cadastro de pacientes/clientes
- [x] Agendamento de serviços
- [x] Chat com IA (opcional)
- [x] FAQ automatizado
- [x] Envio de localização
- [x] Sessão temporária com expiração automática

---

## 🗂️ Estrutura de Pastas
<!--
Explique brevemente como está organizado o projeto.
Exemplo:
-->
project/
├── chat/ # Fluxo do atendimento e IA
│ ├── chat.py
│ └── ia.py
├── utils/ # Integrações externas (API, cancelamentos)
│ └── integration.py
├── main.py # Aplicação principal (Flask)
├── .env # Variáveis de ambiente (não subir para o GitHub)
├── requirements.txt # Lista de dependências
└── README.md # Este arquivo

yaml
Copiar
Editar

---

## ⚙️ Instalação

Passo a passo para rodar o projeto localmente:

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/seu-projeto.git

# 2. Acesse a pasta
cd seu-projeto

# 3. Crie um ambiente virtual (Python)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Crie um arquivo .env com as variáveis de ambiente
# Exemplo:
# Z-API=seu_id
# API=seu_token
# CLIENT_TOKEN=token_cliente

# 6. Execute o servidor
python main.py
✅ Pré-requisitos
Python 3.8 ou superior

Conta na Z-API (para integração WhatsApp)

Acesso à internet

Editor de código como VS Code

💡 Melhorias Futuras (opcional)
<!-- Liste melhorias que podem ser feitas no futuro. -->
 Painel administrativo em frontend

 Login com autenticação

 Testes automatizados

 Armazenamento em banco de dados

 Internacionalização (i18n)

🤝 Contribuindo (opcional)
Se desejar contribuir com este projeto:

Faça um fork

Crie uma branch com a sua feature:

bash
Copiar
Editar
git checkout -b minha-feature
Faça o commit das suas alterações:

bash
Copiar
Editar
git commit -m 'feat: minha nova feature'
Faça o push para a sua branch:

bash
Copiar
Editar
git push origin minha-feature
Abra um Pull Request


bash'''



📬 Contato
Quer conversar sobre o projeto, contratar ou colaborar?

📧 Email: seuemail@dominio.com

💼 LinkedIn: linkedin.com/in/seu-perfil

📱 WhatsApp: Clique aqui para falar comigo

🧾 Licença
Este projeto está licenciado sob a licença MIT.
Você pode usá-lo, modificar e distribuir livremente.

✅ Dica:
Se for usar o GitHub como vitrine de portfólio, preencha esse README.md com cuidado. É o que os recrutadores e clientes verão primeiro. Vale caprichar! 😉