import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import webbrowser
import requests
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AppControleFinanceiro:
    def __init__(self, root):
        self.root = root
        self.root.title("Consultoria e Gestão Financeira - Painel Corporativo")
        self.root.geometry("1200x850")
        self.root.configure(bg="#f4f6f9")
        
        # Configuração de Estilo Visual (Layout Corporativo de Alto Padrão)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background="#f4f6f9", borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[12, 5])
        self.style.configure("TButton", font=("Arial", 10, "bold"), background="#1a365d", foreground="white")
        self.style.map("TButton", background=[("active", "#2b6cb0")])
        
        # Bancos de Dados Temporários na Memória (Estruturas de Dados)
        self.dados_contas_pagar = []
        self.dados_contas_receber = []
        self.dados_entidades = []  # Armazena Clientes e Fornecedores cadastrados
        self.dados_estoque = []    # Armazena os Produtos em Estoque
        
        # Metas Financeiras (Valores Padrão Editáveis)
        self.meta_faturamento = 50000.0
        self.meta_lucro = 20000.0
        self.meta_custos = 15000.0
        
        # Estrutura de Abas (Notebook)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Inicialização Primária das Telas das Abas
        self.aba_dashboard = ttk.Frame(self.notebook)
        self.aba_entidades = ttk.Frame(self.notebook)
        self.aba_estoque = ttk.Frame(self.notebook)  # NOVA ABA DE ESTOQUE
        self.aba_pagar = ttk.Frame(self.notebook)
        self.aba_receber = ttk.Frame(self.notebook)
        self.aba_inadimplencia = ttk.Frame(self.notebook)
        self.aba_metas = ttk.Frame(self.notebook)
        
        self.notebook.add(self.aba_dashboard, text="Dashboard Executivo")
        self.notebook.add(self.aba_entidades, text="Cadastro de Entidades")
        self.notebook.add(self.aba_estoque, text="Gerenciamento de Estoque")
        self.notebook.add(self.aba_pagar, text="Contas a Pagar")
        self.notebook.add(self.aba_receber, text="Contas a Receber")
        self.notebook.add(self.aba_inadimplencia, text="Gestão de Inadimplência")
        self.notebook.add(self.aba_metas, text="Metas Financeiras")
        
        # Evento reativo ao alternar entre as abas do sistema
        self.notebook.bind("<<NotebookTabChanged>>", self.ao_alternar_aba)
        
        # Construção Inicial de Layouts Estáticos e Formulários
        self.criar_layout_entidades()
        self.criar_layout_estoque()  # Construção da interface de estoque
        self.criar_layout_contas_pagar()
        self.criar_layout_contas_receber()
        
    def ao_alternar_aba(self, event):
        """ Renderização sob demanda para garantir atualização em tempo real e performance """
        aba_atual = self.notebook.index(self.notebook.select())
        if aba_atual == 0: self.renderizar_dashboard_executivo()
        elif aba_atual == 4: self.renderizar_inadimplencia()
        elif aba_atual == 5: self.renderizar_metas()

    # =========================================================================
    # NOVA ABA: GERENCIAMENTO DE ESTOQUE (INTEGRADA COM FORNECEDORES)
    # =========================================================================
    def criar_layout_estoque(self):
        # 1.1 Formulário de Cadastro de Produto
        frame_form = tk.LabelFrame(self.aba_estoque, text=" Cadastrar Novo Produto no Estoque ", font=("Arial", 11, "bold"), fg="#1a365d", bg="white", padx=15, pady=15)
        frame_form.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_form, text="Descrição Produto:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_desc_produto = ttk.Entry(frame_form, width=30)
        self.entry_desc_produto.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Part Number:", bg="white").grid(row=0, column=2, sticky="w", padx=15)
        self.entry_part_number = ttk.Entry(frame_form, width=20)
        self.entry_part_number.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Fornecedor Vinculado:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_fornecedor_produto = ttk.Combobox(frame_form, values=[], width=27, state="readonly")
        self.combo_fornecedor_produto.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Qtd. Inicial:", bg="white").grid(row=1, column=2, sticky="w", padx=15)
        self.entry_qtd_inicial = ttk.Entry(frame_form, width=10)
        self.entry_qtd_inicial.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.entry_qtd_inicial.insert(0, "0")
        
        btn_salvar_prod = ttk.Button(frame_form, text="Salvar Produto", command=self.adicionar_produto_estoque)
        btn_salvar_prod.grid(row=2, column=0, columnspan=4, pady=12)
        
        # 1.2 Painel de Gerenciamento Visual (Tabela e Alteração de Quantidades)
        frame_tabela = tk.LabelFrame(self.aba_estoque, text=" Painel do Estoque Atual e Movimentação ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)
        
        colunas = ("id", "desc", "pn", "forn", "qtd")
        self.tree_estoque = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        self.tree_estoque.heading("id", text="ID")
        self.tree_estoque.heading("desc", text="Descrição / Item")
        self.tree_estoque.heading("pn", text="Part Number")
        self.tree_estoque.heading("forn", text="Fornecedor")
        self.tree_estoque.heading("qtd", text="Quantidade em Estoque")
        
        self.tree_estoque.column("id", width=50, anchor="center")
        self.tree_estoque.column("desc", width=350, anchor="w")
        self.tree_estoque.column("pn", width=150, anchor="center")
        self.tree_estoque.column("forn", width=250, anchor="w")
        self.tree_estoque.column("qtd", width=150, anchor="center")
        
        self.tree_estoque.pack(fill="both", expand=True, side="top")
        
        # Botões operacionais para alterar a quantidade em estoque
        frame_botoes_estoque = ttk.Frame(frame_tabela)
        frame_botoes_estoque.pack(pady=10, fill="x")
        
        btn_entrada = ttk.Button(frame_botoes_estoque, text="➕ Dar Entrada no Estoque", command=lambda: self.alterar_quantidade_estoque(operacao="entrada"))
        btn_entrada.pack(side="left", padx=20, expand=True)
        
        btn_saida = ttk.Button(frame_botoes_estoque, text="➖ Dar Saída no Estoque", command=lambda: self.alterar_quantidade_estoque(operacao="saida"))
        btn_saida.pack(side="right", padx=20, expand=True)

    def adicionar_produto_estoque(self):
        desc = self.entry_desc_produto.get().strip()
        pn = self.entry_part_number.get().strip()
        forn = self.combo_fornecedor_produto.get()
        qtd_str = self.entry_qtd_inicial.get().strip()
        
        if not desc or not pn:
            messagebox.showerror("Erro", "Descrição e Part Number são obrigatórios.")
            return
        if not forn:
            messagebox.showerror("Erro", "Selecione um Fornecedor cadastrado. Caso não exista nenhum, cadastre-o primeiro na aba 'Cadastro de Entidades'.")
            return
            
        try:
            qtd = int(qtd_str)
            if qtd < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "A quantidade inicial precisa ser um número inteiro válido e positivo.")
            return
            
        id_p = len(self.dados_estoque) + 1
        # Estrutura: [ID, Descrição, Part Number, Fornecedor, Quantidade]
        self.dados_estoque.append([id_p, desc, pn, forn, qtd])
        
        self.atualizar_tabela_estoque_visual()
        
        # Limpar Campos
        self.entry_desc_produto.delete(0, tk.END)
        self.entry_part_number.delete(0, tk.END)
        self.combo_fornecedor_produto.set("")
        self.entry_qtd_inicial.delete(0, tk.END)
        self.entry_qtd_inicial.insert(0, "0")
        messagebox.showinfo("Sucesso", "Produto inserido no inventário!")

    def atualizar_tabela_estoque_visual(self):
        """ Atualiza os registros visuais exibidos na Treeview do Estoque """
        for item in self.tree_estoque.get_children():
            self.tree_estoque.delete(item)
            
        for prod in self.dados_estoque:
            self.tree_estoque.insert("", "end", values=(prod[0], prod[1], prod[2], prod[3], prod[4]))

    def alterar_quantidade_estoque(self, operacao):
        """ Permite o usuário gerenciar as entradas e saídas físicas do material """
        selecionado = self.tree_estoque.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item na tabela de estoque para alterar a quantidade.")
            return
            
        valores = self.tree_estoque.item(selecionado, "values")
        id_prod = int(valores[0])
        desc_prod = valores[1]
        
        titulo_prompt = "Entrada de Material" if operacao == "entrada" else "Saída de Material"
        texto_prompt = f"Quantidade a ser ADICIONADA ao item '{desc_prod}':" if operacao == "entrada" else f"Quantidade a ser RETIRADA do item '{desc_prod}':"
        
        qtd_movimento = simpledialog.askinteger(titulo_prompt, texto_prompt, minvalue=1)
        
        if qtd_movimento:
            for prod in self.dados_estoque:
                if prod[0] == id_prod:
                    if operacao == "entrada":
                        prod[4] += qtd_movimento
                        messagebox.showinfo("Sucesso", f"Entrada processada! Nova quantidade: {prod[4]}")
                    elif operacao == "saida":
                        if prod[4] - qtd_movimento < 0:
                            messagebox.showerror("Erro", f"Saldo insuficiente em estoque! Saldo atual é de apenas {prod[4]} unidade(s).")
                            return
                        prod[4] -= qtd_movimento
                        messagebox.showinfo("Sucesso", f"Saída processada! Nova quantidade: {prod[4]}")
                    break
            self.atualizar_tabela_estoque_visual()

    # =========================================================================
    # CADASTRO DE ENTIDADES (CLIENTES / FORNECEDORES) COM BUSCA CNPJ
    # =========================================================================
    def criar_layout_entidades(self):
        frame_form = tk.LabelFrame(self.aba_entidades, text=" Cadastrar Cliente ou Fornecedor ", font=("Arial", 11, "bold"), fg="#1a365d", bg="white", padx=15, pady=15)
        frame_form.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_form, text="Tipo:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_tipo_entidade = ttk.Combobox(frame_form, values=["Cliente", "Fornecedor"], width=15, state="readonly")
        self.combo_tipo_entidade.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.combo_tipo_entidade.set("Cliente")
        
        tk.Label(frame_form, text="CNPJ (Apenas números):", bg="white").grid(row=0, column=2, sticky="w", padx=10)
        self.entry_cnpj = ttk.Entry(frame_form, width=20)
        self.entry_cnpj.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        self.btn_buscar_cnpj = ttk.Button(frame_form, text="Buscar Dados (Receita/SEFAZ)", command=self.disparar_busca_cnpj)
        self.btn_buscar_cnpj.grid(row=0, column=4, padx=10, pady=5)
        
        tk.Label(frame_form, text="Razão Social / Nome:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_nome_entidade = ttk.Entry(frame_form, width=35)
        self.entry_nome_entidade.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Telefone / Whats:", bg="white").grid(row=1, column=3, sticky="w", padx=10)
        self.entry_tel_entidade = ttk.Entry(frame_form, width=18)
        self.entry_tel_entidade.grid(row=1, column=4, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Cidade/UF:", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_cidade_entidade = ttk.Entry(frame_form, width=25)
        self.entry_cidade_entidade.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        btn_adicionar = ttk.Button(frame_form, text="Salvar Entidade", command=self.adicionar_entity)
        btn_adicionar.grid(row=3, column=0, columnspan=5, pady=10)
        
        frame_tabela = tk.LabelFrame(self.aba_entidades, text=" Entidades Cadastradas ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)
        
        colunas = ("id", "tipo", "nome", "cnpj", "telefone", "localidade")
        self.tree_entidades = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        self.tree_entidades.heading("id", text="ID")
        self.tree_entidades.heading("tipo", text="Tipo")
        self.tree_entidades.heading("nome", text="Razão Social / Nome")
        self.tree_entidades.heading("cnpj", text="CNPJ")
        self.tree_entidades.heading("telefone", text="Telefone")
        self.tree_entidades.heading("localidade", text="Cidade/UF")
        
        self.tree_entidades.column("id", width=50, anchor="center")
        self.tree_entidades.column("tipo", width=100, anchor="center")
        self.tree_entidades.column("nome", width=350, anchor="w")
        self.tree_entidades.column("cnpj", width=150, anchor="center")
        self.tree_entidades.column("telefone", width=130, anchor="center")
        self.tree_entidades.column("localidade", width=150, anchor="w")
        self.tree_entidades.pack(fill="both", expand=True)

    def disparar_busca_cnpj(self):
        cnpj = "".join(filter(str.isdigit, self.entry_cnpj.get().strip()))
        if len(cnpj) != 14:
            messagebox.showwarning("Aviso", "Insira um CNPJ válido com 14 dígitos.")
            return
        self.btn_buscar_cnpj.config(state="disabled")
        threading.Thread(target=self.executar_busca_api_cnpj, args=(cnpj,), daemon=True).start()

    def executar_busca_api_cnpj(self, cnpj):
        try:
            url = f"https://receitaws.com.br/v1/cnpj/{cnpj}"
            resposta = requests.get(url, timeout=8)
            if resposta.status_code == 200:
                dados = resposta.json()
                if dados.get("status") == "ERROR":
                    self.root.after(0, lambda: messagebox.showerror("Erro", f"CNPJ inválido ou não encontrado: {dados.get('message')}"))
                else:
                    nome = dados.get("nome", "")
                    cidade = f"{dados.get('municipio', '')}/{dados.get('uf', '')}"
                    telefone = dados.get("telefone", "")
                    self.root.after(0, lambda: self.preencher_campos_cnpj(nome, city=cidade, tel=telefone))
            else:
                self.root.after(0, lambda: messagebox.showerror("Erro", "Não foi possível conectar ao servidor de consulta."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Falha de conexão: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.btn_buscar_cnpj.config(state="normal"))

    def preencher_campos_cnpj(self, nome, city, tel):
        self.entry_nome_entidade.delete(0, tk.END)
        self.entry_nome_entidade.insert(0, nome)
        self.entry_cidade_entidade.delete(0, tk.END)
        self.entry_cidade_entidade.insert(0, city)
        self.entry_tel_entidade.delete(0, tk.END)
        self.entry_tel_entidade.insert(0, tel)
        messagebox.showinfo("Sucesso", "Dados capturados e preenchidos com sucesso!")

    def adicionar_entity(self):
        tipo = self.combo_tipo_entidade.get()
        nome = self.entry_nome_entidade.get().strip()
        cnpj = self.entry_cnpj.get().strip()
        telefone = self.entry_tel_entidade.get().strip()
        cidade = self.entry_cidade_entidade.get().strip()
        
        if not nome:
            messagebox.showerror("Erro", "O campo 'Razão Social / Nome' é obrigatório.")
            return
            
        id_e = len(self.dados_entidades) + 1
        self.dados_entidades.append((id_e, tipo, nome, cnpj if cnpj else "Não Informado", telefone, cidade))
        self.tree_entidades.insert("", "end", values=(id_e, tipo, nome, cnpj if cnpj else "N/I", telefone, cidade))
        
        self.entry_cnpj.delete(0, tk.END)
        self.entry_nome_entidade.delete(0, tk.END)
        self.entry_tel_entidade.delete(0, tk.END)
        self.entry_cidade_entidade.delete(0, tk.END)
        
        self.atualizar_combos_vinculo_entidades()
        messagebox.showinfo("Sucesso", f"{tipo} cadastrado com sucesso!")

    def atualizar_combos_vinculo_entidades(self):
        clientes = [e[2] for e in self.dados_entidades if e[1] == "Cliente"]
        fornecedores = [e[2] for e in self.dados_entidades if e[1] == "Fornecedor"]
        
        self.combo_fornecedor_pagar.config(values=fornecedores)
        self.combo_cliente_receber.config(values=clientes)
        self.combo_fornecedor_produto.config(values=fornecedores)  # Atualiza os fornecedores da aba de estoque

    # =========================================================================
    # DASHBOARD EXECUTIVO INTERATIVO (COM TOOLTIP E HOVER)
    # =========================================================================
    def renderizar_dashboard_executivo(self):
        for widget in self.aba_dashboard.winfo_children(): widget.destroy()
        
        faturamento = sum(item[2] for item in self.dados_contas_receber)
        despesas_fixas = sum(item[2] for item in self.dados_contas_pagar if "Fixo" in str(item[3]) or "Boleto" in str(item[3]))
        despesas_variaveis = sum(item[2] for item in self.dados_contas_pagar) - despesas_fixas
        total_despesas = despesas_fixas + despesas_variaveis
        lucro_liquido = faturamento - total_despesas
        
        hoje = datetime.now()
        inadimplencia = sum(item[2] for item in self.dados_contas_receber if datetime.strptime(item[3], "%d/%m/%Y") < hoje)
        ticket_medio = faturamento / len(self.dados_contas_receber) if self.dados_contas_receber else 0.0
        
        self.lbl_tooltip = tk.Label(self.aba_dashboard, text="Passe o mouse sobre os elementos dos gráficos para ver os detalhes", 
                                    font=("Arial", 11, "bold"), fg="#2b6cb0", bg="#f4f6f9", pady=4)
        self.lbl_tooltip.pack(fill="x")
        
        frame_cards = ttk.Frame(self.aba_dashboard)
        frame_cards.pack(fill="x", padx=10, pady=5)
        
        kpis = [
            ("Faturamento do Mês", f"R$ {faturamento:,.2f}", "#2f855a"),
            ("Lucro Líquido", f"R$ {lucro_liquido:,.2f}", "#2b6cb0" if lucro_liquido >= 0 else "#c53030"),
            ("Despesas Fixas", f"R$ {despesas_fixas:,.2f}", "#4a5568"),
            ("Despesas Variáveis", f"R$ {despesas_variaveis:,.2f}", "#718096"),
            ("Inadimplência Crítica", f"R$ {inadimplencia:,.2f}", "#e53e3e"),
            ("Ticket Médio", f"R$ {ticket_medio:,.2f}", "#d69e2e")
        ]
        
        for i, (titulo, valor, cor) in enumerate(kpis):
            card = tk.Frame(frame_cards, bg="white", highlightbackground="#e2e8f0", highlightthickness=1, padx=12, pady=12)
            card.grid(row=i//3, column=i%3, padx=8, pady=6, sticky="nsew")
            tk.Label(card, text=titulo, font=("Arial", 9, "bold"), fg="#718096", bg="white").pack(anchor="w")
            tk.Label(card, text=valor, font=("Arial", 15, "bold"), fg=cor, bg="white", pady=3).pack(anchor="w")
            frame_cards.grid_columnconfigure(i%3, weight=1)

        frame_graficos = ttk.Frame(self.aba_dashboard)
        frame_graficos.pack(fill="both", expand=True, padx=10, pady=5)
        
        if not self.dados_contas_pagar and not self.dados_contas_receber:
            tk.Label(frame_graficos, text="Insira dados de receitas ou despesas para ativar os gráficos interativos.", font=("Arial", 11, "italic")).pack(pady=40)
            return

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))
        fig.patch.set_facecolor('#f4f6f9')

        barras = ax1.bar(['Receber', 'Pagar'], [faturamento, total_despesas], color=['#2f855a', '#c53030'], width=0.5)
        ax1.set_title("Balanço Mensal (R$)", fontsize=9, fontweight='bold', color='#1a365d')
        ax1.set_facecolor('white')

        datas_pagar = {}
        for item in self.dados_contas_pagar:
            d_venc = item[5]
            datas_pagar[d_venc] = datas_pagar.get(d_venc, 0) + item[2]
        datas_ordenadas = sorted(datas_pagar.keys())
        valores_ordenados = [datas_pagar[d] for d in datas_ordenadas]

        if datas_ordenadas:
            ax2.plot(datas_ordenadas, valores_ordenados, marker='o', color='#3182ce', linewidth=2)
            ax2.set_title("Fluxo de Saídas por Vencimento", fontsize=9, fontweight='bold', color='#1a365d')
            ax2.tick_params(axis='x', rotation=25, labelsize=7)
        else:
            ax2.text(0.5, 0.5, 'Sem dados de saída', ha='center', va='center', fontsize=9, style='italic')
        ax2.set_facecolor('white')

        if self.dados_contas_pagar:
            descricoes = [item[1] for item in self.dados_contas_pagar]
            valores_despesas = [item[2] for item in self.dados_contas_pagar]
            wedges, texts = ax3.pie(valores_despesas, labels=descricoes, startangle=90, 
                                    textprops=dict(color="black", size=7),
                                    wedgeprops=dict(width=0.4, edgecolor='w'))
            ax3.set_title("Distribuição por Despesa", fontsize=9, fontweight='bold', color='#1a365d')
        else:
            ax3.text(0.5, 0.5, 'Sem despesas', ha='center', va='center', fontsize=9, style='italic')

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame_graficos)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        def ao_mover_mouse(event):
            if event.inaxes == ax1:
                for bar in barras:
                    contem, _ = bar.contains(event)
                    if contem:
                        label_tipo = 'Contas a Receber' if bar.get_x() < 0 else 'Contas a Pagar'
                        self.lbl_tooltip.config(text=f"Grupo: {label_tipo} | Total Consolidado: R$ {bar.get_height():,.2f}")
                        return
            elif event.inaxes == ax2 and datas_ordenadas:
                contem, ind = ax2.lines[0].contains(event)
                if contem:
                    idx = ind['ind'][0]
                    self.lbl_tooltip.config(text=f"Data de Vencimento: {datas_ordenadas[idx]} | Total do Dia: R$ {valores_ordenados[idx]:,.2f}")
                    return
            elif event.inaxes == ax3 and self.dados_contas_pagar:
                for i, wedge in enumerate(wedges):
                    contem, _ = wedge.contains(event)
                    if contem:
                        self.lbl_tooltip.config(text=f"Lançamento: {descricoes[i]} | Valor Individual: R$ {valores_despesas[i]:,.2f}")
                        return
            self.lbl_tooltip.config(text="Passe o mouse sobre os elementos dos gráficos para ver os detalhes")

        fig.canvas.mpl_connect("motion_notify_event", ao_mover_mouse)
        canvas.draw()

    # =========================================================================
    # CONTAS A PAGAR (ATÉ 24X NO CRÉDITO)
    # =========================================================================
    def criar_layout_contas_pagar(self):
        frame_form = tk.LabelFrame(self.aba_pagar, text=" Novo Lançamento de Despesa ", font=("Arial", 11, "bold"), fg="#1a365d", bg="white", padx=15, pady=15)
        frame_form.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_form, text="Descrição:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_descricao = ttk.Entry(frame_form, width=25)
        self.entry_descricao.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_form, text="Valor (R$):", bg="white").grid(row=0, column=2, sticky="w", padx=10)
        self.entry_valor = ttk.Entry(frame_form, width=12)
        self.entry_valor.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_form, text="Vencimento:", bg="white").grid(row=0, column=4, sticky="w", padx=10)
        self.entry_data_pagar = ttk.Entry(frame_form, width=14)
        self.entry_data_pagar.grid(row=0, column=5, padx=5, pady=5)
        self.entry_data_pagar.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        tk.Label(frame_form, text="Fornecedor:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_fornecedor_pagar = ttk.Combobox(frame_form, values=[], width=22, state="readonly")
        self.combo_fornecedor_pagar.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Forma:", bg="white").grid(row=1, column=2, sticky="w", padx=10)
        self.combo_forma_pagto = ttk.Combobox(frame_form, values=["Dinheiro", "Pix", "Boleto Fixo", "Cartão de Crédito"], width=15, state="readonly")
        self.combo_forma_pagto.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.combo_forma_pagto.set("Pix")
        self.combo_forma_pagto.bind("<<ComboboxSelected>>", self.toggle_campo_parcelas)
        
        self.lbl_parcelas = tk.Label(frame_form, text="Parcelas:", bg="white")
        self.combo_parcelas = ttk.Combobox(frame_form, values=[f"{i}x" for i in range(1, 24)], width=8, state="readonly")
        
        btn_salvar = ttk.Button(frame_form, text="Adicionar Despesa", command=self.adicionar_conta_pagar)
        btn_salvar.grid(row=2, column=0, columnspan=6, pady=12)
        
        frame_tabela = tk.LabelFrame(self.aba_pagar, text=" Painel de Exibição ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree_pagar = ttk.Treeview(frame_tabela, columns=("id", "desc", "forn", "val", "forma", "parc", "venc"), show="headings")
        self.tree_pagar.heading("id", text="ID"); self.tree_pagar.heading("desc", text="Descrição"); self.tree_pagar.heading("forn", text="Fornecedor"); self.tree_pagar.heading("val", text="Valor"); self.tree_pagar.heading("forma", text="Forma"); self.tree_pagar.heading("parc", text="Parc."); self.tree_pagar.heading("venc", text="Vencimento")
        self.tree_pagar.pack(fill="both", expand=True)

    def toggle_campo_parcelas(self, event):
        if self.combo_forma_pagto.get() == "Cartão de Crédito":
            self.lbl_parcelas.grid(row=1, column=4, sticky="w", padx=10)
            self.combo_parcelas.grid(row=1, column=5, padx=5, pady=5, sticky="w")
            self.combo_parcelas.set("1x")
        else:
            self.lbl_parcelas.grid_forget()
            self.combo_parcelas.grid_forget()

    def adicionar_conta_pagar(self):
        try:
            desc = self.entry_descricao.get().strip()
            forn = self.combo_fornecedor_pagar.get()
            valor = float(self.entry_valor.get().replace(",", "."))
            venc = self.entry_data_pagar.get().strip()
            forma = self.combo_forma_pagto.get()
            datetime.strptime(venc, "%d/%m/%Y")
            
            parcelas = self.combo_parcelas.get() if forma == "Cartão de Crédito" else "À Vista"
            exibicao_desc = f"{desc} ({forn})" if forn else desc
            
            id_c = len(self.dados_contas_pagar) + 1
            self.dados_contas_pagar.append((id_c, exibicao_desc, valor, forma, parcelas, venc, datetime.now().strftime("%d/%m/%Y")))
            self.tree_pagar.insert("", "end", values=(id_c, desc, forn if forn else "N/V", f"R$ {valor:,.2f}", forma, parcelas, venc))
            
            self.entry_descricao.delete(0, tk.END)
            self.entry_valor.delete(0, tk.END)
            self.combo_forma_pagto.set("Pix")
            self.combo_fornecedor_pagar.set("")
            self.lbl_parcelas.grid_forget()
            self.combo_parcelas.grid_forget()
            messagebox.showinfo("Sucesso", "Lançamento de despesa efetuado.")
        except Exception:
            messagebox.showerror("Erro", "Valide se as entradas numéricas estão corretas e se o vencimento segue DD/MM/AAAA.")

    # =========================================================================
    # CONTAS A RECEBER
    # =========================================================================
    def criar_layout_contas_receber(self):
        frame_form_receber = tk.LabelFrame(self.aba_receber, text=" Novo Lançamento de Receita ", font=("Arial", 11, "bold"), fg="#1a365d", bg="white", padx=15, pady=15)
        frame_form_receber.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_form_receber, text="Descrição Serviço:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_desc_receber = ttk.Entry(frame_form_receber, width=30)
        self.entry_desc_receber.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_form_receber, text="Valor (R$):", bg="white").grid(row=0, column=2, sticky="w", padx=10)
        self.entry_val_receber = ttk.Entry(frame_form_receber, width=15)
        self.entry_val_receber.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_form_receber, text="Cliente Vinculado:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_cliente_receber = ttk.Combobox(frame_form_receber, values=[], width=27, state="readonly")
        self.combo_cliente_receber.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form_receber, text="Data Vencimento:", bg="white").grid(row=1, column=2, sticky="w", padx=10)
        self.entry_data_receber = ttk.Entry(frame_form_receber, width=16)
        self.entry_data_receber.grid(row=1, column=3, padx=5, pady=5)
        self.entry_data_receber.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        ttk.Button(frame_form_receber, text="Adicionar Receita", command=self.adicionar_conta_receber).grid(row=2, column=0, columnspan=4, pady=12)
        
        frame_tabela_receber = tk.LabelFrame(self.aba_receber, text=" Painel de Exibição ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        frame_tabela_receber.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree_receber = ttk.Treeview(frame_tabela_receber, columns=("id", "desc", "cli", "val", "venc"), show="headings")
        self.tree_receber.heading("id", text="ID"); self.tree_receber.heading("desc", text="Descrição"); self.tree_receber.heading("cli", text="Cliente"); self.tree_receber.heading("val", text="Valor"); self.tree_receber.heading("venc", text="Vencimento")
        self.tree_receber.pack(fill="both", expand=True)

    def adicionar_conta_receber(self):
        try:
            desc = self.entry_desc_receber.get().strip()
            cli = self.combo_cliente_receber.get()
            valor = float(self.entry_val_receber.get().replace(",", "."))
            venc = self.entry_data_receber.get().strip()
            datetime.strptime(venc, "%d/%m/%Y")
            
            exibicao_nome = f"{cli if cli else desc}"
            
            id_r = len(self.dados_contas_receber) + 1
            self.dados_contas_receber.append((id_r, exibicao_nome, valor, venc, datetime.now().strftime("%d/%m/%Y")))
            self.tree_receber.insert("", "end", values=(id_r, desc, cli if cli else "N/V", f"R$ {valor:,.2f}", venc))
            
            self.entry_desc_receber.delete(0, tk.END)
            self.entry_val_receber.delete(0, tk.END)
            self.combo_cliente_receber.set("")
            messagebox.showinfo("Sucesso", "Lançamento de receita efetuado.")
        except Exception:
            messagebox.showerror("Erro", "Valide os campos inseridos.")

    # =========================================================================
    # GESTÃO DE INADIMPLÊNCIA (NOTIFICAÇÃO OPERACIONAL VIA WHATSAPP)
    # =========================================================================
    def renderizar_inadimplencia(self):
        for widget in self.aba_inadimplencia.winfo_children(): widget.destroy()
        
        hoje = datetime.now()
        clientes_atraso = [item for item in self.dados_contas_receber if datetime.strptime(item[3], "%d/%m/%Y") < hoje]
        
        frame_lista = tk.LabelFrame(self.aba_inadimplencia, text=" Clientes com Títulos em Atraso ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=10)
        
        colunas = ("id", "cliente", "valor", "vencimento")
        self.tree_inad = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        self.tree_inad.heading("id", text="ID")
        self.tree_inad.heading("cliente", text="Cliente Vinculado")
        self.tree_inad.heading("valor", text="Valor Devido")
        self.tree_inad.heading("vencimento", text="Vencimento Original")
        
        self.tree_inad.column("id", width=50, anchor="center")
        self.tree_inad.column("cliente", width=400, anchor="w")
        self.tree_inad.column("valor", width=150, anchor="e")
        self.tree_inad.column("vencimento", width=150, anchor="center")
        
        for item in clientes_atraso:
            self.tree_inad.insert("", "end", values=(item[0], item[1], f"R$ {item[2]:,.2f}", item[3]))
            
        self.tree_inad.pack(side="left", fill="both", expand=True)
        
        btn_cobrar = ttk.Button(self.aba_inadimplencia, text="Disparar Cobrança WhatsApp (Solicitar Número)", command=self.disparar_cobranca_real)
        btn_cobrar.pack(pady=10)

    def disparar_cobranca_real(self):
        selecionado = self.tree_inad.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Por favor, selecione um registro de devedor na tabela acima para cobrar.")
            return
            
        valores = self.tree_inad.item(selecionado, "values")
        id_tit, cliente, valor_devido, data_venc = valores
        
        tel_sugerido = ""
        for ent in self.dados_entidades:
            if ent[2] == cliente:
                tel_sugerido = ent[4]
                break
                
        num_whatsapp = simpledialog.askstring("Contato do Devedor", f"Informe o WhatsApp de '{cliente}' com o DDD:", initialvalue=tel_sugerido)
        
        if num_whatsapp:
            num_limpo = "".join(filter(str.isdigit, num_whatsapp))
            mensagem_codificada = (
                f"Prezado(a) {cliente},\n\n"
                f"Identificamos em nosso sistema administrativo que o título no valor de {valor_devido}, "
                f"com vencimento original em {data_venc}, consta como pendente.\n\n"
                f"Pedimos a gentileza de entrar em contato para regularização da pendência."
            )
            url_api = f"https://web.whatsapp.com/send?phone=55{num_limpo}&text={mensagem_codificada.replace(' ', '%20').replace('\n', '%0A')}"
            webbrowser.open(url_api)
            messagebox.showinfo("Sucesso", "Link de redirecionamento gerado e enviado ao navegador.")

    # =========================================================================
    # METAS FINANCEIRAS
    # =========================================================================
    def renderizar_metas(self):
        for widget in self.aba_metas.winfo_children(): widget.destroy()
        
        faturamento = sum(item[2] for item in self.dados_contas_receber)
        total_despesas = sum(item[2] for item in self.dados_contas_pagar)
        lucro = faturamento - total_despesas
        
        frame_progresso = tk.LabelFrame(self.aba_metas, text=" Progresso das Metas de Gestão ", font=("Arial", 11, "bold"), bg="white", padx=15, pady=15)
        frame_progresso.pack(fill="both", expand=True, padx=10, pady=10)
        
        metas_lista = [
            ("Meta de Faturamento Comercial", faturamento, self.meta_faturamento, "#2f855a"),
            ("Meta de Lucro Líquido Real", lucro, self.meta_lucro, "#2b6cb0"),
            ("Teto de Gastos Operacionais", total_despesas, self.meta_custos, "#c53030")
        ]
        
        for i, (titulo, atual, alvo, cor) in enumerate(metas_lista):
            tk.Label(frame_progresso, text=f"{titulo} (Alvo Definido: R$ {alvo:,.2f})", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=(10, 2))
            
            porcentagem = (atual / alvo) * 100 if alvo > 0 else 0.0
            if "Teto" in titulo:
                porcentagem = 100 - ((atual - alvo) / alvo * 100) if atual > alvo else 100.0
            porcentagem = max(0.0, min(100.0, porcentagem))
            
            pb = ttk.Progressbar(frame_progresso, length=450, mode="determinate")
            pb.pack(fill="x", pady=2)
            pb["value"] = porcentagem
            
            tk.Label(frame_progresso, text=f"Status Atual: R$ {atual:,.2f} ({porcentagem:.1f}%)", font=("Arial", 9, "bold"), fg=cor, bg="white").pack(anchor="w", pady=(0, 10))

if __name__ == "__main__":
    root = tk.Tk()
    app = AppControleFinanceiro(root)
    root.mainloop()