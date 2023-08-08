import curses
import ctypes
import random
from time import sleep
import locale
import pandas as pd
from operator import itemgetter

global prision, players_info, players
prision = {}
players_info = {}
players = []
final_standing = {}
titulos = pd.read_csv('data/titulos.csv')
titulos.set_index('Posição')
companhias = pd.read_csv('data/companhias.csv')
companhias.set_index('Posição')

def return_false(stdscr, pl, dice):
    return False

def get_card(stdscr, pl, dice):
    global players, players_info
    win_card = get_max_window(stdscr)
    values = [10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]
    par = values[random.randint(0, 9)]
    impar = values[random.randint(0, 9)]
    f_par = str_to_money(par)
    f_impar = str_to_money(impar)
    message_par = f'Sorte: se a soma dos dados for um número par, receba {f_par}'
    message_impar = f'Revés: se a soma dos dados for um número impar, pague {f_impar}'
    win_center_message(win_card, message_par)
    win_center_message(win_card, message_impar)
    if dice % 2 == 0:
        players_info[pl]['caixa'] += par 
        saldo = str_to_money(players_info[pl]['caixa'])
        message = f'{pl} recebeu {f_par}. Seu saldo agora é de {saldo}'
        win_center_message(win_card, message, 3)
    else:
        if pay(win_card, stdscr, pl, impar) == True:
            players_info[pl]['caixa'] -= impar 
            saldo = str_to_money(players_info[pl]['caixa'])
            message = f'{pl} pagou {f_impar}. Seu saldo agora é de {saldo}'
            win_center_message(win_card, message, 3)
        else:
            bankrup(win_card, pl, impar)

def prision_visit(stdscr, pl, dice):
    win_prision = get_max_window(stdscr)
    win_center_message(win_prision, f'{pl} visitou a detenção.')

def go_to_prision(stdscr, pl, dice):
    global prision, players, players_info
    prision[pl] = 0
    players_info[pl]['boardPosition'] = 10
    win_prision = get_max_window(stdscr)
    win_center_message(win_prision, 'Entre no camborão e vá para a detenção.')
    win_center_message(win_prision, f'{pl} não poderá mover pelas próximas duas rodadas.')

def pay_value(stdscr, pl, dice):
    global players, players_info
    win_pay = get_max_window(stdscr)
    value = 200000
    if pay(win_pay, stdscr, pl, value) == True:
        players_info[pl]['caixa'] -= value
        money = str_to_money(value)
        win_center_message(win_pay, f'{pl} pagou {money} do Imposto de Renda', 3)
    else:
        bankrup(win_pay, pl, value)

def get_money(stdscr, pl, dice):
    global players, players_info
    players_info[pl]['caixa'] += 200000
    money = str_to_money(200000)
    win_pay = get_max_window(stdscr)
    win_center_message(win_pay, f'{pl} recebeu {money} de Restituição do Imposto de Renda', 3)

locale.setlocale(locale.LC_ALL, '')  # Utiliza a configuração padrão do sistema
BOARD = ['INICIO', 'Jardim Botânico', 'Avenida Niemeyer','Companhia Petrolífera', 'Avenida Beira-Mar', 'Avenida Juscelino Kubitschek', 'Sorte ou Revés', 'Rua Oscar Freire', 'Restituição do Imposto de Renda', 'Avenida Ibirapuera', 'Cadeia', 'Sorte ou Revés', 'Praça da Sé', 'Rua da Consolação', 'Central de Força e Luz', 'Viaduto do Chá', 'Receita Federal', 'Higienópolis', 'Jardins', 'Avenida São João', 'Livre', 'Avenida Ipiranga', 'Companhia de Água e Saneamento', 'Companhia de Mineração', 'Sorte ou Revés', 'Avenida Recife', 'Avenida Paulista', 'Sorte ou Revés', 'Ponte do Guaiba', 'Pontocom', 'Vá para a cadeia', 'Praça dos Três Poderes', 'Sorte ou Revés', 'Praça Castro Alves', 'Avenida do Contorno', 'Ponte Rio-Niterói', 'Crédito de Carbono', 'Barra da Tijuca', 'Sorte ou Revés', 'Marina da Glória']
BOARD_FUNCTIONS = {
    'INICIO': return_false,
    'Sorte ou Revés': get_card,
    'Restituição do Imposto de Renda': get_money,
    'Cadeia': prision_visit,
    'Receita Federal': pay_value,
    'Vá para a cadeia': go_to_prision,
    'Livre': return_false
}


def get_nvda():
    nvda_dll = ctypes.CDLL("./nvda.dll")
    speak = nvda_dll.nvdaController_speakText
    nvda_silence = nvda_dll.nvdaController_cancelSpeech
    
    return nvda_silence, speak

def print_menu(stdscr, selected_row_idx, options, message):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    if message:
        title_x = width//2 - len(message)//2
        title_y = y = height//2 - len(options)//2 - 1
        stdscr.addstr(title_y, title_x, message)

    NVDA_SPEAK(options[selected_row_idx])

    for idx, option in enumerate(options):
        x = width//2 - len(option)//2
        y = height//2 - len(options)//2 + idx + 1
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.insstr(y, x, option)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, option)

    stdscr.refresh()

def newMenu(stdscr, options, message = False, nvda_message = False):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    current_row_idx = 0
    if nvda_message:
        NVDA_SPEAK(nvda_message)
    elif message != False and nvda_message == False:
        NVDA_SPEAK(message)
    print_menu(stdscr, current_row_idx, options, message)

    while True:
        key = stdscr.getch()
        stdscr.clear()
        NVDA_SILENCE()
        if key == curses.KEY_UP:
            if current_row_idx > 0:
                current_row_idx -= 1
            else:
                current_row_idx = len(options) - 1
        elif key == curses.KEY_DOWN: 
            if current_row_idx < len(options)-1:
                current_row_idx += 1
            else:
                current_row_idx = 0
        elif key == ord('\n'):
            return options[current_row_idx]
        elif key == ord('q'):
            break
        
        # NVDA_SPEAK(options[current_row_idx])
        print_menu(stdscr, current_row_idx, options, message)

def get_max_window(stdscr):
    height, width = stdscr.getmaxyx()
    win = curses.newwin(height, width, 0, 0)
    win.clear()

    return win

def win_center_message(win, message, time_sleep = 5, y_ajust = 0, nvda_message = False):
    if nvda_message == False:
        nvda_message = message
    win.clear()
    height, width = win.getmaxyx()
    x = width//2 - len(message)//2
    y = height//2 - y_ajust
    win.addstr(y, x, message)
    NVDA_SPEAK(nvda_message)
    win.refresh()
    sleep(time_sleep)

def center_message(stdscr, message, y_ajust = 0, nvda_message = False):
    if nvda_message == False:
        nvda_message = message
    height, width = stdscr.getmaxyx()
    x = width//2 - len(message)//2
    y = height//2 - y_ajust
    stdscr.addstr(y, x, message)
    NVDA_SPEAK(nvda_message)
    stdscr.refresh()

def insert_user_input(win, message, only_num = False):
    curses.curs_set(1)
    height, width = win.getmaxyx()
    x = width//2 - len(message)//2
    y = height//2
    win.addstr(y-1, x, message)
    win.refresh()
    curses.echo()
    if only_num == True:
        while True:
            win.clear()
            win.addstr(y-1, x, message)
            win.refresh()
            curses.echo()
            input_str = win.getstr(y, x, 20).decode('utf-8')
            if input_str.isdigit():  # Verifica se a entrada é composta apenas de dígitos
                break
            else:
                curses.beep()
                win_center_message(win, 'Digite apenas números')
    else:
        input_str = win.getstr(y, x, 20).decode('utf-8')
    curses.noecho()
    curses.curs_set(0)

    return input_str

def getBoardPosition(game_win, position, dice, pl):
    global players, players_info
    total = position + dice
    qtd = len(BOARD) 
    if total < qtd:
        return total, total
    else:
        money = str_to_money(200000)
        players_info[pl]['caixa'] += 200000
        new_balance = str_to_money(players_info[pl]['caixa'])
        win_center_message(game_win, f'{pl} ganhou {money}. Seu saldo agora é de {new_balance}')
        newPosition = qtd - position
        newPosition = dice - newPosition
        return newPosition, newPosition

def showInfo(stdscr, space_content, board_space):
    space_info = []
    for key, value in space_content.items():
        ft_value = value
        if type(ft_value) == int or type(ft_value) == float:
            f_value = str_to_money(ft_value)
        else:
            f_value = ft_value
        space_info.append(f'{key}: {f_value}')
    option_selected = newMenu(stdscr, space_info, f'Informações de {board_space} (Aperte Enter para voltar a outra tela)')

def show_properties(game_win, stdscr, pl):
    properties = []
    qtd = titulos['Dono'] == pl
    if sum(qtd) > 0:
        df_prop = titulos.loc[titulos['Dono'] == pl, ['Propriedade', 'Cor']]
        properties = [f'{propriedade} ({cor})' for propriedade, cor in zip(df_prop['Propriedade'], df_prop['Cor'])]
        return properties
    else:
        return False

def show_companies(game_win, stdscr, pl):
    companies = []
    qtd = companhias['Dono'] == pl
    if sum(qtd) > 0:
        def_comp = companhias.loc[companhias['Dono'] == pl, ['Companhia']]
        companies = [f'{companhia}' for companhia in def_comp['Companhia']]
        return companies
    else:
        return False

def new_dice(game_win):
    game_win.clear()
    win_center_message(game_win, 'Rolando os dados...', 1)
    dice_1 = random.randint(1, 6)
    dice_2 = random.randint(1, 6)
    game_win.clear()
    win_center_message(game_win, f'Os números {dice_1} e {dice_2} foram sorteados', 1)
    dice = dice_1 + dice_2

    return dice

def forced_dice(game_win, dice_1, dice_2):
    game_win.clear()
    win_center_message(game_win, 'Rolando os dados...', 1)
    game_win.clear()
    win_center_message(game_win, f'Os números {dice_1} e {dice_2} foram sorteados', 1)
    dice = dice_1 + dice_2

    return dice

def buy(game_win, space_value, new_position, board_space, pl):
    global players, players_info
    players_info[pl]['caixa'] -= space_value
    if board_space in titulos['Propriedade'].values:
        titulos.loc[titulos['Posição'] == new_position, 'Dono'] = pl
    else:
        companhias.loc[companhias['Posição'] == new_position, 'Dono'] = pl
    game_win.clear()
    new_balance = str_to_money(players_info[pl]['caixa'])
    message =f'{pl} comprou {board_space}. Seu saldo agora é de {new_balance}'
    win_center_message(game_win, message)

def pay(game_win, stdscr, pl, value):
    global players, players_info
    while True:
        caixa = players_info[pl]['caixa']
        if value > caixa:
            options = []
            deficit = value - caixa
            properties = titulos.loc[(titulos['Dono'] == pl) & (titulos['Hipotecada'] == 0), ['Propriedade', 'Hipoteca']]
            count_properties = len(properties)
            value_prop = properties['Hipoteca'].sum()
            companies = companhias.loc[(companhias['Dono'] == pl) & (companhias['Hipotecada'] == 0), ['Companhia', 'Hipoteca']]
            count_companies = len(companies)
            value_comp = companies['Hipoteca'].sum()
            total_value = value_comp + value_prop
            if total_value > deficit:
                win_center_message(game_win, f'Seu saldo atual não é suficiente para pagar toda a sua dívida.')
                win_center_message(game_win, f'Consiga pelo menos {str_to_money(deficit)} hipotecando propriedades.')
                if count_properties > 0:
                    options.append('Minhas Propriedades')
                    prop_menu = [f'{propriedade}' for propriedade in properties['Propriedade']]
                if count_companies > 0:
                    options.append('Minhas Companhias')
                    comp_menu = [f'{companhia}' for companhia in companies['Companhia']]
                option = newMenu(stdscr, options, 'Escolha alguma propriedade ou companhia para hipotecar')
                if option == 'Minhas Propriedades':
                    manage_properties(game_win, stdscr, prop_menu, pl)
                elif option == 'Minhas Companhias':
                    manage_companies(game_win, stdscr, comp_menu, pl)
            else:
                return False

        else:
            return True

def bankrup(game_win, pl, value, receiver = False):
    global players, players_info, final_standing
    if receiver == False:
        titulos.loc[titulos['Dono'] == pl, 'Hipotecada'] = 0
        titulos.loc[titulos['Dono'] == pl, 'Dono'] = pd.NA
        companhias.loc[companhias['Dono'] == pl, 'Hipotecada'] = 0
        companhias.loc[companhias['Dono'] == pl, 'Dono'] = pd.NA
        del players_info[pl]
        players.remove(pl)  
    else: 
        titulos.loc[titulos['Dono'] == pl, 'Hipotecada'] = 0
        titulos.loc[titulos['Dono'] == pl, 'Dono'] = receiver
        companhias.loc[companhias['Dono'] == pl, 'Hipotecada'] = 0
        companhias.loc[companhias['Dono'] == pl, 'Dono'] = receiver
        players.remove(pl) 
    final_standing[pl] = players_info['caixa'][pl] - value
    win_center_message(game_win, f'{pl} está falido!')

def balance_change(value, payer, receiver):
    global players, players_info
    players_info[payer]['caixa'] -= value
    players_info[receiver]['caixa'] += value

def infos_in_name(name, color):
    prop = f'{name} (Cor: {color})'

    return prop

def get_property_by_name(name):
    df = titulos[titulos['Propriedade'] == name]
    final_df = df.iloc[0].to_dict()

    return final_df

def get_properties_by_player(player):
    df = titulos[titulos['Dono'] == player]
    final_df = df[df['Hipotecada'] == 0]
    propriedade = [f'{propriedade} (Cor: {cor}, Valor:  {str_to_money(valor)})' for propriedade, cor, valor in zip(final_df['Propriedade'], final_df['Cor'], final_df['Preço'])]

    return propriedade

def get_company_by_name(name):
    df = companhias[companhias['Companhia'] == name]
    final_df = df.iloc[0].to_dict()

    return final_df

def get_companies_by_player(player):
    df = companhias[companhias['Dono'] == player]
    final_df = df[df['Hipotecada'] == 0]
    companies = [f'{companhia} ( {str_to_money(valor)})' for companhia, valor in zip(final_df['Companhia'], final_df['Preço'])]

    return companies

def manage_properties(game_win, stdscr, properties, pl):
    option_selected = newMenu(stdscr, properties, f'Propriedades de {pl}')
    prop = option_selected.split(' (')[0]
    prop_menu = ['Ver informações']
    property = get_property_by_name(prop)
    hipotecada = property['Hipotecada']
    if hipotecada == 1:
        prop_menu.append('Retirar Hipoteca')
    else:
        prop_menu.append('Hipotecar Propriedade')
    prop_menu.append('Voltar')
    option = newMenu(stdscr, prop_menu, f'{option_selected}')
    if option == 'Hipotecar Propriedade':
        propriedade_hipoteca(game_win, stdscr, property, pl)
    elif option == 'Retirar Hipoteca':
        propriedade_retirar_hipoteca(game_win, stdscr, property, pl)
    elif option == 'Ver informações':
        del property['Dono']
        del property['Ativo']
        del property['Posição']
        del property['Hipotecada']
        del property['Propriedade']
        showInfo(stdscr, property, prop)

def propriedade_hipoteca(game_win, stdscr, property, pl):
    global players, players_info
    options = ['Sim', 'Não']
    prop = property['Propriedade']
    valor_recebido = str_to_money(property['Hipoteca'])
    option = newMenu(stdscr, options, f'Deseja hipotecar {prop} e receber {valor_recebido}?')
    if option == 'Sim':
        players_info[pl]['caixa'] += property['Hipoteca']
        novo_saldo = str_to_money(players_info[pl]['caixa'])
        titulos.loc[titulos['Propriedade'] == prop, 'Hipotecada'] = 1
        win_center_message(game_win, f'{pl} hipotecou {prop} e recebeu  {valor_recebido}')
        win_center_message(game_win, f'O novo saldo de {pl} é  {novo_saldo}')
        win_center_message(game_win, f'Não será recebido aluguéis de {prop} enquanto essa propriedade estiver hipotecada')
    else:
        return False
    
def propriedade_retirar_hipoteca(game_win, stdscr, property, pl):
    global players, players_info
    options = ['Sim', 'Não']
    prop = property['Propriedade']
    valor_recebido = str_to_money(property['Hipoteca'])
    option = newMenu(stdscr, options, f'Deseja retirar a Hipoteca de {prop} e pagar  {valor_recebido}?')
    if option == 'Sim':
        players_info[pl]['caixa'] -= property['Hipoteca']
        novo_saldo = str_to_money(players_info[pl]['caixa'])
        titulos.loc[titulos['Propriedade'] == prop, 'Hipotecada'] = 0
        win_center_message(game_win, f'{pl} retirou a hipoteca de {prop} e pagou  {valor_recebido}')
        win_center_message(game_win, f'O novo saldo de {pl} é  {novo_saldo}')
        win_center_message(game_win, f'{prop} pode ser evoluida e receber aluguéis novamente')
    else:
        return False

def manage_companies(game_win, stdscr, companies, pl):
    option_selected = newMenu(stdscr, companies, f'Companhias de {pl}')
    comp = option_selected.split(' (')[0]
    comp_menu = ['Ver informações']
    company = get_company_by_name(comp)
    hipotecada = company['Hipotecada']
    if hipotecada == 1:
        comp_menu.append('Retirar Hipoteca')
    else:
        comp_menu.append('Hipotecar Companhia')
    comp_menu.append('Voltar')
    option = newMenu(stdscr, comp_menu, f'{option_selected}')
    if option == 'Hipotecar Companhia':
        companhia_hipoteca(game_win, stdscr, company, pl)
    elif option == 'Retirar Hipoteca':
        companhia_retirar_hipoteca(game_win, stdscr, company, pl)
    elif option == 'Ver informações':
        del company['Dono']
        del company['Ativo']
        del company['Posição']
        del company['Hipotecada']
        del company['Companhia']
        showInfo(stdscr, company, comp)

def companhia_hipoteca(game_win, stdscr, company, pl):
    global players, players_info
    options = ['Sim', 'Não']
    comp = company['Procompany']
    valor_recebido = str_to_money(company['Hipoteca'])
    option = newMenu(stdscr, options, f'Deseja hipotecar {comp} e receber {valor_recebido}?')
    if option == 'Sim':
        players_info[pl]['caixa'] += company['Hipoteca']
        novo_saldo = str_to_money(players_info[pl]['caixa'])
        companhias.loc[companhias['Companhia'] == comp, 'Hipotecada'] = 1
        win_center_message(game_win, f'{pl} hipotecou {comp} e recebeu  {valor_recebido}')
        win_center_message(game_win, f'O novo saldo de {pl} é  {novo_saldo}')
        win_center_message(game_win, f'Não será recebido aluguéis de {comp} enquanto essa propriedade estiver hipotecada')
    else:
        return False
    
def companhia_retirar_hipoteca(game_win, stdscr, company, pl):
    global players, players_info
    options = ['Sim', 'Não']
    comp = company['Companhia']
    valor_recebido = str_to_money(company['Hipoteca'])
    option = newMenu(stdscr, options, f'Deseja retirar a Hipoteca de {comp} e pagar  {valor_recebido}?')
    if option == 'Sim':
        players_info[pl]['caixa'] -= company['Hipoteca']
        novo_saldo = str_to_money(players_info[pl]['caixa'])
        companhias.loc[companhias['Companhia'] == comp, 'Hipotecada'] = 0
        win_center_message(game_win, f'{pl} retirou a hipoteca de {comp} e pagou  {valor_recebido}')
        win_center_message(game_win, f'O novo saldo de {pl} é  {novo_saldo}')
        win_center_message(game_win, f'{comp} pode ser evoluida e receber aluguéis novamente')
    else:
        return False

def make_deal(game_win, stdscr, pl, players_with_real_estate):
    global players, players_info
    options = []
    for p in players_with_real_estate:
        if p != pl:
            op_properties = (titulos['Dono'] == p) & (titulos['Hipotecada'] == 0)
            opc = sum(op_properties)
            op_companies = (companhias['Dono'] == p) & (companhias['Hipotecada'] == 0)
            occ = sum(op_companies)
            if opc > 0 or occ > 0:
                options.append(p)
    
    seller = newMenu(stdscr, options, f'Para quem você deseja fazer proposta?')
    seller_properties = (titulos['Dono'] == seller) & (titulos['Hipotecada'] == 0)
    op_properties = sum(seller_properties)
    seller_companies = (companhias['Dono'] == seller) & (companhias['Hipotecada'] == 0)
    op_companies = sum(seller_companies)
    options = []
    options.append('Cancelar Oferta')
    options.append('Continuar')
    deal_prop = []
    deal_comp = []
    
    while True:
        game_win.clear()
        if op_companies > 0 and 'Adicionar Companhia' not in options:
            options.insert(0, 'Adicionar Companhia')
            seller_companies = get_companies_by_player(seller)
            seller_companies.append('Voltar')
        elif op_companies == 0 and 'Adicionar Companhia' in options:
            options.remove('Adicionar Companhia')

        if op_properties > 0 and 'Adicionar Propriedade' not in options:
            options.insert(0, 'Adicionar Propriedade')
            seller_properties = get_properties_by_player(seller)
            seller_properties.append('Voltar')
        elif op_properties == 0 and 'Adicionar Propriedade' in options:
            options.remove('Adicionar Propriedade')

        option = newMenu(stdscr, options, f'Selecione companhias ou propriedades que você tenha interesse em adquirir de {seller}')
        opt = option.split(' ')[0]
        imovel = option.replace('Remover ', '')
        if option == 'Adicionar Propriedade':
            prop = newMenu(stdscr, seller_properties, 'Qual propriedade você gostaria de adicionar?')
            if prop != 'Voltar':
                deal_prop.append(prop)
                options.insert(0, f'Remover {prop}')
                seller_properties.remove(prop)
                op_properties -= 1
        elif option == 'Adicionar Companhia':
            comp = newMenu(stdscr, seller_companies, f'Qual companhia você gostaria de adicionar?')
            if comp != 'Voltar':
                deal_comp.append(comp)
                options.insert(0, f'Remover {comp}')
                seller_companies.remove(comp)
                op_companies -= 1
        elif option == 'Cancelar Oferta':
            break
        elif opt == 'Remover':
            if imovel in deal_prop:
                deal_prop.remove(imovel)
                seller_properties.append(imovel)
                op_properties += 1
            else:
                deal_comp.remove(imovel)
                seller_companies.append(imovel)
                op_companies += 1
            options.remove(option)
        elif opt == 'Continuar':
            if len(deal_comp) > 0 or len(deal_prop) > 0:
                valor = insert_user_input(game_win, 'Qual valor você deseja oferecer?', True)
                valor = int(valor)
                f_valor = ''+str_to_money(valor)
                deal = deal_comp + deal_prop
                if len(deal) == 1:
                    f_deal = deal[0]
                elif len(deal) > 1:
                    f_deal = ', '.join(deal)
                
                message = f'{pl} oferece à {seller}: {f_valor} por {f_deal}. {seller} aceita a proposta?'
                response = newMenu(stdscr, ['Sim', 'Não'], message)
                if response == 'Sim':
                    players_info[pl]['caixa'] -= valor
                    players_info[seller]['caixa'] += valor
                    win_center_message(game_win, f'{pl} pagou {f_valor} à {seller}')
                    if len(deal_prop) > 0:
                        for prop in deal_prop:
                            nome = prop.split(' (')[0]
                            titulos.loc[titulos['Propriedade'] == nome, 'Dono'] = pl
                            win_center_message(game_win, f'{pl} recebeu {nome}')

                    if len(deal_comp) > 0:
                        for comp in deal_comp:
                            nome = comp.split(' (')[0]
                            companhias.loc[companhias['Companhia'] == nome, 'Dono'] = pl
                            win_center_message(game_win, f'{pl} recebeu {nome}')
                    
                    break
                    
            else:
                win_center_message(game_win, 'Adicione alguma Companhia ou Propriedade para continuar')
            
def roll_dice(game_win, stdscr, pl):
    global players, players_info
    dice = new_dice(game_win)
    position = players_info[pl]['boardPosition']
    players_info[pl]['boardPosition'], new_position = getBoardPosition(game_win, position, dice, pl)
    game_win.clear()
    board_space = BOARD[new_position]
    win_center_message(game_win, f'{pl} parou em {board_space}')
    game_win.clear()
    if board_space in BOARD_FUNCTIONS.keys():
        BOARD_FUNCTIONS[board_space](stdscr, pl, dice)
    else:
        if int(new_position) in titulos['Posição'].values:
            df_partial = titulos[titulos['Posição'] == new_position]
            columns = ['Posição', 'Dono', 'Ativo', 'Hipotecada']
            space_content = df_partial.drop(columns, axis=1)
            df_partial = df_partial.iloc[0].to_dict()
            f_name = infos_in_name(df_partial['Propriedade'], df_partial['Cor'])
        else:
            df_partial = companhias[companhias['Posição'] == new_position]
            columns = ['Posição', 'Dono', 'Ativo', 'Hipotecada']
            space_content = df_partial.drop(columns, axis=1)
            df_partial = df_partial.iloc[0].to_dict()
            f_name = df_partial['Companhia']
        
        
        dono = df_partial['Dono']
        ativo = df_partial['Ativo']
        hipotecada = df_partial['Hipotecada']
        space_content = space_content.iloc[0].to_dict()
                        
        space_value = space_content['Preço']
        f_space_value = str_to_money(space_value)
        while True:
            if pd.isna(dono):
                if space_content['Preço'] < players_info[pl]['caixa']:
                    option_selected = newMenu(stdscr, ['Sim', 'Não', 'Ver Mais Informações'], f'Deseja comprar {f_name} por {f_space_value}?')

                    if option_selected == 'Sim':
                        buy(game_win, space_value, new_position, board_space, pl)
                        break
                    elif option_selected == 'Não':
                        break
                    else:
                        showInfo(stdscr, space_content, board_space)
                else:
                    win_center_message(game_win, f'{pl} não tem dinheiro para comprar essa propriedade')
                    break
            elif dono == pl and hipotecada == 0:
                caixa = players_info[pl]['caixa']
                preco_casa = space_content['Comprar Casa']
                preco_hotel = space_content['Comprar Hotel']
                titulo_color = titulos.loc[titulos['Cor'] == space_content['Cor']]
                color_total = len(titulo_color)
                color_qtd = titulo_color.loc[titulo_color['Dono'] == pl]
                color_qtd = len(color_qtd)
                if color_qtd == color_total and ativo != 'Hotel' and caixa >= preco_casa:
                    if ativo == 'Aluguel':
                        num_casas = 4
                    else:
                        casas = ativo.split(' ')
                        num_casas = 4 - int(casas)
                    options = []
                    if num_casas > 0:
                        for nc in range(1, num_casas + 1):
                            total_value = preco_casa * nc
                            if caixa >= total_value:
                                msg = '1 casa' if nc == 1 else f'{nc} casas'
                                f_total_value = str_to_money(total_value)
                                options.append(f'Comprar {msg} por {f_total_value}')
                            else:
                                break
                        total_hotel = preco_hotel + total_value
                        if caixa >= total_hotel:
                            f_preco_hotel = str_to_money(total_hotel)
                            options.append(f'Comprar {msg} e Hotel por {f_preco_hotel}')
                    else:
                        if caixa >= preco_hotel:
                            f_preco_hotel = str_to_money(preco_hotel)
                            options.append(f'Comprar Hotel por {f_preco_hotel}')
                        
                    options.append('Passar vez')
                    option_selected = newMenu(stdscr, options, f'Evoluir {board_space}')

                    if option_selected == 'Passar vez':
                        break
                    else:
                        f_option = option_selected.split('Comprar ')[1]
                        tvalue = option_selected.split('')[1]
                        f_value = locale.atof(tvalue)
                        f_value = int(f_value)
                        if f_value > (num_casas * preco_casa):
                            titulos.loc[titulos['Posição'] == new_position, 'Ativo'] = 'Hotel'
                        else:
                            casas_compradas = int(f_value / preco_casa)
                            if casas_compradas > 1:
                                ativo = f'{casas_compradas} Casas'
                            else:
                                ativo = f'{casas_compradas} Casa'
                            titulos.loc[titulos['Posição'] == new_position, 'Ativo'] = f'{ativo}'
                        players_info[pl]['caixa'] -= f_value
                        novo_saldo = str_to_money(players_info[pl]['caixa'])
                        msg_1 = f'{pl} comprou {f_option}'
                        win_center_message(game_win, msg_1)
                        msg_2 = f'Saldo de {pl} é {novo_saldo}'
                        win_center_message(game_win, msg_2)
                        break
                else:
                    break
            elif hipotecada == 1:
                win_center_message(game_win, f'{board_space} hipotecada! Não pode ser evoluida e nem receber aluguéis.')
                break
            else:
                if pay(game_win, stdscr, pl, space_content[ativo]) == True:
                    balance_change(space_content[ativo], pl, dono)
                    game_win.clear()
                    value_paid = str_to_money(space_content[ativo])
                    message = f'{board_space} pertence a {dono}. {pl} paga {value_paid} de aluguel à {dono}'
                    win_center_message(game_win, message)
                    break
                else:
                    bankrup(game_win, pl, dono)
                    value_receive = players_info[pl]['caixa']
                    players_info[dono]['caixa'] += value_receive
                    players_info[pl]['caixa'] -= space_content[ativo]
                    win_center_message(game_win, f'{dono} recebe {value_receive} e todas as propriedades pertencentes a {pl}')

def game_start(game_win, stdscr, ROUNDS):
    global prision, players, players_info, final_standing
    win_center_message(game_win, 'O jogo vai começar...')
    round = 1
    while True:
        if len(players) != 1:
            for pl in players:
                game_win.clear() 
                while True:
                    caixa = str_to_money(players_info[pl]['caixa'])
                    if pl not in list(prision.keys()):
                        user_menu = ['Rolar os dados']
                        if show_properties(game_win, stdscr, pl):
                            user_menu.append('Minhas Propriedades')
                            properties = show_properties(game_win, stdscr, pl)
                        if show_companies(game_win, stdscr, pl):
                            user_menu.append('Minhas Companhias')
                            companies = show_companies(game_win, stdscr, pl)
                        op_properties = (titulos['Dono'] != pl) & (titulos['Dono'].notna()) & (titulos['Hipotecada'] == 0)
                        op_properties = sum(op_properties)
                        op_companies = (companhias['Dono'] != pl) & (companhias['Dono'].notna()) & (companhias['Hipotecada'] == 0)
                        op_companies = sum(op_companies)
                        if(op_properties > 0 or op_companies > 0):
                            user_menu.append('Fazer Proposta')
                        option_selected = newMenu(stdscr, user_menu, f'Turno de {pl} (Dinheiro em Caixa:  {caixa})')
                        if option_selected == 'Rolar os dados':
                            roll_dice(game_win, stdscr, pl)

                            break
                        elif option_selected == 'Minhas Propriedades':
                            manage_properties(game_win, stdscr, properties, pl)
                        elif option_selected == 'Minhas Companhias':
                            manage_companies(game_win, stdscr, companies, pl)
                        elif option_selected == 'Fazer Proposta':
                            make_deal(game_win, stdscr, pl, players)
                            

                    else:
                        if prision[pl] == 0:
                            win_center_message(game_win, f'{pl} passou o primeiro dia na prisão.')
                            prision[pl] = 1
                        else:
                            win_center_message(game_win, f'{pl} passou o segundo dia na prisão. Na próxima rodada ele estará livre.')
                            del prision[pl]
                        
                        user_menu = ['Passar Vez', 'Minhas Propriedades', 'Minhas Companhias']
                        option_selected = newMenu(stdscr, user_menu, f'Turno de {pl} (Dinheiro em Caixa:  {caixa})')
                        if option_selected == 'Passar Vez':
                            break
                        elif option_selected == 'Minhas Propriedades':
                            manage_properties(game_win, stdscr, properties, pl)
                        elif option_selected == 'Minhas Companhias':
                            manage_companies(game_win, stdscr, companies, pl)
                        elif option_selected == 'Fazer Proposta':
                            make_deal(game_win, stdscr, pl, players)
        else:
            end_game(game_win)
            break

        if round <= ROUNDS:
            round += 1
        else:
            end_game(game_win)
            break

def str_to_money(value):
    money = 'R$ '+locale.format_string('%0.2f', value, grouping=True) 
    return money

def end_game(game_win):
    global players_info
    win_center_message(game_win, 'Fim de jogo')
    win_center_message(game_win, 'Vamos aos vencedores')
    all_players = players_info.keys()
    players_balance = {}
    for pl in all_players:
        players_balance[pl] = players_info[pl]['caixa']
    num = len(players_balance)
    final_standing = {}
    for pl, value in players_balance.items():
        properties = titulos.loc[(titulos['Dono'] == pl) & (titulos['Hipotecada'] == 0), ['Propriedade', 'Preço']]
        value_prop = properties['Preço'].sum()
        companies = companhias.loc[(companhias['Dono'] == pl) & (companhias['Hipotecada'] == 0), ['Companhia', 'Preço']]
        value_comp = companies['Preço'].sum()
        total_value = value + value_comp + value_prop
        final_standing[pl] = total_value
    
    final_standing = dict(sorted(final_standing.items(), key=lambda item: item[1]))
    for pl, value in final_standing.items():
        f_value = str_to_money(value)
        win_center_message(game_win, f'Em {num}º lugar')
        win_center_message(game_win, f'{pl} com um patrimônio de {f_value}')
        num -= 1


def main(stdscr):
    global players, players_info
    NVDA_SILENCE()
    curses.curs_set(0)
    message = 'Bem-Vindo ao Banco Imobiliário'
    center_message(stdscr, message)
    sleep(2)
    while True:
        mode_menu = ['Modo Clássico', 'Modo Rápido']
        option = newMenu(stdscr, mode_menu, 'Escolha o modo de jogo: ')
        if option == 'Modo Rápido':
            rapid_mode = ['5 Rodadas', '10 Rodadas', '20 Rodadas', '30 Rodadas', '40 Rodadas', '50 Rodadas', 'Voltar']
            option = newMenu(stdscr, rapid_mode, 'Quantas rodadas você quer jogar?')
            if option != 'Voltar':
                ROUNDS = int(option.split(' ')[0])
                break
        else:
            ROUNDS = False
            break
    main_menu = ['2 Jogadores', '3 Jogadores', '4 Jogadores', '5 Jogadores', '6 Jogadores']
    option_select = newMenu(stdscr, main_menu, 'Quantidade de jogadores: ')
    option = option_select.split(' ')[0]
    NUM_PLAYERS = int(option)
    stdscr.clear()
    for i in range(1, NUM_PLAYERS+1):
        pn_win = get_max_window(stdscr)
        message = f'Digite o nome do jogador {i}'
        NVDA_SPEAK(message)
        player = insert_user_input(pn_win, message)
        players.append(player)
        players_info[player] = {}
        players_info[player]['caixa'] = 1000000
        players_info[player]['boardPosition'] = 0
        players_info[player]['posses'] = []
    pn_win.clear()
    game_win = get_max_window(stdscr)
    game_start(game_win, stdscr, ROUNDS)


NVDA_SILENCE, NVDA_SPEAK = get_nvda()
curses.wrapper(main)