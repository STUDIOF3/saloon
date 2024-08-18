from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import sqlite3
from fpdf import FPDF
from PyQt5.QtGui import QIcon
from unidecode import unidecode
from math import ceil  # Importa a função ceil

 

# Conexão com o banco de dados
conn = sqlite3.connect('saloon_recipes.db')
cursor = conn.cursor()

# Criação das tabelas
cursor.execute('''
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    dollar_value REAL DEFAULT 0,
    stock INTEGER DEFAULT 0,
    category TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER,
    name TEXT NOT NULL,
    quantity INTEGER,
    FOREIGN KEY (recipe_id) REFERENCES recipes (id)
)
''')

conn.commit()

class RecipeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Estrela do Oeste')
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        self.initUI()
        self.apply_styles()

    def initUI(self):
        # Cria um layout horizontal para o widget central
        layout = QtWidgets.QHBoxLayout(self.centralWidget())

        # Painel esquerdo para imagem do saloon e barra de busca
        left_panel = QtWidgets.QVBoxLayout()

        # Definindo a largura máxima do painel
        left_panel.setContentsMargins(0, 0, 0, 0)  # Remove margens padrão
        left_panel.setSpacing(10)  # Adiciona algum espaçamento entre os widgets

        # Define o widget do painel e a largura máxima
        left_panel_widget = QtWidgets.QWidget(self)
        left_panel_widget.setLayout(left_panel)
        left_panel_widget.setMaximumWidth(300)  # Define a largura máxima

        # Adiciona o widget do painel ao layout principal
        layout.addWidget(left_panel_widget)

        # Imagem do saloon
        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        pixmap = QtGui.QPixmap("imagens/saloon.jpg")  # Carrega a imagem do saloon
        self.image_label.setPixmap(pixmap.scaled(300, 180, QtCore.Qt.KeepAspectRatio))  # Redimensiona a imagem mantendo a proporção
        self.image_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)  # Permite que a imagem expanda
        self.image_label.setScaledContents(True)  # Ajusta o conteúdo escalado da imagem
        left_panel.addWidget(self.image_label)  # Adiciona a imagem ao painel esquerdo

        # Barra de busca
        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setPlaceholderText('Buscar Receita...')  # Texto de placeholder
        left_panel.addWidget(self.search_bar)  # Adiciona a barra de busca ao painel esquerdo

        # Botão de busca
        self.search_button = QtWidgets.QPushButton(self)
        self.search_button.setIcon(QIcon('imagens\\buscar.png'))  # Ajusta o caminho do ícone
        self.search_button.setIconSize(QtCore.QSize(24, 24))  # Define o tamanho do ícone
        left_panel.addWidget(self.search_button)  # Adiciona o botão de busca ao painel esquerdo

        # Filtro de categoria
        self.category_filter = QtWidgets.QComboBox(self)
        self.category_filter.addItem("Todas")  # Adiciona a opção "Todas"
        self.category_filter.addItems(["Entrada", "Prato Principal", "Doces", "Bebidas Alcolicas", "Sucos", "Salgados", "Sopas"])  # Adiciona outras categorias
        self.category_filter.currentTextChanged.connect(self.load_recipes)  # Conecta a mudança de texto à função de carregar receitas
        left_panel.addWidget(self.category_filter)  # Adiciona o filtro de categoria ao painel esquerdo

        # Adiciona o layout do painel esquerdo ao layout principal
        layout.addLayout(left_panel)

        # Painel direito para lista de receitas e botões
        right_panel = QtWidgets.QVBoxLayout()

        # Lista de receitas
        self.recipe_list = QtWidgets.QListWidget(self)
        self.recipe_list.setStyleSheet('font-size: 14pt;')  # Define o tamanho da fonte da lista
        self.recipe_list.itemClicked.connect(self.show_recipe_options)  # Conecta o clique na lista à função de mostrar opções da receita
        right_panel.addWidget(self.recipe_list)  # Adiciona a lista de receitas ao painel direito

        # Layout para os botões
        buttons_layout = QtWidgets.QHBoxLayout()

        # Botão de adicionar receita
        self.add_button = QtWidgets.QPushButton(self)
        self.add_button.setIcon(QIcon('imagens\\adicionar.png'))  # Ajusta o caminho do ícone
        self.add_button.setIconSize(QtCore.QSize(24, 24))  # Define o tamanho do ícone
        self.add_button.clicked.connect(self.add_recipe_and_ingredients)  # Conecta o clique ao método de adicionar receita e ingredientes
        buttons_layout.addWidget(self.add_button)  # Adiciona o botão de adicionar receita ao layout de botões

        # Botão de relatório
        self.report_button = QtWidgets.QPushButton(self)
        self.report_button.setIcon(QIcon('imagens\\relatorio.png'))  # Ajusta o caminho do ícone
        self.report_button.setIconSize(QtCore.QSize(24, 24))  # Define o tamanho do ícone
        self.report_button.clicked.connect(self.generate_pdf_report)  # Conecta o clique ao método de gerar relatório PDF
        buttons_layout.addWidget(self.report_button)  # Adiciona o botão de relatório ao layout de botões

        # Adiciona o layout de botões ao painel direito
        right_panel.addLayout(buttons_layout)

        # Adiciona o painel direito ao layout principal
        layout.addLayout(right_panel)

        # Carrega as receitas iniciais
        self.load_recipes()

        # Botão de orçamento
        self.budget_button = QtWidgets.QPushButton(self)
        self.budget_button.setIcon(QIcon('imagens\\orcamento.png'))  # Ajuste o caminho do ícone
        self.budget_button.setIconSize(QtCore.QSize(24, 24))  # Define o tamanho do ícone
        self.budget_button.clicked.connect(self.open_budget_dialog)  # Conecta o clique ao método de abrir o diálogo de orçamento
        buttons_layout.addWidget(self.budget_button)  # Adiciona o botão de orçamento ao layout de botões

    def open_budget_dialog(self):
        budget_dialog = BudgetDialog(self)
        budget_dialog.exec_()

    def apply_styles(self):
        style = """
            QMainWindow {
                background-color: #3D5A73;
            }
            QLabel {
                color: #182625;
                font-size: 14pt;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #2F3D40;
                color: #ffffff;
                border: 1px solid #2F3D40;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #28403D;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7c7c7c;
            }
            QListWidget {
                background-color: #2F3D40;
                color: #ffffff;
                border: 1px solid #5c5c5c;
            }
        """
        self.setStyleSheet(style)

    def load_recipes(self):
        self.recipe_list.clear()
        category = self.category_filter.currentText()
        if category == "Todas":
            cursor.execute("SELECT id, name, dollar_value, stock, category FROM recipes")
        else:
            cursor.execute("SELECT id, name, dollar_value, stock, category FROM recipes WHERE category = ?", (category,))
        for row in cursor.fetchall():
            item = QtWidgets.QListWidgetItem(f"{row[1].upper()} - ${row[2]:.2f} (Estoque: {row[3]}) - Categoria: {row[4]}")
            item.setData(QtCore.Qt.UserRole, row[0])
            self.recipe_list.addItem(item)

    def search_recipe(self):
        search_term = self.search_bar.text()
        self.recipe_list.clear()
        cursor.execute("SELECT id, name, dollar_value, stock, category FROM recipes WHERE name LIKE ?", ('%' + search_term + '%',))
        for row in cursor.fetchall():
            item = QtWidgets.QListWidgetItem(f"{row[1].upper()} - ${row[2]:.2f} (Estoque: {row[3]}) - Categoria: {row[4]}")
            item.setData(QtCore.Qt.UserRole, row[0])
            self.recipe_list.addItem(item)

    def add_recipe_and_ingredients(self):
        name, ok = QtWidgets.QInputDialog.getText(self, 'Receita', 'Digite nome do prato/comida:')
        if ok and name:
            dollar_value, ok = QtWidgets.QInputDialog.getDouble(self, 'Valor', 'Preço do prato:', decimals=2)
            if ok:
                stock, ok = QtWidgets.QInputDialog.getInt(self, 'Estoque', 'Quantidade em Estoque:')
                if ok:
                    categories = ["Entrada", "Prato Principal", "Doces", "Bebidas Alcolicas", "Sucos", "Salgados", "Sopas"]
                    category, ok = QtWidgets.QInputDialog.getItem(self, "Categoria", "Escolha a categoria da receita:", categories, 0, False)
                    if ok and category:
                        cursor.execute("INSERT INTO recipes (name, dollar_value, stock, category) VALUES (?, ?, ?, ?)", (name, dollar_value, stock, category))
                        conn.commit()
                        recipe_id = cursor.lastrowid
                        self.load_recipes()
                        self.edit_recipe(recipe_id)

    def edit_recipe(self, recipe_id):
        edit_dialog = EditRecipeDialog(self, recipe_id)
        if edit_dialog.exec_():
            self.load_recipes()

    def show_recipe_options(self, item):
        recipe_id = item.data(QtCore.Qt.UserRole)
        menu = QtWidgets.QMenu(self)
        edit_action = menu.addAction('Editar')
        delete_action = menu.addAction('Deletar')
        calculate_action = menu.addAction('Calcular Ingredientes')
        action = menu.exec_(QtGui.QCursor.pos())
        if action == edit_action:
            self.edit_recipe(recipe_id)
        elif action == delete_action:
            self.delete_recipe(recipe_id)
        elif action == calculate_action:
            self.calculate_ingredients(recipe_id)

    def delete_recipe(self, recipe_id):
        cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        cursor.execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe_id,))
        conn.commit()
        self.load_recipes()

    def calculate_ingredients(self, recipe_id):
        cursor.execute("SELECT name, quantity FROM ingredients WHERE recipe_id = ?", (recipe_id,))
        ingredients = cursor.fetchall()
        if ingredients:
            quantity, ok = QtWidgets.QInputDialog.getInt(self, 'Quantidade', 'Quantidade de Pratos:')
            if ok:
                calculated_ingredients = [(name, ceil(quantity / 5) * qty) for name, qty in ingredients]
                calculate_dialog = CalculateDialog(self, calculated_ingredients)
                calculate_dialog.exec_()
        else:
            QtWidgets.QMessageBox.information(self, 'Erro', 'Nenhum ingrediente encontrado para esta receita.')

    def generate_pdf_report(self):
        cursor.execute("SELECT id, name, stock FROM recipes")
        recipes = cursor.fetchall()
        total_ingredients = {}

        for recipe in recipes:
            recipe_id = recipe[0]
            stock = recipe[2]
            cursor.execute("SELECT name, quantity FROM ingredients WHERE recipe_id = ?", (recipe_id,))
            ingredients = cursor.fetchall()
            for name, quantity in ingredients:
                if name not in total_ingredients:
                    total_ingredients[name] = 0
                total_ingredients[name] += (quantity / 5) * stock  # Usando a mesma fórmula de cálculo da função calculate_ingredients

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for ingredient, total_quantity in total_ingredients.items():
            pdf.cell(200, 10, txt=f"{ingredient}: {ceil(total_quantity)}", ln=True)

        pdf.output("Lista de Compras.pdf")
        QtWidgets.QMessageBox.information(self, 'Relatório Gerado', 'Relatório de ingredientes gerado com sucesso.')

class EditRecipeDialog(QtWidgets.QDialog):
    def __init__(self, parent, recipe_id):
        super().__init__(parent)
        self.setWindowTitle('Editar Receita')
        self.setGeometry(100, 100, 400, 300)
        self.recipe_id = recipe_id
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Recipe name
        cursor.execute("SELECT name, dollar_value, stock, category FROM recipes WHERE id = ?", (self.recipe_id,))
        recipe = cursor.fetchone()
        self.name_edit = QtWidgets.QLineEdit(recipe[0], self)
        layout.addWidget(QtWidgets.QLabel('Nome da Receita:'))
        layout.addWidget(self.name_edit)

        # Dollar value
        self.dollar_value_edit = QtWidgets.QDoubleSpinBox(self)
        self.dollar_value_edit.setDecimals(2)
        self.dollar_value_edit.setValue(recipe[1])
        layout.addWidget(QtWidgets.QLabel('Preço do Prato:'))
        layout.addWidget(self.dollar_value_edit)

        # Stock
        self.stock_edit = QtWidgets.QSpinBox(self)
        self.stock_edit.setMaximum(100000)  # Define o valor máximo para o estoque
        self.stock_edit.setValue(recipe[2])
        layout.addWidget(QtWidgets.QLabel('Quantidade em Estoque:'))
        layout.addWidget(self.stock_edit)

        # Category
        self.category_edit = QtWidgets.QComboBox(self)
        self.category_edit.addItems(["Entrada", "Prato Principal", "Doces", "Bebidas Alcolicas", "Sucos", "Salgados", "Sopas"])
        self.category_edit.setCurrentText(recipe[3])
        layout.addWidget(QtWidgets.QLabel('Categoria:'))
        layout.addWidget(self.category_edit)

        # Ingredients
        self.ingredients_list = QtWidgets.QListWidget(self)
        layout.addWidget(QtWidgets.QLabel('Ingredientes:'))
        layout.addWidget(self.ingredients_list)
        self.load_ingredients()

        # Add ingredient
        add_ingredient_layout = QtWidgets.QHBoxLayout()
        self.new_ingredient_edit = QtWidgets.QLineEdit(self)
        add_ingredient_layout.addWidget(self.new_ingredient_edit)

        # Ingredient suggestions
        cursor.execute("SELECT DISTINCT name FROM ingredients")
        ingredient_names = [row[0] for row in cursor.fetchall()]
        completer = QtWidgets.QCompleter(ingredient_names)
        self.new_ingredient_edit.setCompleter(completer)

        self.new_ingredient_quantity_edit = QtWidgets.QSpinBox(self)
        self.new_ingredient_quantity_edit.setMinimum(1)
        add_ingredient_layout.addWidget(self.new_ingredient_quantity_edit)
    
        add_ingredient_button = QtWidgets.QPushButton('Adicionar', self)
        add_ingredient_button.clicked.connect(self.add_ingredient)
        add_ingredient_layout.addWidget(add_ingredient_button)
        layout.addLayout(add_ingredient_layout)

        # Delete ingredient
        delete_ingredient_button = QtWidgets.QPushButton('Deletar Ingrediente', self)
        delete_ingredient_button.clicked.connect(self.delete_ingredient)
        layout.addWidget(delete_ingredient_button)

        # Save and Cancel buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        save_button = QtWidgets.QPushButton('Salvar', self)
        save_button.clicked.connect(self.save_recipe)
        buttons_layout.addWidget(save_button)

        cancel_button = QtWidgets.QPushButton('Cancelar', self)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

    def load_ingredients(self):
        self.ingredients_list.clear()
        cursor.execute("SELECT id, name, quantity FROM ingredients WHERE recipe_id = ?", (self.recipe_id,))
        for row in cursor.fetchall():
            item = QtWidgets.QListWidgetItem(f"{row[1]} - {row[2]}")
            item.setData(QtCore.Qt.UserRole, row[0])
            self.ingredients_list.addItem(item)

    def add_ingredient(self):
        name = self.new_ingredient_edit.text()
        quantity = self.new_ingredient_quantity_edit.value()
        cursor.execute("INSERT INTO ingredients (recipe_id, name, quantity) VALUES (?, ?, ?)", (self.recipe_id, name, quantity))
        conn.commit()
        self.load_ingredients()
        # Limpar os campos de entrada após adicionar o ingrediente
        self.new_ingredient_edit.clear()
        self.new_ingredient_quantity_edit.setValue(1)

    def delete_ingredient(self):
        selected_item = self.ingredients_list.currentItem()
        if selected_item:
            ingredient_id = selected_item.data(QtCore.Qt.UserRole)
            cursor.execute("DELETE FROM ingredients WHERE id = ?", (ingredient_id,))
            conn.commit()
            self.load_ingredients()

    def save_recipe(self):
        name = self.name_edit.text()
        dollar_value = self.dollar_value_edit.value()
        stock = self.stock_edit.value()
        category = self.category_edit.currentText()
        cursor.execute("UPDATE recipes SET name = ?, dollar_value = ?, stock = ?, category = ? WHERE id = ?", (name, dollar_value, stock, category, self.recipe_id))
        conn.commit()
        self.accept()

class CalculateDialog(QtWidgets.QDialog):
    def __init__(self, parent, ingredients):
        super().__init__(parent)
        self.setWindowTitle('Ingredientes Calculados')
        self.setGeometry(100, 100, 300, 200)
        self.ingredients = ingredients
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        for name, qty in self.ingredients:
            layout.addWidget(QtWidgets.QLabel(f"{name}: {qty}"))
        close_button = QtWidgets.QPushButton('Fechar', self)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

class BudgetDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Gerar Orçamento')
        self.setGeometry(100, 100, 400, 300)
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Lista de receitas para selecionar
        self.recipe_selection = QtWidgets.QListWidget(self)
        cursor.execute("SELECT id, name, dollar_value FROM recipes")
        for row in cursor.fetchall():
            item = QtWidgets.QListWidgetItem(f"{row[1]} - ${row[2]:.2f}")
            item.setData(QtCore.Qt.UserRole, row)
            self.recipe_selection.addItem(item)
        layout.addWidget(self.recipe_selection)

        # Input de quantidade
        quantity_layout = QtWidgets.QHBoxLayout()
        self.quantity_input = QtWidgets.QSpinBox(self)
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(100000)
        quantity_layout.addWidget(QtWidgets.QLabel('Quantidade:'))
        quantity_layout.addWidget(self.quantity_input)
        layout.addLayout(quantity_layout)

        # Botão para adicionar ao orçamento
        add_button = QtWidgets.QPushButton('Adicionar ao Orçamento', self)
        add_button.clicked.connect(self.add_to_budget)
        layout.addWidget(add_button)

        # Lista de itens do orçamento
        self.budget_list = QtWidgets.QListWidget(self)
        layout.addWidget(self.budget_list)

        # Botão para remover do orçamento
        remove_button = QtWidgets.QPushButton('Remover do Orçamento', self)
        remove_button.clicked.connect(self.remove_from_budget)
        layout.addWidget(remove_button)

        # Botão para gerar PDF
        generate_pdf_button = QtWidgets.QPushButton('Gerar PDF do Orçamento', self)
        generate_pdf_button.clicked.connect(self.generate_budget_pdf)
        layout.addWidget(generate_pdf_button)

        # Botões de fechar e cancelar
        buttons_layout = QtWidgets.QHBoxLayout()
        close_button = QtWidgets.QPushButton('Fechar', self)
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        layout.addLayout(buttons_layout)

        self.budget_items = []

    def add_to_budget(self):
        selected_item = self.recipe_selection.currentItem()
        if selected_item:
            recipe_data = selected_item.data(QtCore.Qt.UserRole)
            quantity = self.quantity_input.value()
            total_price = recipe_data[2] * quantity
            budget_item = (recipe_data[1], quantity, total_price)
            self.budget_items.append(budget_item)
            self.budget_list.addItem(f"{recipe_data[1]} x{quantity} - ${total_price:.2f}")

    def remove_from_budget(self):
        selected_item = self.budget_list.currentItem()
        if selected_item:
            # Remove da lista de itens de orçamento
            item_text = selected_item.text()
            for item in self.budget_items:
                if item_text.startswith(item[0]):
                    self.budget_items.remove(item)
                    break
            # Remove da lista visual
            self.budget_list.takeItem(self.budget_list.row(selected_item))

    def generate_budget_pdf(self):
        if not self.budget_items:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Nenhum item no orçamento.')
            return

        total_value = sum(item[2] for item in self.budget_items)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Orçamento", ln=True, align="C")
        pdf.cell(200, 10, txt="", ln=True)  # Linha em branco

        for item in self.budget_items:
            pdf.cell(200, 10, txt=f"{item[0]} x{item[1]} - ${item[2]:.2f}", ln=True)

        pdf.cell(200, 10, txt="", ln=True)  # Linha em branco
        pdf.cell(200, 10, txt=f"Total: ${total_value:.2f}", ln=True, align="R")

        pdf.output("Orçamento.pdf")
        QtWidgets.QMessageBox.information(self, 'Relatório Gerado', 'Orçamento gerado com sucesso.')



def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = RecipeApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()