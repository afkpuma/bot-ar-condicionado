from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional


class Endereco(BaseModel):
    """
    Modelo de endereço do cliente.
    
    Valida automaticamente os campos obrigatórios e formatos.
    """
    
    rua: str = Field(
        ..., 
        min_length=3, 
        description="Nome da rua",
        examples=["Rua das Flores"]
    )
    
    numero: str = Field(
        ..., 
        description="Número do imóvel",
        examples=["123", "456-A"]
    )
    
    bairro: str = Field(
        ..., 
        min_length=2, 
        description="Nome do bairro",
        examples=["Centro", "Jardim Paulista"]
    )
    
    cidade: str = Field(
        ..., 
        min_length=2, 
        description="Nome da cidade",
        examples=["São Paulo", "Rio de Janeiro"]
    )
    
    cep: str = Field(
        ..., 
        pattern=r"^\d{5}-?\d{3}$", 
        description="CEP no formato XXXXX-XXX ou XXXXXXXX",
        examples=["01234-567", "01234567"]
    )
    
    complemento: Optional[str] = Field(
        None, 
        description="Complemento opcional (apto, bloco, etc)",
        examples=["Apto 101", "Bloco B"]
    )


class Cliente(BaseModel):
    """
    Modelo de cliente do sistema.
    
    Contém informações pessoais e de contato.
    """
    
    nome: str = Field(
        ..., 
        min_length=3, 
        description="Nome completo do cliente",
        examples=["João da Silva"]
    )
    
    telefone: str = Field(
        ..., 
        pattern=r"^\d{10,11}$", 
        description="Telefone com DDD (apenas números)",
        examples=["11987654321"]
    )
    
    endereco: Endereco = Field(
        ..., 
        description="Endereço completo do cliente"
    )


class AgendamentoRequest(BaseModel):
    """
    Modelo de requisição de agendamento.
    
    Usado no endpoint POST /agendar.
    Valida automaticamente que data e hora formam um datetime válido.
    """
    
    servico: str = Field(
        ..., 
        pattern=r"^(limpeza|instalacao|manutencao)$",
        description="Tipo de serviço",
        examples=["limpeza", "instalacao", "manutencao"]
    )
    
    data: str = Field(
        ..., 
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data no formato YYYY-MM-DD",
        examples=["2026-01-15"]
    )
    
    hora: str = Field(
        ..., 
        pattern=r"^\d{2}:\d{2}$",
        description="Hora no formato HH:MM",
        examples=["14:30", "09:00"]
    )
    
    cliente: Cliente = Field(
        ..., 
        description="Dados do cliente"
    )
    
    # Campo interno calculado após validação
    _data_hora: datetime = None
    
    @model_validator(mode='after')
    def validar_data_hora(self) -> 'AgendamentoRequest':
        """
        Valida que data + hora formam um datetime válido.
        
        Raises:
            ValueError: Se a combinação de data e hora for inválida.
        """
        try:
            self._data_hora = datetime.strptime(
                f"{self.data} {self.hora}",
                "%Y-%m-%d %H:%M"
            )
        except ValueError as e:
            raise ValueError(
                f"Data ou hora em formato inválido. "
                f"Formato esperado: data=YYYY-MM-DD, hora=HH:MM. Detalhe: {e}"
            )
        return self
    
    @property
    def data_hora(self) -> datetime:
        """Retorna o datetime calculado a partir de data + hora."""
        return self._data_hora


class MensagemWhatsApp(BaseModel):
    """
    Modelo de mensagem recebida do WhatsApp.
    
    Usado no endpoint POST /whatsapp.
    """
    
    telefone: str = Field(
        ..., 
        pattern=r"^\d{10,11}$",
        description="Telefone com DDD (apenas números)",
        examples=["11987654321"]
    )
    
    mensagem: str = Field(
        ..., 
        min_length=1,
        description="Mensagem enviada pelo cliente",
        examples=["Olá", "Quero agendar uma limpeza"]
    )
