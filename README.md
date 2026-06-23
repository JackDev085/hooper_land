# Ballers085 Backend

Este é o backend da plataforma **Ballers085**, uma API RESTful de alta performance desenvolvida com **FastAPI**, **SQLModel** (com base em SQLAlchemy e Pydantic) e **SQLite/PostgreSQL** para gerenciamento de treinos de basquete, usuários, rankings, sequências (streaks) e agendamento de partidas.

---

## 🏗️ Arquitetura do Projeto

O backend segue uma arquitetura em camadas limpa e com divisão clara de responsabilidades:

```
backend/
├── api/             # Camada de Apresentação (Rotas HTTP, Endpoints FastAPI)
├── core/            # Configurações globais, segurança (JWT) e conexão com banco
├── models/          # Entidades e tabelas do banco de dados (SQLModel)
├── repositories/    # Camada de Acesso a Dados (Queries e persistência)
├── schemas/         # Modelos de validação de entrada/saída (Pydantic/SQLModel)
├── services/        # Regras de Negócio (Camada de Serviço)
└── tests/           # Suíte de testes automatizados (Pytest)
```

### Fluxo de Dados:
`Request ➔ Endpoint (API) ➔ Service (Regras de Negócio) ➔ Repository (Acesso a Dados) ➔ Database`

---

## 🛠️ Tecnologias Utilizadas

- **FastAPI**: Framework web moderno, rápido e de alta performance.
- **SQLModel**: ORM híbrido que integra o poder do SQLAlchemy com a validação do Pydantic.
- **Pytest**: Estrutura de testes automatizados robusta e extensível.
- **Passlib & JWT**: Criptografia de senhas (bcrypt) e autenticação segura via JSON Web Tokens.

---

## 🚀 Como Executar Localmente

### 1. Requisitos
- Python 3.10 ou superior instalado.

### 2. Clonar e Acessar a Pasta
```bash
cd backend
```

### 3. Configurar Ambiente Virtual (venv)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar as Variáveis de Ambiente
Crie um arquivo `.env` na raiz da pasta `backend/` seguindo o exemplo abaixo:
```env
SECRET_KEY=sua_chave_secreta_aqui
POSTGRES_URL_FASTAPI=postgresql://usuario:senha@localhost:5432/ballersdb
PROD=False
```
> [!NOTE]
> Se nenhuma variável de ambiente for configurada localmente ou em testes, o sistema iniciará automaticamente usando um banco de dados SQLite local (`database.db`) e uma chave JWT padrão para facilitar o desenvolvimento.

### 6. Executar o Servidor de Desenvolvimento
```bash
uvicorn main:app --reload
```
A API estará acessível em `http://127.0.0.1:8000`. 
A documentação interativa (Swagger UI) pode ser visualizada em `http://127.0.0.1:8000/docs`.

---

## 📌 Principais Endpoints

- **Autenticação (`/token`, `/register`, `/me`)**: Registro de hoopers, login de acesso e consulta de perfil.
- **Treinos (`/workouts`)**: Listagem, criação de treinos, exclusão e conclusão (`/complete`) com atualização dinâmica de sequência (streak).
- **Exercícios (`/exercises`)**: Cadastro e listagem de exercícios recomendados.
- **Partidas e Agendamentos (`/games`)**: Controle de jogos agendados, lista de presença de atletas e fotos de partidas passadas.