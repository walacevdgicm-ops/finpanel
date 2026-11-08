# 📊 FinPanel — Painel de Gestão Financeira

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-informational)
![Matplotlib](https://img.shields.io/badge/Gráficos-Matplotlib-orange)

Painel desktop de **consultoria e gestão financeira**: dashboard executivo, contas a pagar e receber, estoque, inadimplência, **cobrança via WhatsApp** e **metas financeiras com barra de progresso**.

Foi o ponto de partida do meu ERP: um protótipo rápido, com dados em memória, para validar telas e fluxos antes de colocar banco de dados.

## ✨ Funcionalidades

- 📈 **Dashboard executivo** com gráficos interativos (Matplotlib)
- 👥 Cadastro de clientes/fornecedores com **consulta automática de CNPJ** (ReceitaWS)
- 📦 **Gerenciamento de estoque**
- 💸 **Contas a pagar** com parcelamento e **contas a receber**
- ⏰ **Gestão de inadimplência** com mensagem de cobrança pronta para o **WhatsApp Web**
- 🎯 **Metas financeiras**: faturamento, lucro e teto de gastos com percentual atingido

## 🚀 Como executar

```bash
pip install -r requirements.txt
python finpanel.py
```

## 🧭 Evolução do projeto

**`FinPanel`** → [`FinPanel SQLite`](https://github.com/walacevdgicm-ops/finpanel-sqlite) → [`Nexus ERP v1`](https://github.com/walacevdgicm-ops/nexus-erp-v1) → [`Nexus ERP`](https://github.com/walacevdgicm-ops/nexus-erp)

## 👨‍💻 Autor

**Walace Soares Vidigal Junior** · [GitHub](https://github.com/walacevdgicm-ops)

Licença [MIT](LICENSE)
