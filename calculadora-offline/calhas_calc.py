# -*- coding: utf-8 -*-
"""
Motor de calculo - Calculadora de Calhas e Condutores Pluviais
================================================================
Executado no navegador via Brython (Python 3 em JavaScript, embutido no HTML)
e tambem em CPython (para testes):  python3 calhas_calc.py

Base normativa principal:
  ABNT NBR 10844:1989 - Instalacoes prediais de aguas pluviais
    - 5.1  Intensidade pluviometrica, duracao t = 5 min, periodo de retorno T
    - 5.2  Area de contribuicao (superficie inclinada: A = (a + h/2) * b)
    - 5.3  Vazao de projeto Q = I * A / 60  (L/min; I em mm/h; A em m2)
    - 5.5  Calhas: Manning-Strickler Q = K * (S/n) * Rh^(2/3) * i^(1/2), K = 60 000
           declividade minima 0,5 %; coeficientes de rugosidade (n);
           coeficientes multiplicativos da vazao para curvas proximas a saida
    - 5.6  Condutores verticais: diametro interno minimo 70 mm
    - Tabela 5: Chuvas intensas no Brasil (Pfafstetter, 1957), t = 5 min
  ABNT NBR 5688 - Tubos e conexoes de PVC-U para sistemas prediais de agua
    pluvial, esgoto sanitario e ventilacao (diametros comerciais).
"""

try:  # ---- Brython (navegador) ----
    from browser import window
    _M = window.Math
    PI = float(_M.PI)

    def _f(fn):
        return lambda *a: float(fn(*a))
    sin, cos, tan, asin, acos, atan, atan2 = (
        _f(_M.sin), _f(_M.cos), _f(_M.tan), _f(_M.asin), _f(_M.acos),
        _f(_M.atan), _f(_M.atan2))
    BRYTHON = True
except ImportError:  # ---- CPython (testes) ----
    import math as _m
    PI = _m.pi
    sin, cos, tan, asin, acos, atan, atan2 = (
        _m.sin, _m.cos, _m.tan, _m.asin, _m.acos, _m.atan, _m.atan2)
    BRYTHON = False

G = 9.81
VERSAO = "1.0"

# ---------------------------------------------------------------------------
# 1) DADOS PLUVIOMETRICOS - NBR 10844:1989, Tabela 5 (t = 5 min)
#    (UF, local, lat, lon, I[T=1], I[T=5], I[T=25], anos de observacao)
#    I em mm/h. None = valor nao disponivel para T=25 na tabela.
#    Coordenadas aproximadas dos postos (para busca do posto mais proximo).
# ---------------------------------------------------------------------------
ESTACOES = [
    ("AC", "Rio Branco", -9.97, -67.81, 126, 139, None, 2),
    ("AC", "Sena Madureira", -9.07, -68.66, 120, 160, 170, 7),
    ("AL", "Maceió", -9.67, -35.74, 102, 122, 174, 17),
    ("AM", "Juaretê", 0.61, -69.20, 192, 240, 288, 6),
    ("AM", "Manaus", -3.12, -60.02, 138, 180, 198, 7),
    ("AM", "Parintins", -2.63, -56.74, 130, 200, None, 4),
    ("AM", "Uaupés", -0.13, -67.09, 144, 204, 230, 7),
    ("BA", "Salvador", -12.97, -38.50, 108, 122, 145, 24),
    ("CE", "Fortaleza", -3.73, -38.53, 120, 156, 180, 21),
    ("CE", "Guaramiranga", -4.26, -38.93, 114, 126, None, 7),
    ("CE", "Quixeramobim", -5.20, -39.29, 115, 121, 126, 14),
    ("ES", "Vitória", -20.32, -40.34, 102, 156, 210, 13),
    ("GO", "Catalão", -18.17, -47.95, 132, 174, None, 3),
    ("GO", "Formosa", -15.54, -47.33, 136, 176, 217, 20),
    ("GO", "Goiânia", -16.68, -49.25, 120, 178, 192, 17),
    ("MA", "Barra do Corda", -5.50, -45.25, 120, 128, 152, 20),
    ("MA", "São Luís", -2.53, -44.30, 120, 126, 152, 18),
    ("MA", "Turiaçu", -1.66, -45.37, 126, 162, 230, 7),
    ("MG", "Barbacena", -21.23, -43.77, 156, 222, 265, 13),
    ("MG", "Belo Horizonte", -19.92, -43.94, 132, 227, 230, 12),
    ("MG", "Bom Sucesso", -21.03, -44.76, 143, 196, None, 8),
    ("MG", "Caxambu", -21.98, -44.93, 106, 137, None, 8),
    ("MG", "Ouro Preto", -20.39, -43.50, 120, 211, None, 3),
    ("MG", "Passa Quatro", -22.39, -44.97, 118, 180, 192, 8),
    ("MG", "Sete Lagoas", -19.47, -44.25, 122, 182, 281, 21),
    ("MG", "Teófilo Otoni", -17.86, -41.51, 108, 121, 154, 6),
    ("MS", "Corumbá", -19.01, -57.65, 120, 131, 161, 9),
    ("MT", "Cuiabá", -15.60, -56.10, 144, 190, 230, 12),
    ("PA", "Alto Tapajós", -6.20, -57.80, 168, 229, 267, 21),
    ("PA", "Belém", -1.46, -48.50, 138, 157, 185, 20),
    ("PA", "Soure", -0.72, -48.52, 149, 162, 212, 18),
    ("PA", "Taperinha", -2.53, -54.30, 149, 202, 241, 21),
    ("PB", "João Pessoa", -7.12, -34.86, 115, 140, 163, 8),
    ("PB", "São Gonçalo", -6.84, -38.31, 120, 124, 152, 15),
    ("PE", "Nazaré da Mata", -7.74, -35.23, 118, 134, 155, 13),
    ("PE", "Olinda", -8.01, -34.86, 115, 167, 173, 16),
    ("PE", "Fernando de Noronha", -3.85, -32.42, 110, 120, 140, 25),
    ("PI", "Teresina", -5.09, -42.80, 154, 240, 262, 23),
    ("PR", "Curitiba", -25.43, -49.27, 132, 204, 228, 40),
    ("PR", "Jacarezinho", -23.16, -49.97, 115, 122, 146, 11),
    ("PR", "Paranaguá", -25.52, -48.51, 127, 186, 191, 18),
    ("PR", "Ponta Grossa", -25.09, -50.16, 120, 126, 148, 22),
    ("RJ", "Alto Itatiaia", -22.38, -44.68, 124, 164, 240, 13),
    ("RJ", "Alto Teresópolis", -22.42, -42.98, 114, 137, None, 6),
    ("RJ", "Cabo Frio", -22.88, -42.02, 113, 146, None, 10),
    ("RJ", "Campos dos Goytacazes", -21.75, -41.32, 132, 206, 240, 9),
    ("RJ", "Km 47 - Rodovia Presidente Dutra", -22.75, -43.70, 122, 164, 174, 12),
    ("RJ", "Niterói", -22.88, -43.10, 130, 183, 250, 8),
    ("RJ", "Nova Friburgo", -22.28, -42.53, 120, 124, 156, 15),
    ("RJ", "Petrópolis", -22.51, -43.18, 120, 126, 156, 23),
    ("RJ", "Pinheiral", -22.51, -44.00, 142, 214, 244, 11),
    ("RJ", "Resende", -22.47, -44.45, 130, 203, 264, 11),
    ("RJ", "Rio de Janeiro (Bangu)", -22.88, -43.47, 122, 156, 174, 20),
    ("RJ", "Rio de Janeiro (Ipanema)", -22.98, -43.20, 119, 125, 160, 15),
    ("RJ", "Rio de Janeiro (Jacarepaguá)", -22.96, -43.36, 120, 142, 152, 19),
    ("RJ", "Rio de Janeiro (Jardim Botânico)", -22.97, -43.22, 122, 167, 227, 36),
    ("RJ", "Rio de Janeiro (Praça XV)", -22.90, -43.17, 120, 174, 204, 34),
    ("RJ", "Rio de Janeiro (Praça Saenz Peña)", -22.92, -43.23, 125, 139, 167, 15),
    ("RJ", "Rio de Janeiro (Santa Cruz)", -22.92, -43.68, 121, 132, 172, 8),
    ("RJ", "Santa Maria Madalena", -21.96, -42.01, 121, 126, 152, 7),
    ("RJ", "Teresópolis", -22.41, -42.97, 115, 149, 176, 6),
    ("RJ", "Vassouras", -22.40, -43.66, 125, 179, 222, 11),
    ("RJ", "Volta Redonda", -22.52, -44.10, 156, 216, 265, 13),
    ("RN", "Natal", -5.79, -35.21, 113, 120, 143, 19),
    ("RO", "Porto Velho", -8.76, -63.90, 130, 167, 184, 10),
    ("RS", "Alegrete", -29.78, -55.79, 174, 238, 313, 35),
    ("RS", "Bagé", -31.33, -54.10, 126, 204, 234, 30),
    ("RS", "Caxias do Sul", -29.17, -51.18, 120, 127, 218, 7),
    ("RS", "Cruz Alta", -28.64, -53.61, 204, 246, 347, 17),
    ("RS", "Encruzilhada do Sul", -30.54, -52.52, 106, 126, 158, 19),
    ("RS", "Iraí", -27.19, -53.25, 120, 198, 228, 18),
    ("RS", "Passo Fundo", -28.26, -52.41, 110, 125, 180, 19),
    ("RS", "Porto Alegre", -30.03, -51.23, 118, 146, 167, 38),
    ("RS", "Rio Grande", -32.04, -52.10, 121, 204, 222, 23),
    ("RS", "Santa Maria", -29.69, -53.81, 114, 122, 145, 13),
    ("RS", "Santa Vitória do Palmar", -33.52, -53.37, 120, 126, 152, 18),
    ("RS", "São Luiz Gonzaga", -28.41, -54.96, 158, 209, 253, 17),
    ("RS", "Uruguaiana", -29.75, -57.09, 120, 142, 161, 24),
    ("RS", "Viamão", -30.08, -51.02, 114, 126, 152, 15),
    ("SC", "Blumenau", -26.92, -49.07, 120, 125, 152, 15),
    ("SC", "Florianópolis", -27.60, -48.55, 114, 120, 144, 13),
    ("SC", "São Francisco do Sul", -26.24, -48.64, 118, 132, 167, 18),
    ("SE", "Aracaju", -10.91, -37.07, 116, 122, 126, 16),
    ("SP", "Avaré", -23.10, -48.93, 115, 144, 170, 13),
    ("SP", "Bauru", -22.32, -49.06, 110, 120, 148, 9),
    ("SP", "Campos do Jordão", -22.74, -45.59, 122, 144, 164, 9),
    ("SP", "Lins", -21.68, -49.74, 96, 122, 137, 9),
    ("SP", "Piracicaba", -22.73, -47.65, 119, 122, 151, 17),
    ("SP", "Santos", -23.96, -46.33, 136, 198, 240, 31),
    ("SP", "Santos-Itapema", -23.93, -46.30, 120, 174, 204, 21),
    ("SP", "São Carlos", -22.02, -47.89, 120, 178, 161, 10),
    ("SP", "São Paulo (Congonhas)", -23.63, -46.66, 122, 132, None, 3),
    ("SP", "São Paulo (Mirante de Santana)", -23.50, -46.62, 122, 172, 191, 31),
    ("SP", "São Simão", -21.48, -47.55, 116, 148, 175, 10),
    ("SP", "Taubaté", -23.03, -45.56, 122, 172, 208, 33),
    ("SP", "Tupi", -22.72, -47.53, 122, 154, None, 30),
    ("SP", "Ubatuba", -23.43, -45.07, 122, 149, 184, 7),
]

# Cidades adicionais (sem posto proprio): (nome, lat, lon)
CIDADES_EXTRA = {
    "AC": [("Cruzeiro do Sul", -7.63, -72.67)],
    "AL": [("Arapiraca", -9.75, -36.66), ("Penedo", -10.29, -36.59)],
    "AM": [("Itacoatiara", -3.14, -58.44), ("Tefé", -3.35, -64.71),
           ("São Gabriel da Cachoeira", -0.13, -67.09)],
    "AP": [("Macapá", 0.03, -51.07), ("Santana", -0.06, -51.18),
           ("Oiapoque", 3.84, -51.83)],
    "BA": [("Feira de Santana", -12.27, -38.97), ("Vitória da Conquista", -14.86, -40.84),
           ("Ilhéus", -14.79, -39.05), ("Itabuna", -14.79, -39.28),
           ("Juazeiro", -9.41, -40.50), ("Barreiras", -12.15, -45.00),
           ("Porto Seguro", -16.45, -39.06), ("Lauro de Freitas", -12.89, -38.33),
           ("Camaçari", -12.70, -38.32), ("Teixeira de Freitas", -17.54, -39.74)],
    "CE": [("Juazeiro do Norte", -7.21, -39.32), ("Sobral", -3.69, -40.35),
           ("Caucaia", -3.74, -38.65), ("Crato", -7.23, -39.41),
           ("Maracanaú", -3.88, -38.63)],
    "DF": [("Brasília", -15.79, -47.88), ("Taguatinga", -15.83, -48.06),
           ("Ceilândia", -15.82, -48.11), ("Gama", -16.02, -48.06)],
    "ES": [("Vila Velha", -20.33, -40.29), ("Serra", -20.13, -40.31),
           ("Cariacica", -20.26, -40.42), ("Cachoeiro de Itapemirim", -20.85, -41.11),
           ("Linhares", -19.39, -40.07), ("Colatina", -19.54, -40.63),
           ("Guarapari", -20.67, -40.50)],
    "GO": [("Anápolis", -16.33, -48.95), ("Aparecida de Goiânia", -16.82, -49.24),
           ("Rio Verde", -17.80, -50.93), ("Luziânia", -16.25, -47.95),
           ("Itumbiara", -18.42, -49.22), ("Jataí", -17.88, -51.72),
           ("Valparaíso de Goiás", -16.07, -47.98)],
    "MA": [("Imperatriz", -5.53, -47.48), ("Caxias", -4.86, -43.36),
           ("Timon", -5.09, -42.84), ("Bacabal", -4.22, -44.78),
           ("Balsas", -7.53, -46.04)],
    "MG": [("Uberlândia", -18.92, -48.28), ("Juiz de Fora", -21.76, -43.35),
           ("Contagem", -19.93, -44.05), ("Betim", -19.97, -44.20),
           ("Montes Claros", -16.73, -43.86), ("Uberaba", -19.75, -47.93),
           ("Governador Valadares", -18.85, -41.95), ("Ipatinga", -19.47, -42.54),
           ("Divinópolis", -20.14, -44.89), ("Poços de Caldas", -21.79, -46.56),
           ("Varginha", -21.55, -45.43), ("Pouso Alegre", -22.23, -45.94),
           ("Lavras", -21.25, -45.00), ("Patos de Minas", -18.58, -46.52),
           ("São João del-Rei", -21.14, -44.26), ("Conselheiro Lafaiete", -20.66, -43.79)],
    "MS": [("Campo Grande", -20.47, -54.62), ("Dourados", -22.22, -54.81),
           ("Três Lagoas", -20.75, -51.68), ("Ponta Porã", -22.54, -55.73)],
    "MT": [("Várzea Grande", -15.65, -56.13), ("Rondonópolis", -16.47, -54.64),
           ("Sinop", -11.86, -55.51), ("Tangará da Serra", -14.62, -57.49),
           ("Barra do Garças", -15.89, -52.26), ("Cáceres", -16.07, -57.68)],
    "PA": [("Ananindeua", -1.37, -48.37), ("Santarém", -2.44, -54.71),
           ("Marabá", -5.37, -49.12), ("Castanhal", -1.30, -47.92),
           ("Parauapebas", -6.07, -49.90), ("Altamira", -3.20, -52.21),
           ("Itaituba", -4.28, -55.98)],
    "PB": [("Campina Grande", -7.23, -35.88), ("Patos", -7.02, -37.28),
           ("Sousa", -6.76, -38.23), ("Cajazeiras", -6.89, -38.56)],
    "PE": [("Recife", -8.05, -34.88), ("Jaboatão dos Guararapes", -8.11, -35.01),
           ("Caruaru", -8.28, -35.97), ("Petrolina", -9.39, -40.50),
           ("Garanhuns", -8.89, -36.49), ("Paulista", -7.94, -34.87)],
    "PI": [("Parnaíba", -2.90, -41.78), ("Picos", -7.08, -41.47),
           ("Floriano", -6.77, -43.02)],
    "PR": [("Londrina", -23.31, -51.16), ("Maringá", -23.42, -51.94),
           ("Cascavel", -24.96, -53.46), ("Foz do Iguaçu", -25.55, -54.59),
           ("São José dos Pinhais", -25.53, -49.21), ("Guarapuava", -25.39, -51.46),
           ("Toledo", -24.72, -53.74), ("Umuarama", -23.77, -53.32),
           ("Apucarana", -23.55, -51.46), ("Pato Branco", -26.23, -52.67)],
    "RJ": [("Rio de Janeiro (Centro)", -22.90, -43.18), ("Duque de Caxias", -22.79, -43.31),
           ("Nova Iguaçu", -22.76, -43.45), ("São Gonçalo", -22.83, -43.06),
           ("Macaé", -22.37, -41.79), ("Angra dos Reis", -23.01, -44.32),
           ("Barra Mansa", -22.54, -44.17), ("Itaperuna", -21.21, -41.89)],
    "RN": [("Mossoró", -5.19, -37.34), ("Parnamirim", -5.92, -35.26),
           ("Caicó", -6.46, -37.10)],
    "RO": [("Ji-Paraná", -10.88, -61.95), ("Ariquemes", -9.91, -63.04),
           ("Vilhena", -12.74, -60.15), ("Cacoal", -11.44, -61.45)],
    "RR": [("Boa Vista", 2.82, -60.67), ("Rorainópolis", 0.94, -60.42)],
    "RS": [("Pelotas", -31.77, -52.34), ("Canoas", -29.92, -51.18),
           ("Novo Hamburgo", -29.68, -51.13), ("São Leopoldo", -29.76, -51.15),
           ("Gravataí", -29.94, -50.99), ("Santa Cruz do Sul", -29.72, -52.43),
           ("Lajeado", -29.47, -51.96), ("Erechim", -27.63, -52.27),
           ("Ijuí", -28.39, -53.91), ("Santo Ângelo", -28.30, -54.26),
           ("Bento Gonçalves", -29.17, -51.52), ("Gramado", -29.38, -50.87)],
    "SC": [("Joinville", -26.30, -48.85), ("Chapecó", -27.10, -52.62),
           ("Itajaí", -26.91, -48.66), ("Criciúma", -28.68, -49.37),
           ("Lages", -27.82, -50.33), ("Balneário Camboriú", -26.99, -48.63),
           ("São José", -27.61, -48.63), ("Tubarão", -28.47, -49.01),
           ("Jaraguá do Sul", -26.49, -49.07), ("Brusque", -27.10, -48.92)],
    "SE": [("Nossa Senhora do Socorro", -10.86, -37.13), ("Lagarto", -10.92, -37.65),
           ("Itabaiana", -10.68, -37.43)],
    "SP": [("São Paulo (Centro)", -23.55, -46.63), ("Campinas", -22.91, -47.06),
           ("Guarulhos", -23.45, -46.53), ("São Bernardo do Campo", -23.69, -46.56),
           ("Santo André", -23.66, -46.53), ("Osasco", -23.53, -46.79),
           ("Ribeirão Preto", -21.18, -47.81), ("Sorocaba", -23.50, -47.46),
           ("São José dos Campos", -23.18, -45.89), ("São José do Rio Preto", -20.82, -49.38),
           ("Jundiaí", -23.19, -46.88), ("Presidente Prudente", -22.12, -51.39),
           ("Marília", -22.21, -49.95), ("Araraquara", -21.79, -48.18),
           ("Franca", -20.54, -47.40), ("Limeira", -22.56, -47.40),
           ("Guarujá", -23.99, -46.26), ("Praia Grande", -24.01, -46.40),
           ("Araçatuba", -21.21, -50.43), ("Botucatu", -22.89, -48.44),
           ("Registro", -24.49, -47.84), ("Mogi das Cruzes", -23.52, -46.19)],
    "TO": [("Palmas", -10.18, -48.33), ("Araguaína", -7.19, -48.21),
           ("Gurupi", -11.73, -49.07), ("Porto Nacional", -10.71, -48.42)],
}

UF_NOMES = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul", "RO": "Rondônia",
    "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe",
    "TO": "Tocantins",
}

# ---------------------------------------------------------------------------
# 2) MATERIAIS - coeficiente de rugosidade n (NBR 10844:1989)
# ---------------------------------------------------------------------------
MATERIAIS = {
    "galvanizada": {"nome": "Chapa de aço galvanizado", "n": 0.011, "chapa": True,
                    "dens": 7.85},
    "aluminio": {"nome": "Chapa de alumínio", "n": 0.011, "chapa": True, "dens": 2.70},
    "cobre": {"nome": "Chapa de cobre", "n": 0.011, "chapa": True, "dens": 8.93},
    "inox": {"nome": "Chapa de aço inoxidável", "n": 0.011, "chapa": True, "dens": 7.93},
    "pvc": {"nome": "PVC (calha pré-fabricada)", "n": 0.011, "chapa": False},
    "fibrocimento": {"nome": "Fibrocimento", "n": 0.011, "chapa": False},
    "concreto_alisado": {"nome": "Concreto alisado", "n": 0.012, "chapa": False},
    "alvenaria_revestida": {"nome": "Alvenaria revestida", "n": 0.012, "chapa": False},
    "concreto": {"nome": "Concreto não alisado", "n": 0.013, "chapa": False},
    "ceramica": {"nome": "Cerâmica", "n": 0.013, "chapa": False},
    "alvenaria": {"nome": "Alvenaria de tijolos não revestida", "n": 0.015,
                  "chapa": False},
}

FORMAS = {
    "beiral": "Calha de beiral (recebe 1 água)",
    "central": "Calha central / água-furtada (recebe 2 águas)",
    "retangular": "Calha retangular (platibanda)",
    "meiacana": "Calha meia-cana (semicircular)",
}

# Coeficientes multiplicativos da vazao de projeto (NBR 10844, curvas na calha)
COEF_CURVA = {
    "nenhuma": (1.00, "Sem curvas a menos de 4 m da saída"),
    "reto_2": (1.20, "Curva em canto reto a menos de 2 m da saída"),
    "arred_2": (1.10, "Curva em canto arredondado a menos de 2 m da saída"),
    "reto_4": (1.10, "Curva em canto reto entre 2 m e 4 m da saída"),
    "arred_4": (1.05, "Curva em canto arredondado entre 2 m e 4 m da saída"),
}

# Tubos PVC-U para agua pluvial/esgoto (NBR 5688) - DN, DE, DI de calculo (mm)
# DI de calculo conservador (parede da serie reforcada); confira o catalogo.
TUBOS_PVC = [
    (75, 75.0, 71.0),
    (100, 100.0, 96.0),
    (150, 150.0, 145.0),
    (200, 200.0, 193.0),
]

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def _r(x, nd=2):
    if x is None:
        return None
    return round(float(x), nd)


def ceil_to(x, step):
    k = int(x / step)
    if k * step < x - 1e-9:
        k += 1
    return k * step


def floor_to(x, step):
    return int(x / step + 1e-9) * step


def ceil_int(x):
    k = int(x)
    return k + 1 if k < x - 1e-9 else k


def haversine_km(lat1, lon1, lat2, lon2):
    rad = PI / 180.0
    dlat = (lat2 - lat1) * rad
    dlon = (lon2 - lon1) * rad
    a = sin(dlat / 2) ** 2 + cos(lat1 * rad) * cos(lat2 * rad) * sin(dlon / 2) ** 2
    return 2 * 6371.0 * asin(min(1.0, a ** 0.5))


def to_json(o):
    """Serializador JSON minimo (dispensa a stdlib no Brython)."""
    if o is None:
        return "null"
    if o is True:
        return "true"
    if o is False:
        return "false"
    if isinstance(o, (int, float)):
        if o != o or o in (float("inf"), float("-inf")):
            return "null"
        return repr(o) if isinstance(o, float) else str(o)
    if isinstance(o, str):
        s = o.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return '"' + s + '"'
    if isinstance(o, dict):
        return "{" + ",".join(to_json(str(k)) + ":" + to_json(v)
                              for k, v in o.items()) + "}"
    if isinstance(o, (list, tuple)):
        return "[" + ",".join(to_json(v) for v in o) + "]"
    return to_json(str(o))


# ---------------------------------------------------------------------------
# 3) LOCALIDADES E CHUVA
# ---------------------------------------------------------------------------
def listar_ufs():
    return [{"uf": uf, "nome": UF_NOMES[uf]} for uf in sorted(UF_NOMES)]


def _cidades(uf):
    out = {}
    for e in ESTACOES:
        if e[0] == uf:
            out[e[1]] = (e[2], e[3], True)
    for nome, la, lo in CIDADES_EXTRA.get(uf, []):
        if nome not in out:
            out[nome] = (la, lo, False)
    return out


def listar_cidades(uf):
    c = _cidades(uf)
    return [{"nome": k, "posto": c[k][2]} for k in sorted(c)]


def _intensidade(est, T):
    I1, I5, I25 = est[4], est[5], est[6]
    if T == 1:
        return float(I1), False
    if T == 5:
        return float(I5), False
    if I25 is not None:
        return float(I25), False
    # Sem valor tabelado para T=25: extrapolacao log-linear em ln(T)
    # I25 = I5 + (I5 - I1) * ln(25/5)/ln(5/1) = I5 + (I5 - I1)
    return float(I5 + (I5 - I1)), True


def dados_chuva(uf, cidade, T, lat=None, lon=None, I_manual=None):
    T = int(T)
    avisos = []
    if lat is None or lon is None:
        c = _cidades(uf).get(cidade)
        if c is None:
            raise ValueError("Cidade não encontrada: " + str(cidade))
        lat, lon = c[0], c[1]
    dist = []
    for e in ESTACOES:
        d = 0.0 if (e[0] == uf and e[1] == cidade) else haversine_km(lat, lon, e[2], e[3])
        dist.append((d, e))
    dist.sort(key=lambda t: t[0])
    d0, est = dist[0]
    I, estimado = _intensidade(est, T)
    if estimado:
        avisos.append("Posto sem valor tabelado para T = 25 anos: intensidade "
                      "extrapolada (log-linear em T a partir de T=1 e T=5).")
    if T == 25 and est[6] is not None and est[6] < est[5]:
        avisos.append("No posto %s a intensidade tabelada para T=25 (%d mm/h) é menor que "
                      "para T=5 (%d mm/h); avalie adotar o maior valor." % (est[1], est[6], est[5]))
    if d0 > 150:
        avisos.append("Posto pluviográfico mais próximo a %.0f km. Recomenda-se usar "
                      "equação IDF local (órgão estadual/municipal) e informar a "
                      "intensidade manualmente." % d0)
    elif d0 > 50:
        avisos.append("Posto pluviográfico de referência a %.0f km da cidade." % d0)
    fonte = "NBR 10844:1989 - Tabela 5 (posto mais próximo)"
    I_tab = I
    if I_manual is not None and I_manual > 0:
        I = float(I_manual)
        fonte = "Intensidade informada pelo usuário (manual)"
        avisos = [a for a in avisos if "T = 25" not in a]
    vizinhos = []
    for d, e in dist[:3]:
        vizinhos.append({"uf": e[0], "posto": e[1], "dist_km": _r(d, 1),
                         "I1": e[4], "I5": e[5], "I25": e[6], "anos": e[7]})
    return {
        "uf": uf, "uf_nome": UF_NOMES.get(uf, uf), "cidade": cidade,
        "lat": _r(lat, 4), "lon": _r(lon, 4),
        "posto": est[1], "posto_uf": est[0], "dist_km": _r(d0, 1),
        "anos_obs": est[7],
        "I1": est[4], "I5": est[5], "I25": est[6],
        "T": T, "duracao_min": 5, "I_tabela": _r(I_tab, 1), "I": _r(I, 1),
        "I_estimado": estimado and not (I_manual and I_manual > 0),
        "i_Ls_m2": _r(I / 3600.0, 5),           # L/s por m2
        "i_Lmin_m2": _r(I / 60.0, 4),           # L/min por m2
        "altura_5min_mm": _r(I * 5 / 60.0, 2),  # lamina precipitada em 5 min
        "fonte": fonte, "avisos": avisos, "vizinhos": vizinhos,
    }


# ---------------------------------------------------------------------------
# 4) AREA DE CONTRIBUICAO E VAZAO (NBR 10844, 5.2 e 5.3)
# ---------------------------------------------------------------------------
def area_contribuicao(n_aguas, a1, a2, b, inc_pct, parede_m2=0.0):
    """a = projecao horizontal da agua perpendicular a calha (m);
    b = comprimento da calha (m); inclinacao em %.  A = (a + h/2) * b."""
    aguas = []
    larguras = [a1] if n_aguas == 1 else [a1, a2]
    for a in larguras:
        h = a * inc_pct / 100.0
        A = (a + h / 2.0) * b
        aguas.append({"a": _r(a, 3), "h": _r(h, 3), "b": _r(b, 3),
                      "A_proj": _r(a * b, 3), "A": _r(A, 3),
                      "comp_inclinado": _r((a * a + h * h) ** 0.5, 3)})
    A_tot = sum(x["A"] for x in aguas)
    A_par = 0.5 * parede_m2   # superficie vertical unica: A = (a*b)/2
    return {"aguas": aguas, "A_telhado": _r(A_tot, 3), "A_parede": _r(A_par, 3),
            "A_total": _r(A_tot + A_par, 3),
            "ang_telhado_graus": _r(atan(inc_pct / 100.0) * 180 / PI, 2)}


def vazao_projeto(I, A):
    return I * A / 60.0  # L/min


# ---------------------------------------------------------------------------
# 5) HIDRAULICA DA CALHA - Manning-Strickler (NBR 10844, 5.5)
# ---------------------------------------------------------------------------
def manning(A_m2, P_m, S, n):
    if A_m2 <= 0 or P_m <= 0:
        return 0.0
    Rh = A_m2 / P_m
    return 60000.0 * (A_m2 / n) * Rh ** (2.0 / 3.0) * S ** 0.5  # L/min


def secao_ret(b_mm, y_mm):
    b, y = b_mm / 1000.0, y_mm / 1000.0
    return b * y, b + 2 * y, b


def secao_semi(D_mm, y_mm):
    R = D_mm / 2000.0
    y = min(y_mm / 1000.0, R)
    if y <= 0:
        return 0.0, 0.0, 0.0
    th = 2 * acos(max(-1.0, min(1.0, 1 - y / R)))  # angulo central molhado
    A = R * R / 2.0 * (th - sin(th))
    P = R * th
    B = 2 * R * sin(th / 2)
    return A, P, B


def q_secao(forma, dims, y, S, n):
    if forma == "meiacana":
        A, P, B = secao_semi(dims["D"], y)
    else:
        A, P, B = secao_ret(dims["b"], y)
    return manning(A, P, S, n), A, P, B


def lamina(forma, dims, Q, S, n, y_max):
    """Altura da lamina d'agua (mm) para a vazao Q (bissecao)."""
    lo, hi = 0.0, y_max
    if q_secao(forma, dims, hi, S, n)[0] < Q:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if q_secao(forma, dims, mid, S, n)[0] < Q:
            lo = mid
        else:
            hi = mid
    return hi


# ---------------------------------------------------------------------------
# 6) DIMENSIONAMENTO DA CALHA (com aproveitamento de chapa)
# ---------------------------------------------------------------------------
ABA_MIN = 60.0               # aba de fixacao minima ao otimizar o corte (mm)
RELACAO_LAMINA = 2.0 / 3.0   # lamina maxima admitida = 2/3 da altura (retangular)


def _partes_fixas(forma, aba, bainha, sobre):
    if forma == "beiral":
        return [("Bainha (contrafluxo)", bainha), ("Aba de fixação", aba),
                ("Sobrealtura traseira", sobre), ("Bainha frontal", bainha)]
    if forma == "central":
        return [("Bainha esq.", bainha), ("Aba esq.", aba),
                ("Aba dir.", aba), ("Bainha dir.", bainha)]
    return [("Bainha esq.", bainha), ("Bainha dir.", bainha)]


def dimensionar_calha(forma, mat_key, Qc, S, aba=100.0, bainha=15.0, sobre=20.0,
                      largura_chapa=1200.0, otimizar_chapa=True,
                      b_min=100.0, h_min=75.0, acresc_max=30.0):
    mat = MATERIAIS[mat_key]
    n = mat["n"]
    chapa = mat["chapa"] and otimizar_chapa
    avisos = []
    fixas = _partes_fixas(forma, aba, bainha, sobre)
    if not mat["chapa"]:
        fixas = []           # PVC/concreto/alvenaria: sem dobras de chapa
    soma_fixas = sum(v for _, v in fixas)

    if forma == "meiacana":
        D = 75.0
        while q_secao("meiacana", {"D": D}, D / 2, S, n)[0] < Qc and D < 1500:
            D += 5.0
        D_hid = D
        dev_min = PI * D / 2 + soma_fixas
        dims = {"D": D}
    else:
        b = b_min
        while True:
            y = b / 2.0                       # secao retangular de maxima eficiencia
            if manning(*secao_ret(b, y)[:2], S=S, n=n) >= Qc or b > 3000:
                break
            b += 5.0
        H = max(h_min, ceil_to(y / RELACAO_LAMINA, 5.0))
        b_hid, H_hid = b, H
        dev_min = b + 2 * H + soma_fixas
        dims = {"b": b, "H": H}

    # ---- Aproveitamento da chapa (tiras = largura_chapa / k) ----
    tiras, dev = 0, None
    if mat["chapa"]:
        dev = ceil_to(dev_min, 5.0)
        if chapa:
            # Tenta fechar na tira imediatamente inferior (1200/k) reduzindo as abas
            # de fixacao (minimo ABA_MIN), poupando material.
            w_inf = None
            for k in range(1, 13):
                w = largura_chapa / k
                if w < dev_min - 1e-6:
                    w_inf = w
                    break
            idx_aba = [i for i, (nm, _) in enumerate(fixas) if nm.startswith("Aba")]
            redutivel = sum(max(0.0, fixas[i][1] - ABA_MIN) for i in idx_aba)
            if w_inf and idx_aba and dev_min - w_inf <= redutivel + 1e-6:
                deficit = dev_min - w_inf
                corte = deficit / len(idx_aba)
                aba_nova = fixas[idx_aba[0]][1] - corte
                fixas = [(nm, (v - corte) if nm.startswith("Aba") else v) for nm, v in fixas]
                soma_fixas = sum(v for _, v in fixas)
                dev_min = w_inf
                avisos.append("Aba(s) de fixação reduzida(s) para %.0f mm para que a tira "
                              "feche em %.0f mm (corte sem sobra na chapa de %.0f mm)."
                              % (aba_nova, w_inf, largura_chapa))
            for k in range(12, 0, -1):
                w = largura_chapa / k
                if w + 1e-6 >= dev_min:
                    tiras, dev = k, w
                    break
            if tiras and dev > dev_min * (1 + acresc_max / 100.0) + 1e-6:
                w_ok = ceil_to(dev_min, 5.0)
                k2 = int((largura_chapa + 1e-6) // w_ok)
                avisos.append("Corte sem sobra exigiria tira de %.0f mm (acréscimo de "
                              "%.0f%% sobre o mínimo de %.0f mm, acima do limite de "
                              "%.0f%%). Adotada tira de %.0f mm: %d tira(s) por chapa, "
                              "sobra de %.0f mm por chapa (aproveitar em cabeceiras, "
                              "rufos ou bocais)." % (dev, 100 * (dev / dev_min - 1),
                                                     dev_min, acresc_max, w_ok, k2,
                                                     largura_chapa - k2 * w_ok))
                tiras, dev = k2, w_ok
            if tiras == 0:
                avisos.append("O desenvolvimento mínimo (%.0f mm) excede a largura da "
                              "chapa (%.0f mm): usar bobina/chapa mais larga ou emenda "
                              "longitudinal." % (dev_min, largura_chapa))
                dev = ceil_to(dev_min, 5.0)
        else:
            tiras = int((largura_chapa + 1e-6) // dev) if dev <= largura_chapa else 0
        var = dev - soma_fixas
        if forma == "meiacana":
            D = var * 2.0 / PI
            D = floor_to(D, 0.5)
            dims = {"D": D}
            folga = dev - (PI * D / 2 + soma_fixas)
            if folga > 0.01:          # sobra (<1 mm) incorporada as bainhas
                fixas = [(nm, v + folga / 2 if "Bainha" in nm else v) for nm, v in fixas]
        else:
            s = var / (dims["b"] + 2 * dims["H"])
            H = max(dims["H"], floor_to(dims["H"] * s, 5.0))
            b = var - 2 * H
            if b < dims["b"]:
                H = dims["H"]
                b = var - 2 * H
            dims = {"b": b, "H": H}
    else:
        if forma == "meiacana":
            dims = {"D": ceil_to(dims["D"], 5.0)}
        else:
            step = 5.0 if mat_key in ("pvc", "fibrocimento") else 10.0
            dims = {"b": ceil_to(dims["b"], step), "H": ceil_to(dims["H"], step)}

    # ---- Verificacao hidraulica final ----
    if forma == "meiacana":
        y_max = dims["D"] / 2.0
        H_tot = y_max
    else:
        y_max = RELACAO_LAMINA * dims["H"]
        H_tot = dims["H"]
    Q_adm = q_secao(forma, dims, y_max, S, n)[0]
    y_l = lamina(forma, dims, Qc, S, n, y_max)
    if y_l is None:
        avisos.append("A seção não comporta a vazão de projeto com a lâmina máxima "
                      "admitida.")
        y_l = y_max
    Qy, A, P, B = q_secao(forma, dims, y_l, S, n)
    V = (Qc / 60000.0) / A if A > 0 else 0
    Fr = V / (G * (A / B)) ** 0.5 if B > 0 and A > 0 else 0

    res = {
        "forma": forma, "forma_nome": FORMAS[forma], "material": mat["nome"],
        "n": n, "S": S, "Qc": _r(Qc, 1),
        "lamina_mm": _r(y_l, 1), "lamina_max_mm": _r(y_max, 1),
        "borda_livre_mm": _r(H_tot - y_l, 1),
        "ocupacao_pct": _r(100 * y_l / H_tot, 1),
        "Q_admissivel": _r(Q_adm, 1), "utilizacao_pct": _r(100 * Qc / Q_adm, 1),
        "area_molhada_cm2": _r(A * 1e4, 1), "perimetro_molhado_mm": _r(P * 1000, 1),
        "raio_hidraulico_mm": _r(1000 * A / P if P else 0, 2),
        "velocidade_ms": _r(V, 3), "froude": _r(Fr, 3),
        "dev_min_mm": _r(dev_min, 1), "dev_mm": _r(dev, 1) if dev else None,
        "tiras_por_chapa": tiras, "largura_chapa": largura_chapa,
        "aproveitamento_pct": _r(100 * tiras * dev / largura_chapa, 1)
        if (tiras and dev) else None,
        "chapa": mat["chapa"], "avisos": avisos, "fixas": fixas,
    }
    if forma == "meiacana":
        res.update({"D_mm": _r(dims["D"], 1), "R_mm": _r(dims["D"] / 2, 2),
                    "D_hidraulico_mm": D_hid, "largura_mm": _r(dims["D"], 1),
                    "altura_mm": _r(dims["D"] / 2, 1)})
    else:
        res.update({"b_mm": _r(dims["b"], 1), "H_mm": _r(dims["H"], 1),
                    "b_hidraulico_mm": b_hid, "H_hidraulico_mm": H_hid,
                    "largura_mm": _r(dims["b"], 1), "altura_mm": _r(dims["H"], 1)})
        if forma == "beiral":
            res["H_traseira_mm"] = _r(dims["H"] + (sobre if mat["chapa"] else 0), 1)
    res["dims"] = dims
    return res


# ---------------------------------------------------------------------------
# 7) CONDUTORES VERTICAIS (NBR 10844, 5.6) - PVC NBR 5688
# ---------------------------------------------------------------------------
def capacidade_condutor(DI_mm, H_mm, saida="aresta"):
    """Capacidade (L/min) de um condutor vertical com saida em aresta viva.
    Entrada (bocal): menor valor entre
        vertedouro circular  Q = 0,62*(2/3)*sqrt(2g)*(pi*D)*H^1,5
        orificio             Q = 0,61*(pi*D^2/4)*sqrt(2g*H)
    Tubo de queda (escoamento anular, Wyly-Eaton, taxa de ocupacao 1/3):
        Q[L/s] = 3,142e-4 * r^(5/3) * D[mm]^(8/3)
    """
    D = DI_mm / 1000.0
    H = max(H_mm, 1.0) / 1000.0
    if saida == "funil":   # funil: entrada 1,5 x DI, bocal convergente Cd = 0,95
        Dv, cd = 1.5 * D, 0.95
    else:                  # aresta viva
        Dv, cd = D, 0.61
    q_vert = 0.62 * (2.0 / 3.0) * (2 * G) ** 0.5 * PI * Dv * H ** 1.5 * 60000
    q_orif = cd * (PI * D * D / 4) * (2 * G * H) ** 0.5 * 60000
    q_tubo = 3.142e-4 * (1.0 / 3.0) ** (5.0 / 3.0) * DI_mm ** (8.0 / 3.0) * 60
    q_ent = min(q_vert, q_orif)
    regime = "vertedouro" if q_vert <= q_orif else "orifício"
    return {"Q_entrada": q_ent, "Q_vertedouro": q_vert, "Q_orificio": q_orif,
            "Q_tubo": q_tubo, "Q_cap": min(q_ent, q_tubo), "regime": regime}


def dimensionar_condutor(Q_total, N, H_mm, saida="aresta"):
    Qn = Q_total / N
    escolhido = None
    tabela = []
    for DN, DE, DI in TUBOS_PVC:
        c = capacidade_condutor(DI, H_mm, saida)
        ok = c["Q_cap"] >= Qn and DI >= 70.0
        tabela.append({"DN": DN, "DE": DE, "DI": DI, "Q_cap": _r(c["Q_cap"], 1),
                       "Q_entrada": _r(c["Q_entrada"], 1), "Q_tubo": _r(c["Q_tubo"], 1),
                       "regime": c["regime"], "ok": ok})
        if ok and escolhido is None:
            escolhido = (DN, DE, DI, c)
    avisos = []
    sugestao = None
    if escolhido is None:
        DN, DE, DI = TUBOS_PVC[-1]
        cap = capacidade_condutor(DI, H_mm, saida)["Q_cap"]
        sugestao = ceil_int(Q_total / cap)
        avisos.append("Nenhum diâmetro comercial atende a vazão por condutor. "
                      "Aumente o número de descidas para no mínimo %d (DN %d) ou a "
                      "altura da calha." % (sugestao, DN))
        escolhido = (DN, DE, DI, capacidade_condutor(DI, H_mm, saida))
    DN, DE, DI, c = escolhido
    # numero minimo de descidas com DN 100 (referencia)
    cap100 = capacidade_condutor(96.0, H_mm, saida)["Q_cap"]
    return {"N": N, "Q_por_condutor": _r(Qn, 1), "DN": DN, "DE": DE, "DI": DI,
            "Q_cap": _r(c["Q_cap"], 1), "Q_entrada": _r(c["Q_entrada"], 1),
            "Q_tubo": _r(c["Q_tubo"], 1), "regime": c["regime"],
            "utilizacao_pct": _r(100 * Qn / c["Q_cap"], 1),
            "H_bocal_mm": _r(H_mm, 1), "N_min_DN100": ceil_int(Q_total / cap100),
            "tabela": tabela, "avisos": avisos, "sugestao_N": sugestao}


# ---------------------------------------------------------------------------
# 8) GEOMETRIA DO PERFIL (desenho em corte) - coordenadas em mm, y para cima
# ---------------------------------------------------------------------------
def _ang_interno(p_prev, p, p_next):
    ax, ay = p_prev[0] - p[0], p_prev[1] - p[1]
    bx, by = p_next[0] - p[0], p_next[1] - p[1]
    la, lb = (ax * ax + ay * ay) ** 0.5, (bx * bx + by * by) ** 0.5
    c = (ax * bx + ay * by) / (la * lb)
    ang = acos(max(-1.0, min(1.0, c))) * 180 / PI
    ux, uy = ax / la + bx / lb, ay / la + by / lb
    lu = (ux * ux + uy * uy) ** 0.5
    if lu < 1e-9:
        ux, uy, lu = -ay / la, ax / la, 1.0
    return ang, (ux / lu, uy / lu)


def geometria(calha, inc_pct):
    forma = calha["forma"]
    fx = dict((nm, v) for nm, v in calha["fixas"])
    th = atan(inc_pct / 100.0)
    segs, pts = [], []
    if forma == "meiacana":
        R = calha["D_mm"] / 2.0
        bl = fx.get("Bainha esq.", 0)
        br = fx.get("Bainha dir.", 0)
        pts = [(-bl, R), (0.0, R)]
        arco = {"cx": R, "cy": R, "r": R, "p0": (0.0, R), "p1": (2 * R, R),
                "comp": PI * R}
        pts_dir = [(2 * R, R), (2 * R + br, R)]
        segs = []
        if bl:
            segs.append({"tipo": "linha", "p0": pts[0], "p1": pts[1], "comp": bl,
                         "nome": "Bainha esq."})
        segs.append({"tipo": "arco", "comp": PI * R, "nome": "Meia-cana (calandrada)",
                     "cx": R, "cy": R, "r": R})
        if br:
            segs.append({"tipo": "linha", "p0": pts_dir[0], "p1": pts_dir[1],
                         "comp": br, "nome": "Bainha dir."})
        dobras = []
        if bl:
            dobras.append({"p": (0.0, R), "ang": 90.0, "bis": (-0.7071, -0.7071)})
        if br:
            dobras.append({"p": (2 * R, R), "ang": 90.0, "bis": (0.7071, -0.7071)})
        y = calha["lamina_mm"]
        hw = (R * R - (R - y) ** 2) ** 0.5
        agua = {"x0": R - hw, "x1": R + hw, "y": y, "tipo": "semi"}
        cent = (R, R * 0.6)
        x_tubo = R
        largura_total = 2 * R
    else:
        b, H = calha["b_mm"], calha["H_mm"]
        if forma == "beiral":
            Hb = H + fx.get("Sobrealtura traseira", 0)
            La = fx.get("Aba de fixação", 0)
            bn = fx.get("Bainha (contrafluxo)", 0)
            bf = fx.get("Bainha frontal", 0)
            T = (-La * cos(th), Hb + La * sin(th))
            pts = []
            if bn:
                pts.append((T[0], T[1] + bn))
            if La:
                pts.append(T)
            pts += [(0.0, Hb), (0.0, 0.0), (b, 0.0), (b, H)]
            if bf:
                pts.append((b + bf, H))
            nomes = ([] if not bn else ["Bainha (contrafluxo)"]) + \
                    ([] if not La else ["Aba de fixação"]) + \
                    ["Parede traseira", "Fundo", "Parede frontal"] + \
                    ([] if not bf else ["Bainha frontal"])
        elif forma == "central":
            La = fx.get("Aba esq.", 0)
            bn = fx.get("Bainha esq.", 0)
            T1 = (-La * cos(th), H + La * sin(th))
            T2 = (b + La * cos(th), H + La * sin(th))
            pts = []
            if bn:
                pts.append((T1[0], T1[1] + bn))
            if La:
                pts.append(T1)
            pts += [(0.0, H), (0.0, 0.0), (b, 0.0), (b, H)]
            if La:
                pts.append(T2)
            if bn:
                pts.append((T2[0], T2[1] + bn))
            nomes = ([] if not bn else ["Bainha esq."]) + ([] if not La else ["Aba esq."]) + \
                    ["Parede esq.", "Fundo", "Parede dir."] + \
                    ([] if not La else ["Aba dir."]) + ([] if not bn else ["Bainha dir."])
        else:
            bn = fx.get("Bainha esq.", 0)
            pts = []
            if bn:
                pts.append((-bn, H))
            pts += [(0.0, H), (0.0, 0.0), (b, 0.0), (b, H)]
            if bn:
                pts.append((b + bn, H))
            nomes = ([] if not bn else ["Bainha esq."]) + \
                    ["Parede esq.", "Fundo", "Parede dir."] + \
                    ([] if not bn else ["Bainha dir."])
        for i in range(len(pts) - 1):
            p0, p1 = pts[i], pts[i + 1]
            L = ((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2) ** 0.5
            segs.append({"tipo": "linha", "p0": p0, "p1": p1, "comp": L,
                         "nome": nomes[i]})
        dobras = []
        for i in range(1, len(pts) - 1):
            ang, bis = _ang_interno(pts[i - 1], pts[i], pts[i + 1])
            dobras.append({"p": pts[i], "ang": ang, "bis": bis})
        agua = {"x0": 0.0, "x1": b, "y": calha["lamina_mm"], "tipo": "ret"}
        cent = (b / 2.0, H / 2.0)
        x_tubo = b / 2.0
        largura_total = b

    # arredondamento para saida
    def rp(p):
        return [_r(p[0], 2), _r(p[1], 2)]
    out_segs = []
    for s in segs:
        d = dict(s)
        if s["tipo"] == "linha":
            d["p0"], d["p1"] = rp(s["p0"]), rp(s["p1"])
        d["comp"] = _r(s["comp"], 1)
        out_segs.append(d)
    out_dob = [{"p": rp(d["p"]), "ang": _r(d["ang"], 1),
                "bis": [_r(d["bis"][0], 4), _r(d["bis"][1], 4)]} for d in dobras]
    return {"segmentos": out_segs, "dobras": out_dob, "agua": agua,
            "centro": rp(cent), "x_tubo": _r(x_tubo, 2),
            "largura": _r(largura_total, 1)}


# ---------------------------------------------------------------------------
# 9) LISTA DE MATERIAIS
# ---------------------------------------------------------------------------
ESPESSURAS_GALV = [(330.0, "nº 26", 0.50), (600.0, "nº 24", 0.65),
                   (1200.0, "nº 22", 0.80), (99999.0, "nº 20", 0.95)]


def materiais(entrada, calha, cond):
    L = entrada["comprimento"]
    N = cond["N"]
    itens = []
    mk = entrada.get("material", "galvanizada")
    mat = MATERIAIS[mk]
    comp_chapa = entrada.get("comp_chapa", 3000.0)
    transp = 50.0
    if mat["chapa"]:
        dev = calha["dev_mm"]
        if mk == "galvanizada":
            for lim, num, e in ESPESSURAS_GALV:
                if dev <= lim:
                    esp_txt, esp = num + " (%.2f mm)" % e, e
                    break
        else:
            esp = 0.5 if mk in ("cobre", "inox") else 0.7
            esp_txt = "%.2f mm (referência)" % esp
        util = comp_chapa - transp
        pecas = ceil_int(L * 1000.0 / util)
        k = calha["tiras_por_chapa"] or 1
        chapas = ceil_int(pecas / float(k)) if calha["tiras_por_chapa"] else pecas
        area = pecas * dev / 1000.0 * comp_chapa / 1000.0
        peso = area * mat["dens"] * esp
        itens.append({"item": "%s %s - chapa %.0f x %.0f mm" % (
            mat["nome"], esp_txt, calha["largura_chapa"], comp_chapa),
            "qtd": chapas, "un": "chapa",
            "obs": "%d tira(s) de %.0f mm por chapa; %d peça(s) de %.2f m "
                   "(transpasse %.0f mm)" % (k if calha["tiras_por_chapa"] else 1, dev,
                                             pecas, comp_chapa / 1000.0, transp)})
        itens.append({"item": "Calha dobrada (desenvolvimento %.0f mm)" % dev,
                      "qtd": _r(L, 2), "un": "m",
                      "obs": "peso estimado %.1f kg (%.2f m² de chapa)" % (peso, area)})
        itens.append({"item": "Emendas/transpasses (rebite + solda estanho ou selante PU)",
                      "qtd": max(0, pecas - 1), "un": "emenda", "obs": ""})
        itens.append({"item": "Cabeceiras (tampas laterais) no mesmo material",
                      "qtd": 2, "un": "pç", "obs": "nas extremidades da calha"})
        itens.append({"item": "Bocal de saída (funil) para condutor DN %d" % cond["DN"],
                      "qtd": N, "un": "pç", "obs": "soldado/rebitado no fundo"})
    else:
        if mk == "pvc":
            itens.append({"item": "Calha PVC pré-fabricada (modelo comercial com "
                                  "capacidade ≥ %.0f L/min)" % calha["Qc"],
                          "qtd": _r(L, 2), "un": "m",
                          "obs": "seção mínima calculada: ver dimensões"})
            itens.append({"item": "Cabeceiras PVC (esq./dir.)", "qtd": 2, "un": "pç",
                          "obs": ""})
            itens.append({"item": "Bocal de saída PVC DN %d" % cond["DN"], "qtd": N,
                          "un": "pç", "obs": ""})
            itens.append({"item": "Emendas de calha PVC", "qtd": max(0, ceil_int(L / 3.0) - 1),
                          "un": "pç", "obs": "barras de 3 m (conferir fabricante)"})
        else:
            itens.append({"item": "Calha moldada in loco - %s (impermeabilizada)" %
                          mat["nome"], "qtd": _r(L, 2), "un": "m",
                          "obs": "seção interna %s" % (
                              "Ø%.0f mm" % calha["D_mm"] if calha["forma"] == "meiacana"
                              else "%.0f x %.0f mm" % (calha["b_mm"], calha["H_mm"]))})
            itens.append({"item": "Ralo/bocal de saída DN %d" % cond["DN"], "qtd": N,
                          "un": "pç", "obs": ""})
    esp_sup = entrada.get("esp_suporte", 0.80)
    itens.append({"item": "Suportes/escápulas de fixação da calha",
                  "qtd": ceil_int(L / esp_sup) + 1, "un": "pç",
                  "obs": "espaçamento ≤ %.2f m" % esp_sup})
    itens.append({"item": "Ralo hemisférico (grelha) para DN %d" % cond["DN"],
                  "qtd": N, "un": "pç", "obs": "evita obstrução por folhas"})
    Lc = float(entrada.get("altura_condutor", 3.0))
    total_tubo = N * Lc
    itens.append({"item": "Tubo PVC-U esgoto/pluvial DN %d (NBR 5688) - barra 6 m" %
                  cond["DN"], "qtd": ceil_int(total_tubo / 6.0), "un": "barra",
                  "obs": "%d condutor(es) x %.2f m = %.2f m" % (N, Lc, total_tubo)})
    itens.append({"item": "Joelho/curva 45° ou 90° PVC DN %d" % cond["DN"],
                  "qtd": 2 * N, "un": "pç", "obs": "2 por condutor (bocal e pé)"})
    itens.append({"item": "Abraçadeiras de fixação DN %d" % cond["DN"],
                  "qtd": N * (ceil_int(Lc / 1.5) + 1), "un": "pç",
                  "obs": "a cada ~1,5 m por condutor"})
    itens.append({"item": "Adesivo para PVC / anel de vedação", "qtd": 1, "un": "cj",
                  "obs": ""})
    return itens


# ---------------------------------------------------------------------------
# 10) ROTINA PRINCIPAL
# ---------------------------------------------------------------------------
def calcular(e):
    avisos = []
    T = int(e.get("T", 5))
    chuva = dados_chuva(e["uf"], e["cidade"], T, e.get("lat"), e.get("lon"),
                        e.get("I_manual"))
    avisos += chuva["avisos"]
    n_aguas = int(e.get("n_aguas", 1))
    area = area_contribuicao(n_aguas, float(e["a1"]), float(e.get("a2") or e["a1"]),
                             float(e["comprimento"]), float(e["inclinacao"]),
                             float(e.get("parede", 0) or 0))
    I = chuva["I"]
    Q = vazao_projeto(I, area["A_total"])
    N = max(1, int(e.get("N", 1)))
    S = max(0.005, float(e.get("declividade", 0.5)) / 100.0)
    if float(e.get("declividade", 0.5)) < 0.5:
        avisos.append("Declividade da calha elevada ao mínimo normativo de 0,5 %.")
    sentido = e.get("fluxo", "uni")
    trechos = N if sentido == "uni" else 2 * N
    coef, coef_desc = COEF_CURVA.get(e.get("curva", "nenhuma"), COEF_CURVA["nenhuma"])
    Q_trecho = Q / trechos
    Qc = Q_trecho * coef
    forma = e.get("forma", "beiral")
    if forma == "central" and n_aguas == 1:
        avisos.append("Calha central normalmente recebe 2 águas; verifique a entrada.")
    calha = dimensionar_calha(forma, e.get("material", "galvanizada"), Qc, S,
                              aba=float(e.get("aba", 100)),
                              bainha=float(e.get("bainha", 15)),
                              sobre=float(e.get("sobre", 20)),
                              largura_chapa=float(e.get("largura_chapa", 1200)),
                              otimizar_chapa=bool(e.get("otimizar", True)),
                              acresc_max=float(e.get("acresc_max", 30)))
    avisos += calha["avisos"]
    cond = dimensionar_condutor(Q, N, calha["lamina_max_mm"], e.get("saida", "aresta"))
    cond["saida"] = e.get("saida", "aresta")
    avisos += cond["avisos"]
    geo = geometria(calha, float(e["inclinacao"]))
    mats = materiais(e, calha, cond)
    if area["A_total"] <= 100 and chuva["fonte"].startswith("NBR"):
        nota_150 = ("Para área de projeção ≤ 100 m², a NBR 10844 admite adotar "
                    "I = 150 mm/h quando não houver dados locais.")
    else:
        nota_150 = ""
    return {
        "versao": VERSAO, "motor": "Brython" if BRYTHON else "CPython",
        "chuva": chuva, "area": area,
        "vazao": {"Q_total_Lmin": _r(Q, 1), "Q_total_Ls": _r(Q / 60, 3),
                  "trechos": trechos, "sentido": sentido,
                  "Q_trecho_Lmin": _r(Q_trecho, 1), "coef_curva": coef,
                  "coef_desc": coef_desc, "Q_calha_Lmin": _r(Qc, 1)},
        "calha": calha, "condutor": cond, "geometria": geo, "materiais": mats,
        "avisos": avisos, "nota_150": nota_150,
    }


# ---- Interface com o JavaScript (somente no navegador) ----
if BRYTHON:
    _TIPO = window.eval("(function(v){return v===null||v===undefined?'n':"
                        "(Array.isArray(v)?'a':typeof v)})")

    def _js2py(o):
        t = str(_TIPO(o))
        if t == "a":
            return [_js2py(x) for x in o]
        if t == "n":
            return None
        if t == "object":
            return dict((str(k), _js2py(o[k])) for k in window.Object.keys(o))
        return o

    def _api(nome, args_json):
        try:
            args = _js2py(window.JSON.parse(args_json))
            if nome == "ufs":
                r = listar_ufs()
            elif nome == "cidades":
                r = listar_cidades(args["uf"])
            elif nome == "chuva":
                r = dados_chuva(args["uf"], args["cidade"], int(args.get("T", 5)),
                                args.get("lat"), args.get("lon"), args.get("I_manual"))
            else:
                r = calcular(args)
            return to_json({"ok": True, "r": r})
        except Exception as ex:
            return to_json({"ok": False, "erro": str(type(ex).__name__) + ": " + str(ex)})

    window.pyApi = _api
    window.pyReady()

if __name__ == "__main__" and not BRYTHON:
    # Teste de validacao: NBR 10844 Tabela 2 (meia-cana D=100 mm, n=0,011,
    # i=0,5 %, lamina = D/2) -> 130 L/min
    A, P, B = secao_semi(100, 50)
    print("Meia-cana D100 i=0,5%%: %.1f L/min (NBR Tab.2: 130)" %
          manning(A, P, 0.005, 0.011))
    A, P, B = secao_semi(150, 75)
    print("Meia-cana D150 i=0,5%%: %.1f L/min (NBR Tab.2: 384)" %
          manning(A, P, 0.005, 0.011))
    A, P, B = secao_semi(200, 100)
    print("Meia-cana D200 i=1,0%%: %.1f L/min (NBR Tab.2: 1167)" %
          manning(A, P, 0.010, 0.011))
    r = calcular({"uf": "SP", "cidade": "Campinas", "T": 5, "n_aguas": 1,
                  "a1": 6.0, "comprimento": 12.0, "inclinacao": 30, "N": 2,
                  "declividade": 0.5, "forma": "beiral", "material": "galvanizada",
                  "altura_condutor": 3.0})
    import json
    print(json.dumps({k: r[k] for k in ("chuva", "area", "vazao")}, indent=1,
                     ensure_ascii=False)[:1500])
    c = dict(r["calha"]); c.pop("fixas"); print(c)
    print({k: v for k, v in r["condutor"].items() if k != "tabela"})
    for d in r["geometria"]["dobras"]:
        print(d)
    for m in r["materiais"]:
        print(m)
    print(r["avisos"])
