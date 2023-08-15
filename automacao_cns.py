#biblitoca para conectar com banco de dados
import pyodbc
import time 

#Bibliotecas para automação selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# String de conexão com o banco de dados
conn = pyodbc.connect('Driver={SQL Server};' 'Server=GUILHERME;' 'Database=WebScraping;')
cursor = conn.cursor()

# Comando SQL a executar
cursor.execute('select Nu_Cpf, CONVERT(VARCHAR,Convert(date,Dt_Nasc,121),103) from [dbo].[ListaDadosPessoas] Where CNS_consulta_Site_Link is null')

linhas = cursor.fetchall()

#Motor de busca Chrome
driver = webdriver.Chrome()

# Verificar a quantidade de linhas retornadas na consulta
#num_rows = cursor.rowcount

for linha in linhas:
        CPF = linha[0]
        Dt_nasc = linha[1]
        #Printar os CPF e Data de Nascimento que será consultado
        print(CPF,Dt_nasc)        
        #Url para "raspar" informações
        driver.get("https://cnesadm.datasus.gov.br/cnesadm/publico/usuarios/cadastro")
        time.sleep(2) 
        #Mapear os campos da URL
        campo_cpf = driver.find_element(By.ID, "cpf")
        campo_cpf.send_keys(CPF)

        campo_data_nascimento = driver.find_element(By.ID, "dataNascimento")
        campo_data_nascimento.send_keys(Dt_nasc)
        
        #Identificar o Botão - "PROSSEGUIR"
        botao_prosseguir = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"].form-control.btn.btn-primary')
        
        #Acao no selecionar o Botão identificado
        botao_prosseguir.click()
       
        #delay para carregar a proxima pagina 
        driver.implicitly_wait(10)  # Espera implícita por 10 segundos  
        
        try:
            elemento_li = driver.find_element(By.CLASS_NAME, "text-red")
            conteudo_li = elemento_li.text
            # Comando SQL a executar de retorno
            update_query = f"UPDATE [dbo].[ListaDadosPessoas] SET CNS_consulta_Site_Link = '{conteudo_li}' WHERE Nu_Cpf = '{CPF}'"
            cursor.execute(update_query)
            conn.commit()                        
            driver.refresh() 
            time.sleep(3)
        except NoSuchElementException :
            campo_cns = driver.find_element(By.ID, "cns")
            valor_cns = campo_cns.get_attribute("value")            
            # Comando SQL a executar de retorno
            update_query = f"UPDATE [dbo].[ListaDadosPessoas] SET CNS_consulta_Site_Link = '{valor_cns}' WHERE Nu_Cpf = '{CPF}'"
            cursor.execute(update_query)
            conn.commit() 
            driver.refresh() 
            time.sleep(3) 
        finally :
            #Recarrega a pagina
            driver.refresh()                           
# Fechar a conexão com o banco de dados
conn.close()