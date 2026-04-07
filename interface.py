import tkinter as tk
from tkinter import ttk, messagebox
from compilador import analisar_query
from sgbd import *

class SGBD:
    def __init__(self, root):
        self.root = root
        self.root.title("SGBD do Michael")
        self.root.geometry("800x600")

        try:
            self.tabela_empregados = carregar_dados('empregados.txt')
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar os dados: {e}")
            self.tabela_empregados = []
        
        self.criar_widgets()

    def criar_widgets(self):
        frame_top = tk.Frame(self.root, padx=10, pady=10)
        frame_top.pack(fill=tk.X)

        tk.Label(frame_top, text="Digite sua consulta SQL:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        self.text_query = tk.Text(frame_top, height=4, font=("Arial", 12))
        self.text_query.pack(fill=tk.X, pady=(5, 10))

        btn_executar = tk.Button(frame_top, text="Executar Query", font=("Arial", 12, "bold"), 
                                 bg="#401DAB", fg="white", command=self.processar_query)
        btn_executar.pack(anchor=tk.E)

        frame_bottom = tk.Frame(self.root, padx=10, pady=10)
        frame_bottom.pack(fill=tk.BOTH, expand=True)
        tk.Label(frame_bottom, text="Resultados:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        scroll = tk.Scrollbar(frame_bottom)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(frame_bottom, yscrollcommand=scroll.set, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.tree.yview)

    def processar_query(self):
        query = self.text_query.get("1.0", tk.END).strip()

        if not query:
            messagebox.showwarning("Aviso", "Por favor, digite uma consulta SQL.")
            return
        
        self.tree.delete(*self.tree.get_children())
        resultado_parser = analisar_query(query)

        if isinstance(resultado_parser, str):
            messagebox.showerror("Erro de Sintaxe", resultado_parser)
            return
        
        colunas_select, tabela, filtro_where, order_by, limit_q = resultado_parser

        if tabela.lower() != "empregados":
            messagebox.showerror("Erro", "Tabela desconhecida. Use a tabela 'empregados'.")
            return
        
        resultados = executar_query(self.tabela_empregados, colunas_select, filtro_where, order_by, limit_q)

        if not resultados or len(resultados) == 0:
            messagebox.showinfo("Resultados", "Nenhum resultado encontrado para a consulta.")
            self.tree["columns"] = []
            return
        
        colunas_exibir = list(resultados[0].keys())
        self.tree["columns"] = colunas_exibir

        for col in colunas_exibir:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor = tk.CENTER, width = 100)

        for linha in resultados:
            valores = [linha[col] for col in colunas_exibir]
            self.tree.insert("", tk.END, values=valores)

if __name__ == "__main__":
    janela_principal = tk.Tk()
    app = SGBD(janela_principal)
    janela_principal.mainloop()