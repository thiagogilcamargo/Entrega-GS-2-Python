import PySimpleGUI as sg
import oracledb as db 
import json

# Configurações de conexão com o banco de dados Oracle
DB_USER = 'rm551211'
DB_PASSWORD = 'fiap23'
DB_DSN = 'oracle.fiap.com.br/orcl'

# Função para conectar ao banco de dados Oracle
def connect_to_oracle():
    connection = db.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    return connection


# Função para realizar consulta no banco de dados
def execute_query(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result


def insert_data(connection, table_name, data, id_column=None):
    cursor = connection.cursor()

    # Remova a coluna de identidade se presente
    if id_column and id_column in data:
        del data[id_column]
    
    # Obtenha o próximo valor da sequência para a coluna de identidade, se especificada
    if id_column:
        # Obtenha o nome da sequência correspondente à coluna de identidade
        sequence_name = f"{id_column}_SEQ"

        cursor.execute(f"SELECT {sequence_name}.nextval FROM dual")
        id_value = cursor.fetchone()[0]

        # Adicione a coluna de identidade e seu valor de volta
        data[id_column] = id_value

    # Separe as colunas e os valores
    columns = [str(column) for column in data]
    values = [data[column] for column in columns]

    # Convertendo os valores para string e formatando a consulta SQL
    values = [str(value) for value in values]

    placeholders = ', '.join([':' + str(i + 1) for i in range(len(values))])

    # Construa a consulta SQL sem especificar a coluna de ID
    if id_column:
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    else:
        query = f"INSERT INTO {table_name} ({id_column}, {', '.join(columns)}) VALUES ({placeholders})"
    
    # Imprimir informações para debug
    print("Query:", query)
    print("Values:", values)

    try:
        # Utilize a função execute para executar a consulta
        cursor.execute(query, values)
        connection.commit()
        sg.popup(f'Registro inserido com sucesso na tabela {table_name}!')
    except Exception as e:
        # Imprima a mensagem completa da exceção para diagnóstico
        print("Error:", e)
        sg.popup_error(f'Erro ao inserir registro na tabela {table_name}. Consulte a saída no console para obter detalhes.')

    cursor.close()


# Função para deletar dados na tabela do banco de dados
def delete_data(connection, table_name, condition_column, condition_value):
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE {condition_column} = :1", (condition_value,))
    connection.commit()
    cursor.close()

def update_data(connection, table_name, update_values, condition_column, condition_value):
    cursor = connection.cursor()
    
    # Construa a string de atualização dinamicamente
    update_string = ', '.join([f'{col} = :{i + 1}' for i, col in enumerate(update_values.keys())])
    
    # Crie um dicionário combinando os valores a serem atualizados e o valor da condição
    update_parameters = {f'{i + 1}': value for i, value in enumerate(update_values.values())}
    update_parameters[f'{len(update_values) + 1}'] = condition_value

    cursor.execute(f"UPDATE {table_name} SET {update_string} WHERE {condition_column} = :{len(update_values) + 1}", update_parameters)
    
    connection.commit()
    cursor.close()



def consult_data_param(connection, table, column, value):
    try:
        cursor = connection.cursor()
        query = f"SELECT * FROM {table} WHERE {column} = :1"
        cursor.execute(query, (value,))
        result = cursor.fetchall()

        # Extrair as colunas do cursor.description e criar um dicionário
        columns = [desc[0] for desc in cursor.description]
        result_dict = [dict(zip(columns, row)) for row in result]

        return result_dict
    except Exception as e:
        print(f"Error in consult_data_param: {str(e)}")
        return None




def export_to_json(data, filename_prefix):
    if not data:
        sg.popup_error('Nenhum resultado para exportar para JSON.')
        return
    
    # Extrai o ID do primeiro item da lista (assumindo que o ID está na primeira posição)
    id_value = str(data[0][0])

    filename = f"{filename_prefix}_id_{id_value}.json"

    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    sg.popup(f'Consulta exportada para JSON com sucesso! Nome do arquivo: {filename}')


# Layout para inserção de paciente
layout_inserir_paciente = [
    [sg.Text('Nome do Paciente:'), sg.InputText(key='nome')],
    [sg.Text('RG do Paciente:'), sg.InputText(key='rg')],
    [sg.Text('CPF do Paciente:'), sg.InputText(key='cpf')],
    [sg.Text('Endereço do Paciente:'), sg.InputText(key='endereco')],
    [sg.Text('E-mail do Paciente:'), sg.InputText(key='email')],
    [sg.Text('Telefone do Paciente:'), sg.InputText(key='telefone')],
    [sg.Text('Sexo do Paciente:'), sg.InputText(key='sexo')],
    [sg.Text('Tipo Sanguíneo do Paciente:'), sg.InputText(key='tipo_sangue')],
    [sg.Text('Peso do Paciente:'), sg.InputText(key='peso')],
    [sg.Text('Altura do Paciente:'), sg.InputText(key='altura')],
    [sg.Text('Escolaridade do Paciente:'), sg.InputText(key='escolaridade')],
    [sg.Button('Cadastrar')]
]

# Layout para exclusão de paciente
layout_excluir_paciente = [
    [sg.Text('ID do Paciente a ser excluído:'), sg.InputText(key='id_paciente')],
    [sg.Button('Excluir')]
]

# Layout para consulta de pacientes
layout_consultar_pacientes = [
    [sg.Text('ID do Paciente a ser consultado:'), sg.InputText(key='id_paciente')],
    [sg.Button('Consultar')]
]

layout_inserir_funcionario = [
    [sg.Text('Nome do Funcionário:'), sg.InputText(key='nome')],
    [sg.Text('CPF do Funcionário:'), sg.InputText(key='cpf')],
    [sg.Text('Endereço do Funcionário:'), sg.InputText(key='endereco')],
    [sg.Text('E-mail do Funcionário:'), sg.InputText(key='email')],
    [sg.Text('Telefone do Funcionário:'), sg.InputText(key='telefone')],
    [sg.Button('Cadastrar')]
]

# Layout para exclusão de funcionário
layout_excluir_funcionario = [
    [sg.Text('ID do Funcionário a ser excluído:'), sg.InputText(key='id_funcionario')],
    [sg.Button('Excluir')]
]

# Layout para consulta de funcionários
layout_consultar_funcionarios = [
    [sg.Text('ID do Funcionário a ser consultado:'), sg.InputText(key='id_funcionario')],
    [sg.Button('Consultar')]
]

# Layout para inserção de médico
layout_inserir_medico = [
    [sg.Text('Nome do Médico:'), sg.InputText(key='nome')],
    [sg.Text('CRM do Médico:'), sg.InputText(key='crm')],
    [sg.Text('Telefone do Médico:'), sg.InputText(key='telefone')],
    [sg.Text('Especialidade do Médico:'), sg.InputText(key='especialidade')],
    [sg.Button('Cadastrar')]
]

# Layout para exclusão de médico
layout_excluir_medico = [
    [sg.Text('ID do Médico a ser excluído:'), sg.InputText(key='id_medico')],
    [sg.Button('Excluir')]
]

# Layout para consulta de médicos
layout_consultar_medicos = [
    [sg.Text('ID do Médico a ser consultado:'), sg.InputText(key='id_medico')],
    [sg.Button('Consultar')]
]


# Layout para atualização de dados nas tabelas
layout_update_data = [
    [sg.Text('Selecione a tabela:')],
    [sg.Radio('Paciente', 'table_radio', key='table_paciente'), sg.Radio('Funcionário', 'table_radio', key='table_funcionario'), sg.Radio('Médico', 'table_radio', key='table_medico')],
    [sg.Text('ID do Registro a ser Atualizado:'), sg.InputText(key='id_update')],
    [sg.Button('Atualizar')]
]


# Layout do menu principal
layout_menu = [
    [sg.Button('1. Inserir Paciente'), sg.Button('2. Excluir Paciente'), sg.Button('3. Consultar Pacientes')],
    [sg.Button('4. Inserir Funcionário'), sg.Button('5. Excluir Funcionário'), sg.Button('6. Consultar Funcionários')],
    [sg.Button('7. Inserir Médico'), sg.Button('8. Excluir Médico'), sg.Button('9. Consultar Médicos')],
    [sg.Button('10. Atualizar Dados'), sg.Button('Sair')],
]



# Criar janela do menu principal
window_menu = sg.Window('Sistema de Cadastro - Healthflow', layout_menu, resizable=True, finalize=True)

# Conectar ao banco de dados Oracle
connection = connect_to_oracle()
if connection is None:
    sg.popup_error('Falha ao conectar ao banco de dados. Verifique as configurações de conexão.')
    exit()



# Loop principal
while True:
    event_menu, values_menu = window_menu.read()

    if event_menu == sg.WINDOW_CLOSED or event_menu == 'Sair':
        break

    if event_menu == '1. Inserir Paciente':
        window_inserir_paciente = sg.Window('Inserir Paciente', layout_inserir_paciente)
        event_inserir_paciente, values_inserir_paciente = window_inserir_paciente.read()

        if event_inserir_paciente == 'Cadastrar':
            try:
                # Validar dados antes de enviar para o banco de dados
                nome = values_inserir_paciente['nome'].strip()
                rg = values_inserir_paciente['rg'].strip()
                cpf = values_inserir_paciente['cpf'].strip()
                endereco = values_inserir_paciente['endereco'].strip()
                email = values_inserir_paciente['email'].strip()
                telefone = values_inserir_paciente['telefone'].strip()
                sexo = values_inserir_paciente['sexo']
                tipo_sangue = values_inserir_paciente['tipo_sangue']
                peso_str = values_inserir_paciente.get('peso', '')
                altura_str = values_inserir_paciente.get('altura', '')
                escolaridade = values_inserir_paciente['escolaridade']
                   
                    # Verificar se os campos obrigatórios estão preenchidos
                if not nome or not rg or not cpf:
                   sg.popup_error('Erro ao inserir paciente. Certifique-se de fornecer nome, RG e CPF.')
                else:
                # Verificar se os valores são válidos e converter para float (peso e altura)
                     if peso_str and altura_str:
                      peso = float(peso_str)
                      altura = float(altura_str)


                # Verifica se os valores são válidos e converte para float
                if peso_str and altura_str:
                    peso = float(peso_str)
                    altura = float(altura_str)

                    
                    insert_data(connection, 'TB_HF_PACIENTE', {
                        'NM_NOME_PACIENTE': values_inserir_paciente['nome'],
                        'NM_RG_PACIENTE': values_inserir_paciente['rg'],
                        'NR_CPF_PACIENTE': values_inserir_paciente['cpf'],
                        'NM_END_PACIENTE': values_inserir_paciente['endereco'],
                        'NM_EMAIL_PACIENTE': values_inserir_paciente['email'],
                        'NM_TEL_PACIENTE': values_inserir_paciente['telefone'],
                        'BL_SEXO_PACIENTE': values_inserir_paciente['sexo'],
                        'NM_TPSANG_PACIENTE': values_inserir_paciente['tipo_sangue'],
                        'NR_PESO_PACIENTE': values_inserir_paciente['peso'],
                        'NR_ALTURA_PACIENTE': values_inserir_paciente['altura'],
                        'NM_ESCOLARIDADE_PACIENTE': values_inserir_paciente['escolaridade'],
                    }, 'ID_PACIENTE')

                    sg.popup('Paciente inserido com sucesso!')
                else:
                    sg.popup_error('Erro ao inserir paciente. Certifique-se de que os campos de peso e altura contêm valores numéricos.')

            except ValueError:
                sg.popup_error('Erro ao inserir paciente. Certifique-se de que os campos de peso e altura contêm valores numéricos.')

            window_inserir_paciente.close()

    elif event_menu == '2. Excluir Paciente':
        window_excluir_paciente = sg.Window('Excluir Paciente', layout_excluir_paciente)
        event_excluir_paciente, values_excluir_paciente = window_excluir_paciente.read()

        if event_excluir_paciente == 'Excluir':
            try:
                connection = connect_to_oracle()
                # Verifica se o ID existe antes de tentar excluir
                if consult_data_param(connection, 'TB_HF_PACIENTE', 'ID_PACIENTE', int(values_excluir_paciente['id_paciente'])):
                    delete_data(connection, 'TB_HF_PACIENTE', 'ID_PACIENTE', int(values_excluir_paciente['id_paciente']))
                    sg.popup('Paciente excluído com sucesso!')
                else:
                    sg.popup_error('ID do Paciente não encontrado.')
            except Exception as e:
                sg.popup_error(f'Erro ao excluir Paciente. Detalhes: {str(e)}')

            window_excluir_paciente.close()

    elif event_menu == '3. Consultar Pacientes':
        window_consultar_pacientes = sg.Window('Consultar Pacientes', layout_consultar_pacientes)
        event_consultar_pacientes, values_consultar_pacientes = window_consultar_pacientes.read()

        if event_consultar_pacientes == 'Consultar':
            try:
                id_paciente = values_consultar_pacientes.get('id_paciente', '')
                if not id_paciente.isdigit() or int(id_paciente) <= 0:
                    sg.popup_error('Por favor, forneça um ID de paciente válido (número inteiro positivo).')
                else:
                    connection = connect_to_oracle()
                    result_pacientes = consult_data_param(connection, 'TB_HF_PACIENTE', 'ID_PACIENTE', int(values_consultar_pacientes['id_paciente']))
                    if result_pacientes:
                        result_popup = sg.popup_ok_cancel(f'Consulta realizada com sucesso!\nResultado:\n{result_pacientes}\n\nDeseja exportar para JSON?',
                                                      title='Consulta de Pacientes', keep_on_top=True)
                        if result_popup == 'OK':
                           export_to_json(result_pacientes, 'consulta_pacientes.json')
                           sg.popup('Consulta exportada para JSON com sucesso!')
                    else:
                        sg.popup_error('ID do Paciente não encontrado.')
            except Exception as e:
                sg.popup_error(f'Erro ao consultar Paciente. Detalhes: {str(e)}')

        elif event_consultar_pacientes == 'Exportar JSON':
            if 'result_pacientes' in locals() and result_pacientes:
                export_to_json(result_pacientes, 'consulta_pacientes')
                sg.popup('Consulta exportada para JSON com sucesso!')

        window_consultar_pacientes.close()

    elif event_menu == '4. Inserir Funcionário':
        window_inserir_funcionario = sg.Window('Inserir Funcionário', layout_inserir_funcionario)
        event_inserir_funcionario, values_inserir_funcionario = window_inserir_funcionario.read()

        if event_inserir_funcionario == 'Cadastrar':
            try:
                # Validar dados antes de enviar para o banco de dados
                nome_funcionario = values_inserir_funcionario['nome'].strip()
                cpf_funcionario = values_inserir_funcionario['cpf'].strip()
                endereco_funcionario = values_inserir_funcionario.get('endereco', '').strip()
                email_funcionario = values_inserir_funcionario.get('email', '').strip()
                telefone_funcionario = values_inserir_funcionario.get('telefone', '').strip()

                # Verificar se os campos obrigatórios estão preenchidos
                if not nome_funcionario or not cpf_funcionario:
                    sg.popup_error('Erro ao inserir funcionário. Certifique-se de fornecer nome e CPF.')
                else:
                    insert_data(connection, 'TB_HF_FUNCIONARIO', {
                    'NM_NOME_FUNCIONARIO': values_inserir_funcionario['nome'],
                    'NR_CPF_FUNCIONARIO': values_inserir_funcionario['cpf'],
                    'NM_END_FUNCIONARIO': values_inserir_funcionario.get('endereco', ''),  
                    'NM_EMAIL_FUNCIONARIO': values_inserir_funcionario.get('email', ''),    
                    'NM_TEL_FUNCIONARIO': values_inserir_funcionario.get('telefone', '')     
                }, 'ID_FUNCIONARIO')

                    sg.popup('Funcionário inserido com sucesso!')
            except Exception as e:
                    sg.popup_error(f'Erro ao inserir Funcionário. Detalhes: {str(e)}')

            window_inserir_funcionario.close()

    elif event_menu == '5. Excluir Funcionário':
        window_excluir_funcionario = sg.Window('Excluir Funcionário', layout_excluir_funcionario)
        event_excluir_funcionario, values_excluir_funcionario = window_excluir_funcionario.read()

        if event_excluir_funcionario == 'Excluir':
            try:
                connection = connect_to_oracle()
                # Verifica se o ID existe antes de tentar excluir
                if consult_data_param(connection, 'TB_HF_FUNCIONARIO', 'ID_FUNCIONARIO', int(values_excluir_funcionario['id_funcionario'])):
                    delete_data(connection, 'TB_HF_FUNCIONARIO', 'ID_FUNCIONARIO', int(values_excluir_funcionario['id_funcionario']))
                    sg.popup('Funcionário excluído com sucesso!')
                else:
                    sg.popup_error('ID do Funcionário não encontrado.')
            except Exception as e:
                sg.popup_error(f'Erro ao excluir Funcionário. Detalhes: {str(e)}')

            window_excluir_funcionario.close()

    elif event_menu == '6. Consultar Funcionários':
        window_consultar_funcionarios = sg.Window('Consultar Funcionários', layout_consultar_funcionarios)
        event_consultar_funcionarios, values_consultar_funcionarios = window_consultar_funcionarios.read()

        if event_consultar_funcionarios == 'Consultar':
            try:
                # Validar se o ID é um número inteiro positivo
                id_funcionario = values_consultar_funcionarios.get('id_funcionario', '')
                if not id_funcionario.isdigit() or int(id_funcionario) <= 0:
                    sg.popup_error('Por favor, forneça um ID de funcionario válido (número inteiro positivo).')
                else:
                    connection = connect_to_oracle()
                    result_funcionarios = consult_data_param(connection, 'TB_HF_FUNCIONARIO', 'ID_FUNCIONARIO', int(values_consultar_funcionarios['id_funcionario']))
                    if result_funcionarios:
                        result_popup = sg.popup_ok_cancel(f'Consulta realizada com sucesso!\nResultado:\n{result_funcionarios}\n\nDeseja exportar para JSON?',
                                                      title='Consulta de Funcionários', keep_on_top=True)
                        if result_popup == 'OK':
                           export_to_json(result_funcionarios, 'consulta_funcionarios.json')
                           sg.popup('Consulta exportada para JSON com sucesso!')
                    else:
                         sg.popup_error('ID do Funcionario não encontrado.')
            except Exception as e:
                sg.popup_error(f'Erro ao consultar Funcionário. Detalhes: {str(e)}')

        elif event_consultar_funcionarios == 'Exportar JSON':
            if 'result_funcionarios' in locals() and result_funcionarios:
                export_to_json(result_funcionarios, 'consulta_funcionarios')
                sg.popup('Consulta exportada para JSON com sucesso!')

        window_consultar_funcionarios.close()

    elif event_menu == '7. Inserir Médico':
        window_inserir_medico = sg.Window('Inserir Médico', layout_inserir_medico)
        event_inserir_medico, values_inserir_medico = window_inserir_medico.read()

        if event_inserir_medico == 'Cadastrar':
            try:
                # Validar dados antes de enviar para o banco de dados
                nome_medico = values_inserir_medico['nome'].strip()
                crm_medico = values_inserir_medico.get('crm', '').strip()
                telefone_medico = values_inserir_medico['telefone'].strip()
                especialidade_medico = values_inserir_medico['especialidade'].strip()

            # Verificar se os campos obrigatórios estão preenchidos
                if not nome_medico or not crm_medico or not telefone_medico or not especialidade_medico:
                   sg.popup_error('Erro ao inserir médico. Certifique-se de fornecer todos os dados obrigatórios.')
                else:
                

                    insert_data(connection, 'TB_HF_MEDICO', {
                        'NM_NOME_MEDICO': values_inserir_medico['nome'],
                        'NM_CRM_MEDICO': crm_medico,
                        'NM_TEL_MEDICO': values_inserir_medico['telefone'],
                        'NM_ESPECIALIDADE_MEDICO': values_inserir_medico['especialidade'],
                    }, 'ID_MEDICO')

                    sg.popup('Médico inserido com sucesso!')
            except Exception as e:
                # Imprima a mensagem completa da exceção para diagnóstico
                print("Error:", e)
                sg.popup_error('Erro ao inserir médico. Consulte a saída no console para obter detalhes.')

            window_inserir_medico.close()

    elif event_menu == '8. Excluir Médico':
        window_excluir_medico = sg.Window('Excluir Médico', layout_excluir_medico)
        event_excluir_medico, values_excluir_medico = window_excluir_medico.read()

        if event_excluir_medico == 'Excluir':
            try:
                connection = connect_to_oracle()
                # Verifica se o ID existe antes de tentar excluir
                if consult_data_param(connection, 'TB_HF_MEDICO', 'ID_MEDICO', int(values_excluir_medico['id_medico'])):
                    delete_data(connection, 'TB_HF_MEDICO', 'ID_MEDICO', int(values_excluir_medico['id_medico']))
                    sg.popup('Médico excluído com sucesso!')
                else:
                    sg.popup_error('ID do Médico não encontrado.')
            except Exception as e:
                sg.popup_error(f'Erro ao excluir Médico. Detalhes: {str(e)}')

            window_excluir_medico.close()

    elif event_menu == '9. Consultar Médicos':
        window_consultar_medicos = sg.Window('Consultar Médicos', layout_consultar_medicos)
        event_consultar_medicos, values_consultar_medicos = window_consultar_medicos.read()

        if event_consultar_medicos == 'Consultar':
            try:
                id_medico = values_consultar_medicos.get('id_medico', '')
                if not id_medico.isdigit() or int(id_medico) <= 0:
                    sg.popup_error('Por favor, forneça um ID de médico válido (número inteiro positivo).')
                else:
                    connection = connect_to_oracle()
                    result_medicos = consult_data_param(connection, 'TB_HF_MEDICO', 'ID_MEDICO', int(values_consultar_medicos['id_medico']))
                    if result_medicos:
                       result_popup = sg.popup_ok_cancel(f'Consulta realizada com sucesso!\nResultado:\n{result_medicos}\n\nDeseja exportar para JSON?',
                                                      title='Consulta de Médicos', keep_on_top=True)
                       if result_popup == 'OK':
                          export_to_json(result_medicos, 'consulta_medicos.json')
                          sg.popup('Consulta exportada para JSON com sucesso!')
                    else:
                         sg.popup_error('ID do Médico não encontrado.') 
            except Exception as e:
                sg.popup_error(f'Erro ao consultar Médico. Detalhes: {str(e)}')

        elif event_consultar_medicos == 'Exportar JSON':
            if 'result_medicos' in locals() and result_medicos:
                # Use o prefixo 'consulta_medicos' para o nome do arquivo
                export_to_json(result_medicos, 'consulta_medicos')
                # sg.popup('Consulta exportada para JSON com sucesso!')
            else:
                sg.popup_error('Nenhum resultado para exportar para JSON.')

            window_consultar_medicos.close()
        


    elif event_menu == '10. Atualizar Dados':
         window_update_data = sg.Window('Atualizar Dados', layout_update_data)
         event_update_data, values_update_data = window_update_data.read()

    if event_update_data == 'Atualizar':
        try:
            # Identificar a tabela selecionada
            if values_update_data['table_paciente']:
                table_name = 'TB_HF_PACIENTE'
                id_column = 'ID_PACIENTE'
            elif values_update_data['table_funcionario']:
                table_name = 'TB_HF_FUNCIONARIO'
                id_column = 'ID_FUNCIONARIO'
            elif values_update_data['table_medico']:
                table_name = 'TB_HF_MEDICO'
                id_column = 'ID_MEDICO'
            else:
                sg.popup_error('Selecione uma tabela para atualizar.')
                continue  # Continue o loop

            # Obter o ID do registro a ser atualizado
            id_to_update = values_update_data['id_update']

            # Verificar se o registro com o ID especificado existe
            if consult_data_param(connection, table_name, id_column, int(id_to_update)):
                # Recuperar os dados atuais para o registro selecionado
                current_data = consult_data_param(connection, table_name, id_column, int(id_to_update))

                # Construir um layout para atualizar o registro
                layout_update_record = [
                    [sg.Text(f'Atualizar dados para o registro de {table_name} com ID {id_to_update}:')],
                ]

                # Adicionar o campo de visualização do ID
                layout_update_record.append([sg.Text(f'{id_column}: {id_to_update}')])

                # Gerar dinamicamente campos de entrada para cada coluna (exceto o ID)
                for i, column_name in enumerate(current_data[0].keys()):
                    if column_name != id_column:
                        layout_update_record.append([sg.Text(f'{column_name}:'), sg.InputText(default_text=current_data[0][column_name], key=f'update_{column_name}')])

                layout_update_record.append([sg.Button('Confirmar Atualização')])

                window_update_record = sg.Window(f'Atualizar Registro - {table_name}', layout_update_record)
                event_update_record, values_update_record = window_update_record.read()

                if event_update_record == 'Confirmar Atualização':
                    # Verificar se há campos vazios
                    if any(values_update_record[f'update_{column_name}'].strip() == '' for column_name in current_data[0].keys() if column_name != id_column):
                        sg.popup_error('Preencha todos os campos antes de confirmar a atualização.')
                        continue 

                    # Construir um dicionário de valores atualizados
                    update_values = {column_name: values_update_record[f'update_{column_name}'] for column_name in current_data[0].keys() if column_name != id_column}

                    # Realizar a atualização no banco de dados
                    update_data(connection, table_name, update_values, id_column, int(id_to_update))

                    sg.popup(f'Registro de {table_name} com ID {id_to_update} atualizado com sucesso!')

                window_update_record.close()
            else:
                sg.popup_error(f'Registro com {id_column} {id_to_update} não encontrado.')

        except Exception as e:
            sg.popup_error(f'Erro ao atualizar dados. Detalhes: {str(e)}')

    window_update_data.close()

    


