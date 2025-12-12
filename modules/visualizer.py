import networkx as nx
import matplotlib.pyplot as plt
import ast

# --- AST ANALİZCİSİ ---
class CallGraphVisitor(ast.NodeVisitor):
    def __init__(self):
        self.edges = []
        self.defined_funcs = set()
        self.current_func = None

    def visit_FunctionDef(self, node):
        self.defined_funcs.add(node.name)
        prev_func = self.current_func
        self.current_func = node.name
        self.generic_visit(node)
        self.current_func = prev_func

    def visit_Call(self, node):
        if self.current_func:
            func_name = self._get_func_name(node)
            if func_name:
                self.edges.append((self.current_func, func_name))
        self.generic_visit(node)

    def _get_func_name(self, node):
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return "unknown_call"

def create_call_graph(user_scenario, generated_code, metrics):
    """
    Caller -> Callee mantığıyla, Shell Layout (Halka Düzeni) kullanan
    ve üst üste binmeyi %100 engelleyen grafik.
    """
    
    # 1. Kodu Analiz Et
    visitor = CallGraphVisitor()
    try:
        tree = ast.parse(generated_code)
        visitor.visit(tree)
    except SyntaxError:
        pass

    # 2. Grafiği Başlat
    G = nx.DiGraph()

    # --- NODE EKLEME VE GRUPLAMA ---
    # Layout için düğümleri listelere ayırmamız lazım
    scenario_node = "Senaryo"
    defined_nodes = []   # Orta Halka
    external_nodes = []  # Dış Halka

    # Merkez
    G.add_node(scenario_node, node_type='scenario', full_name=user_scenario)

    # Tanımlananlar (Testler)
    for func in visitor.defined_funcs:
        G.add_node(func, node_type='defined', full_name=func)
        G.add_edge(scenario_node, func)
        defined_nodes.append(func)

    # Çağrılanlar (Dış Fonksiyonlar)
    for caller, callee in visitor.edges:
        if caller in visitor.defined_funcs:
            if callee not in G.nodes:
                G.add_node(callee, node_type='external', full_name=callee)
                external_nodes.append(callee)
            G.add_edge(caller, callee)

    # --- ETİKETLERİ KISALTMA ---
    labels = {}
    for node in G.nodes():
        if len(node) > 15:
            labels[node] = node[:13] + ".."
        else:
            labels[node] = node

    # --- GÖRSEL AYARLAR ---
    colors = []
    sizes = []
    
    # Renk ve Boyutları belirlerken sıralamayı G.nodes sırasına göre yapmalıyız
    for node in G.nodes:
        nt = G.nodes[node].get('node_type', 'external')
        if nt == 'scenario':
            colors.append('#FF4B4B') 
            sizes.append(4000) # Merkez daha büyük
        elif nt == 'defined':
            colors.append('#1E90FF') 
            sizes.append(2500)
        else:
            colors.append('#90EE90') 
            sizes.append(1500)

    # Okların değmemesi için suni boyut artırma
    arrow_stop_sizes = [s + 800 for s in sizes] # Boşluğu biraz daha artırdık

    # --- KESİN ÇÖZÜM: SHELL LAYOUT (HALKA DÜZENİ) ---
    # Düğümleri katmanlara ayırıyoruz.
    # 1. Katman: Merkez (Senaryo)
    # 2. Katman: Tanımlanan Testler
    # 3. Katman: Dış Fonksiyonlar
    # NetworkX bu listeleri alır ve her birini ayrı bir çember yapar.
    shells = [[scenario_node], defined_nodes, external_nodes]
    
    pos = nx.shell_layout(G, nlist=shells)
    
    # --- ÇİZİM ---
    # Kare canvas kullanıyoruz ki çember tam yuvarlak olsun
    fig, ax = plt.subplots(figsize=(16, 16))
    
    # 1. Düğümleri Çiz
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=sizes, ax=ax, edgecolors='white', linewidths=2)
    
    # 2. OKLARI ÇİZ
    nx.draw_networkx_edges(
        G, pos, 
        node_size=arrow_stop_sizes, 
        edge_color='#333333',   
        arrows=True, 
        arrowstyle='-|>',       
        arrowsize=25,           
        width=2.0,              
        ax=ax, 
        connectionstyle="arc3,rad=0.2" # Hafif kavis
    )
    
    # 3. Yazıları Çiz
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_color='black', font_weight='bold', ax=ax)

    ax.set_title("Caller -> Callee Akış Şeması (Halka Düzeni)", fontsize=18)
    ax.axis('off')
    fig.patch.set_alpha(0.0)
    
    return fig