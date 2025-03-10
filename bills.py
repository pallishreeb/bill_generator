import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from ui_components import generate_bill_tab, display_bills_tab, manage_clients_tab, manage_products_tab

def main():
    root = tk.Tk()
    root.title("Invoice Generator")
    root.geometry("900x600")
    
    style = Style(theme="cosmo")
    
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')
    
    generate_tab = tk.Frame(notebook)
    display_tab = tk.Frame(notebook)
    clients_tab = tk.Frame(notebook)
    products_tab = tk.Frame(notebook)

    notebook.add(generate_tab, text="Generate Bill")
    notebook.add(display_tab, text="Display Bills")
    notebook.add(clients_tab, text="Manage Clients")
    notebook.add(products_tab, text="Manage Products")
    
    # Load UI Components
    generate_bill_tab(generate_tab)
    display_bills_tab(display_tab)
    manage_clients_tab(clients_tab)
    manage_products_tab(products_tab)
    
    root.mainloop()

if __name__ == "__main__":
    main()
