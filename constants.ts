import { RainfallData } from './types';

export const RAINFALL_INTENSITY_DATA: RainfallData = {
  "AC": { "Rio Branco": 139, "Sena Madureira": 160 },
  "AL": { "Maceió": 122 },
  "AM": { "Juaretê": 240, "Manaus": 180, "Paratins": 200, "Uaupés": 204 },
  "BA": { "Salvador": 122 },
  "CE": { "Fortaleza": 156, "Guaramiranga": 126, "Quixeramobim": 121 },
  "ES": { "Vitória": 156 },
  "FN": { "Fernando de Noronha": 120 },
  "GO": { "Catalão": 174, "Formosa": 176, "Goiânia": 178 },
  "MA": { "Barra do Corda": 128, "São Luiz": 126 },
  "MG": { "Barbacena": 222, "Belo Horizonte": 227, "Bonsucesso": 196, "Caxambu": 137, "Ouro Preto": 211, "Passa Quatro": 180, "Sete Lagoas": 182, "Teófilo Otoni": 121, "Turiaçu": 162 },
  "MT": { "Corumbá": 131, "Cuiabá": 190 },
  "PA": { "Alto Tapajós": 229, "Belém": 157, "Soure": 162, "Taperinha": 202 },
  "PB": { "João Pessoa": 140, "São Gonçalo": 124 },
  "PE": { "Nazaré": 134, "Olinda": 167 },
  "PI": { "Teresina": 240 },
  "PR": { "Curitiba": 204, "Jacarezinho": 122, "Paranaguá": 186, "Ponta Grossa": 126 },
  "RJ": { "Alto Itatiaia": 164, "Alto Teresópolis": 137, "Cabo Frio": 146, "Campos": 206, "km 47 - Rodovia Presidente Dutra": 164, "Niterói": 183, "Nova Friburgo": 124, "Petrópolis": 126, "Pinheiral": 214, "Resende": 203, "Rio de Janeiro (Bangu)": 156, "Rio de Janeiro (Ipanema)": 125, "Rio de Janeiro (Jacarepaguá)": 142, "Rio de Janeiro (Jardim Botânico)": 167, "Rio de Janeiro (Praça XV)": 174, "Rio de Janeiro (Praça Saenz Peña)": 139, "Rio de Janeiro (Santa Cruz)": 132, "Vassouras": 179, "Volta Redonda": 216 },
  "RN": { "Natal": 120 },
  "RO": { "Porto Velho": 167 },
  "RS": { "Alegrete": 238, "Bagé": 204, "Caxias do Sul": 127, "Cruz Alta": 246, "Encruzilhada": 126, "Iraí": 198, "Passo Fundo": 125, "Porto Alegre": 146, "Rio Grande": 204, "Santa Maria": 122, "Santa Vitória do Palmar": 126, "São Luiz Gonzaga": 209, "Uruguaiana": 142, "Viamão": 126 },
  "SC": { "Blumenau": 125, "Florianópolis": 120, "São Francisco do Sul": 132 },
  "SE": { "Aracaju": 122 },
  "SP": { "Avaré": 144, "Bauru": 120, "Campos do Jordão": 144, "Lins": 122, "Piracicaba": 122, "Santos": 198, "Santos-Itapema": 174, "São Carlos": 178, "São Paulo (Congonhas)": 132, "São Paulo (Mirante Santana)": 172, "São Simão": 148, "Taubaté": 172, "Tupi": 154, "Ubatuba": 149 }
};

export const GUTTER_MATERIALS = {
  'Chapa Metálica': 0.011,
  'PVC': 0.011,
  'Chapa Galvanizada': 0.011,
};

export const STANDARD_DOWNSPOUT_DIAMETERS = [75, 100, 125, 150, 200, 250, 300];

export const STATES = Object.keys(RAINFALL_INTENSITY_DATA).sort();