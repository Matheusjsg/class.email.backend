import os, re, requests
from typing import Tuple
from .generation import generate_response_ai

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
CLASSIFICATION_MODEL = "facebook/bart-large-mnli"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# --- Categorias e padrões (compilados) ---
categorias = {"Solicitação de Status": [
        r"\bstatus\b", r"andamento", r"progresso", r"atualização", r"como está",
        r"quando chega", r"verificar status", r"confirmação de status", r"acompanhamento",
        r"situação do pedido", r"rastreamento", r"previsão de entrega", r"aguardando resposta",
        r"informações sobre pedido", r"situação atual", r"pedido enviado", r"pedido recebido",
        r"atraso na entrega", r"qual o prazo", r"última atualização", r"pedido processado",
        r"detalhes do pedido", r"solicito atualização", r"pedido em andamento"
    ],

    "Envio de Documento": [
        r"em anexo", r"segue o arquivo", r"documento enviado", r"pdf anexo", r"\banexo\b",
        r"envio de contrato", r"envio de relatório", r"comprovante", r"formulário preenchido",
        r"planilha", r"\barquivo\b", r"documentação anexa", r"arquivo para assinatura",
        r"envio de certificado", r"relatório final", r"cópia digital", r"documento digital",
        r"envio de dados", r"arquivos anexados", r"documento oficial"
    ],

    "Pedido de Suporte": [
        r"erro", r"problema", r"ajuda", r"atenção na minha conta", r"suporte", r"não funciona", 
        r"bug", r"dúvida", r"falha", r"questão técnica", r"assistência", r"reclamação técnica",
        r"não consigo", r"não está funcionando", r"erro ao acessar", r"erro sistema",
        r"problema urgente", r"ajuda imediata", r"erro na plataforma", r"suporte técnico",
        r"interrupção do serviço", r"erro de login", r"sistema travado", r"solicito suporte",
        r"problema técnico"
    ],

    "Alerta de Segurança": [
        r"segurança", r"vulnerabilidade", r"ataque", r"phishing", r"fraude", r"suspeito",
        r"saque não autorizado", r"invadida", r"acesso não autorizado", r"senha comprometida",
        r"invadir", r"atividade suspeita", r"alerta de segurança", r"alerta crítico",
        r"tentativa de invasão", r"roubo de dados", r"problema de segurança", r"hacker",
        r"fraude detectada", r"alerta urgente", r"risco de segurança", r"invasão detectada",
        r"ataque cibernético", r"acesso suspeito", r"tentativa de fraude", r"alerta de risco",
        r"atividade incomum"
    ],

    "Reclamação": [
        r"insatisfeito", r"reclamação", r"péssimo", r"ruim", r"decepcionado",
        r"não gostei", r"problema recorrente", r"não atende", r"má experiência",
        r"insatisfação", r"demora", r"atraso", r"decepção", r"serviço ruim",
        r"não resolveram", r"atendimento ineficiente", r"frustrado", r"reclamo",
        r"descontentamento", r"não satisfeito", r"experiência negativa", r"falha no serviço",
        r"reclamação urgente", r"problema constante"
    ],

    "Mensagem Social": [
        r"feliz natal", r"parabéns", r"amizades", r"felicitações", r"cumprimentos",
        r"bom dia", r"boa tarde", r"boa noite", r"obrigado", r"agradeço", r"feliz aniversário",
        r"felicidades", r"saudações", r"boa sorte", r"feliz ano novo", r"feliz páscoa",
        r"congratulações", r"felicitações pelo sucesso", r"obrigada pela ajuda", r"agradecimento",
        r"mensagem carinhosa", r"saudações cordiais"
    ],

    "Spam/Propaganda": [
        r"promoção", r"desconto", r"oferta", r"ganhe dinheiro", r"publicidade", r"marketing",
        r"propaganda", r"compre agora", r"cupom", r"brinde", r"clique aqui", r"venda",
        r"promo", r"grátis", r"urgente", r"imperdível", r"exclusivo", r"aproveite",
        r"comprar online", r"novidade", r"ganhe já", r"oferta limitada", r"promoção especial",
        r"super desconto", r"receba grátis", r"cupom de desconto", r"promoção relâmpago",
        r"oferta exclusiva"
    ],

    "Outro": [
        r"informação", r"update", r"nota", r"comunicado", r"aviso", r"alerta",
        r"newsletter", r"mensagem", r"email geral", r"relatório", r"documentação",
        r"comunicado oficial", r"informativo", r"informação adicional", r"documento interno",
        r"atualização geral", r"mensagem importante", r"comunicado importante", r"informações gerais",
        r"anúncio", r"boletim", r"recado"
    ],

    "Recebimento de Currículo": [
        r"envio de currículo", r"segue meu currículo", r"currículo em anexo", r"anexo currículo",
        r"cv em anexo", r"anexo cv", r"currículo vitae", r"currículo profissional", r"currículo atualizado",
        r"candidatura", r"me candidatei", r"envio candidatura", r"inscrição vaga", r"aplicação para vaga",
        r"interesse na vaga", r"interessado na vaga", r"candidato", r"perfil profissional", r"experiência profissional",
        r"oportunidade de trabalho", r"vaga de emprego", r"vaga aberta", r"inscrição aberta", r"procuro emprego",
        r"busca de oportunidade", r"trabalhar na empresa", r"envio para seleção", r"processo seletivo", r"seleção aberta",
        r"meu cv", r"curriculo anexado", r"curriculo enviado", r"me inscrevi", r"quero me candidatar",
        r"envio meu perfil", r"perfil anexado", r"currículo para avaliação", r"currículo para vaga", r"candidatura em anexo",
        r"apresento meu currículo", r"anexo meu currículo para análise", r"encaminho currículo", r"me coloco à disposição",
        r"disponível para entrevista", r"anexo documento profissional", r"anexo histórico profissional"
    ]

}

CATEGORIAS_REGEX = {
    categoria: [re.compile(p, re.IGNORECASE) for p in patterns]
    for categoria, patterns in categorias.items()
}

respostas = {
   "Solicitação de Status": "Recebemos a sua solicitação, seu pedido está em andamento. Em breve você receberá uma atualização detalhada sobre o status.",
    "Envio de Documento": "Recebemos seu documento com sucesso. Agradecemos pelo envio.",
    "Pedido de Suporte": "Nosso time de suporte foi acionado e entrará em contato em breve para ajudá-lo da melhor forma possível.",
    "Alerta de Segurança": "Detectamos uma possível ameaça. Sua mensagem foi encaminhada ao time de segurança para investigação imediata.",
    "Reclamação": "Lamentamos pela experiência negativa. Sua reclamação foi registrada e será analisada com prioridade.",
    "Mensagem Social": "Agradecemos sua mensagem e ficamos felizes com seu contato!",
    "Recebimento de Currículo": "Recebemos seu currículo com sucesso. Agradecemos pelo interesse em nossa empresa.",
    "Spam/Propaganda": "Mensagem recebida, mas não requer ação no momento.",
    "Outro": "Mensagem recebida com sucesso. Nossa equipe analisará, caso seja necessário."
}

# --- Classificação manual ---
def classify_email_manual(text: str) -> Tuple[str, str, str]:
    text_lower = text.lower()
    for categoria, patterns in CATEGORIAS_REGEX.items():
        for pattern in patterns:
            if pattern.search(text_lower):
                grupo = "Improdutivo" if categoria in ["Mensagem Social","Recebimento de Currículo","Spam/Propaganda","Outro"] else "Produtivo"
                return grupo, categoria, respostas[categoria]
    return "Improdutivo", "Outro", respostas["Outro"]

# --- Classificação via IA ---
def classify_email_ai(text: str) -> Tuple[str, str, str]:
    candidate_labels = list(categorias.keys())
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{CLASSIFICATION_MODEL}",
            headers=headers,
            json={"inputs": text, "parameters": {"candidate_labels": candidate_labels}}
        )
        result = response.json()
        if "labels" in result:
            categoria = result["labels"][0]
        elif isinstance(result, list) and len(result) > 0 and "label" in result[0]:
            categoria = result[0]["label"]
        else:
            return classify_email_manual(text)
    except Exception as e:
        print("Erro na classificação IA:", e)
        return classify_email_manual(text)

    grupo = "Improdutivo" if categoria in ["Mensagem Social","Spam/Propaganda","Outro"] else "Produtivo"
    resposta = f"Resposta sugerida para categoria '{categoria}'"
    return grupo, categoria, resposta
