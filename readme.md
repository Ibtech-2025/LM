dados: https://drive.google.com/file/d/1CDycH6yfU1ZbXz6aQ8zIZ3GehZLnUsVN/view?usp=sharing

# Descrição das Colunas do Arquivo CSV

Este documento apresenta a descrição detalhada de cada coluna presente no arquivo CSV, explicando seu significado e finalidade.

## Estrutura do Arquivo

### Identificação do Centro de Distribuição
- **Unidade**: Nome do centro de distribuição responsável pelo processamento do pedido.
- **Filial**: Código identificador do centro de distribuição (exemplos: `WNE01`, `WNE02`).
  - A combinação das colunas **Unidade** e **Filial** define um centro de distribuição único.

### Informações do Pedido
- **Pedido**: Número do pedido realizado.
- **Produto**: Código do produto (**SKU**). Este dado é criptografado por motivos de segurança.
- **Descrição**: Descrição detalhada do produto (criptografado).
- **Familia**: Categoria principal à qual o produto pertence.
- **Subfamilia**: Categoria secundária do produto dentro da família principal.
- **CodMarca**: Código identificador da marca do produto.
- **CNPJ**: Cadastro Nacional da Pessoa Jurídica do cliente (criptografado).

### Dados Financeiros
- **Qtd**: Quantidade de unidades do produto vendidas no pedido.
- **VlrBruto**: Valor bruto da venda antes de descontos e impostos.
- **VlrSemImp**: Valor da venda sem a incidência de impostos.
- **CustoContabil**: Custo contábil associado ao produto vendido.
- **PedidoTab**: Preço de tabela unitário do produto antes da aplicação de descontos.
- **PedidoVend**: Preço final unitário do produto após descontos e negociações.

### Informações Geográficas
- **Região**: Nome da região geográfica onde ocorreu a venda.
- **UF**: Unidade Federativa (**Estado**) onde ocorreu a venda.
- **NomeMicroRegião**: Nome da microregião onde ocorreu a venda (criptografado).
- **CodigoIBGE**: Código do IBGE correspondente à localização da venda (criptografado).

### Metadados Comerciais
- **DescTipGrp**: Nome da marca do produto (criptografado).
- **AnoComercial**: Ano em que a venda foi realizada.
- **PeriodoComercial**: Mês comercial correspondente à venda.


