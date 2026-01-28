# Frontend V2 - Hybrid Architecture

## 📋 Contexto

Este módulo é a **interface visual para agendamento rápido** do sistema híbrido (Hybrid Flow). Enquanto o fluxo via WhatsApp (chatbot) oferece uma experiência conversacional guiada, o Frontend Web permite que clientes realizem agendamentos de forma autônoma através de um formulário intuitivo.

O objetivo é oferecer **múltiplos canais de entrada** sem duplicar lógica de negócio, reutilizando 100% dos services existentes.

## 🏗 Arquitetura

### Diagrama de Integração
```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│   ┌─────────────────┐                                           │
│   │  Streamlit App  │ ← Interface visual (mobile-responsive)   │
│   └────────┬────────┘                                           │
│            │                                                    │
│            │ Direct Import (sys.path)                           │
│            ▼                                                    │
├─────────────────────────────────────────────────────────────────┤
│                         Services Layer                          │
│   ┌───────────────────────┐  ┌───────────────────────────────┐  │
│   │ google_calendar_svc   │  │   agendamentos_service        │  │
│   ├───────────────────────┤  ├───────────────────────────────┤  │
│   │ listar_horarios_livres│  │ salvar_agendamento            │  │
│   │ criar_evento          │  └───────────────────────────────┘  │
│   │ horario_disponivel    │                                     │
│   └───────────────────────┘                                     │
├─────────────────────────────────────────────────────────────────┤
│                         Data Layer                              │
│   ┌─────────────────┐          ┌──────────────────────┐         │
│   │ Google Calendar │          │ Supabase (Postgres)  │         │
│   └─────────────────┘          └──────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### Estratégia de Integração: Direct Import

O Frontend importa diretamente os módulos de `services/` configurando o `sys.path` para incluir a raiz do projeto. Isso permite:

1. **Reutilização Total**: Nenhuma lógica de calendário ou banco de dados é reescrita.
2. **Consistência**: Mesmas validações e regras de negócio do chatbot.
3. **Manutenção Simplificada**: Correções nos services beneficiam ambos os canais.

```python
# Padrão de importação utilizado em frontend/app.py
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Agora os services são importáveis
from services.google_calendar_service import listar_horarios_livres, criar_evento
from services.agendamentos_service import salvar_agendamento
```

## 📊 Roadmap de Implementação

### ✅ Fase 1: Setup do Ambiente (Streamlit)
- [x] Configuração de `st.set_page_config` (título, ícone)
- [x] Layout responsivo com containers
- [x] Estilização básica (CSS customizado)

### ✅ Fase 2: Integração com Google Calendar (Leitura)
- [x] Importação de `listar_horarios_livres`
- [x] Exibição dinâmica de horários disponíveis
- [x] Fallback para mensagem "sem horários" se vazio

### ✅ Fase 3: Formulário de Dados do Cliente
- [x] Nome (obrigatório)
- [x] Telefone/WhatsApp (obrigatório)
- [x] Serviço (selectbox: Limpeza, Manutenção, Instalação)
- [x] Endereço completo (Rua, Número, Bairro, Cidade, CEP)
- [x] Data e Hora do agendamento

### ✅ Fase 4: Integração com Services (Escrita)
- [x] Validação de campos obrigatórios
- [x] Chamada a `criar_evento` (Google Calendar)
- [x] Chamada a `salvar_agendamento` (Supabase)
- [x] Feedback visual (sucesso/erro)

## 💡 Decisões Técnicas

### Por que Streamlit?

| Critério           | Streamlit            | Flask + Templates | FastAPI + React     |
|--------------------|----------------------|-------------------|---------------------|
| Velocidade de Dev  | ⭐⭐⭐⭐⭐               | ⭐⭐⭐               | ⭐⭐                   |
| Mobile-Responsive  | ⭐⭐⭐⭐ (automático)    | ⭐⭐ (manual CSS)   | ⭐⭐⭐⭐⭐ (se bem feito) |
| Complexidade       | Baixa                | Média             | Alta                |
| Python Puro        | ✅                    | ✅                 | ❌ (requer JS)       |
| Prototipagem       | Excelente            | Boa               | Lenta               |

**Justificativa**: Para um MVP de agendamento rápido, o Streamlit oferece a melhor relação custo-benefício:
- **Código 100% Python**: Sem necessidade de conhecimento em JavaScript/React.
- **Mobile-Friendly**: Layout responsivo por padrão.
- **Deploy Simples**: `streamlit run app.py` ou deploy direto no Streamlit Cloud.
- **Integração Nativa**: Importa serviços Python diretamente.

### Limitação Conhecida (V1)

A atualização dinâmica de horários ao mudar a data dentro de um `st.form` é limitada pelo Streamlit (forms não re-executam callbacks isoladamente). Na V1, o usuário seleciona data e hora, e a disponibilidade é validada no momento do submit.

**Possível melhoria futura (V2)**: Usar `st.experimental_fragment` ou mover o seletor de data para fora do form.

## 🚀 Como Executar

```bash
# A partir da raiz do projeto
cd bot-ar-condicionado

# Ativar ambiente virtual
.venv\Scripts\activate  # Windows 
# source .venv/bin/activate  # Linux/Mac

# Instalar dependências (se não instalado)
pip install streamlit

# Rodar o frontend
streamlit run frontend/app.py
```

O app estará disponível em `http://localhost:8501`.

## 📁 Estrutura de Arquivos

```
frontend/
├── planning.md   # Este documento
└── app.py        # Aplicação Streamlit
```
