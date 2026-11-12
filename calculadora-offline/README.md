# Calculadora de Calhas e Condutores Pluviais (offline, arquivo único)

**Arquivo para uso:** `calculadora_calhas.html`. Abra direto no navegador (Chrome, Edge, Firefox), sem internet e sem instalar nada.

Os cálculos são feitos em **Python** (`calhas_calc.py`), rodando no navegador pelo
[Brython 3.12.4](https://brython.info) (BSD-3-Clause), que vai embutido no próprio HTML.

## O que faz
- **Chuva:** a partir do Estado e da cidade, localiza o posto pluviográfico mais próximo da
  NBR 10844:1989, Tabela 5 (t = 5 min). Mostra I para T = 1, 5 e 25 anos, a intensidade de
  projeto, as equivalências (L/min·m², L/s·m², altura precipitada) e os 3 postos mais próximos.
  Aceita coordenadas ou intensidade manual (para uma equação IDF local).
- **Área de contribuição:** 1 ou 2 águas, A = (a + h/2)·b, mais parede vertical opcional (50 %).
- **Vazão:** Q = I·A/60, dividida pelos trechos (descidas nas extremidades ou no meio) e
  multiplicada pelo coeficiente de curvas da NBR 10844.
- **Calha** (beiral, central, retangular ou meia-cana; chapa galvanizada, alumínio, cobre,
  inox, PVC, fibrocimento, concreto, alvenaria, cerâmica): Manning-Strickler com K = 60 000.
  Calcula largura, altura, lâmina d'água, borda livre, velocidade e Froude.
- **Corte da chapa:** procura uma tira de 1200/k mm (600, 400, 300, 240…) para cortar sem sobra.
  Se precisar, reduz as abas (mínimo de 60 mm) ou aumenta a seção, até o limite de acréscimo
  definido pelo usuário.
- **Condutores PVC (NBR 5688):** DN 75, 100, 150 e 200, com DI mínimo de 70 mm (NBR 10844).
- **Desenho** em corte com cotas de cada dobra, ângulos internos, lâmina d'água e condutor
  com o diâmetro, mais a planificação da tira e o plano de corte da chapa.
- **Relatório** exportável (HTML) ou impressão/PDF, com dados pluviométricos, desenho,
  memória de cálculo e lista de materiais.

## Validação
`python3 calhas_calc.py` compara o motor com a Tabela 2 da NBR 10844 (calhas semicirculares,
n = 0,011):
D100/0,5 % = 129,5 L/min (tabela: 130), D150/0,5 % = 381,8 (384), D200/1 % = 1162,9 (1167).

## Critérios que não vêm da norma (confira)
- **Condutores verticais:** a NBR 10844 usa os ábacos da Fig. 3. Aqui o método é analítico
  e conservador: a entrada é limitada por vertedouro ou orifício, e o tubo de queda é
  verificado por Wyly-Eaton com ocupação de 1/3.
- **Lâmina máxima em calha retangular:** 2/3 da altura. Na meia-cana a lâmina é D/2 (Tab. 2).
- **Intensidades e coordenadas dos postos:** foram transcritas da Tabela 5 e precisam ser
  conferidas com o texto oficial. Quando houver equação IDF local atualizada, prefira-a.
- **Espessura de chapa, espaçamento de suportes e acessórios:** são práticas usuais de mercado.

## Gerar o HTML de novo
```
python3 build.py   # template.html + calhas_calc.py + vendor/brython → calculadora_calhas.html
```
