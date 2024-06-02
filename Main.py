import types
from abc import abstractmethod, ABCMeta #esse import serve pra gerar as Classes Base Abstratas, pra herança
import sys
from argparse import *
import time
bin_format = '#010b'  # isso daqui é o formato binário para armazenar dados. '#010b' = 8 bits/1 byte sem incluir '0b' anexado
#hd de denisson---------------------------------------------------------------------------------------------
import psutil
import matplotlib.pyplot as plt

def get_disk_usage():
    """
    Obtém o uso do disco do diretório raiz.

    Returns:
    dict: Um dicionário contendo o total, usado e livre espaço em disco em bytes.
    """
    # Obtém as informações de uso do disco para o diretório raiz
    usage = psutil.disk_usage('/')
    # Retorna as informações em um formato de dicionário
    return {
        'total': usage.total,
        'used': usage.used,
        'free': usage.free
    }

def format_size(bytes):
    """
    Formata o tamanho em bytes para uma string legível (KB, MB, GB, TB).

    Args:
    bytes (int): Tamanho em bytes.

    Returns:
    str: Tamanho formatado como uma string legível.
    """
    # Define os sufixos para os diferentes tamanhos
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024

def plot_disk_usage(usage):
    """
    Plota o uso do disco em um gráfico de pizza.

    Args:
    usage (dict): Dicionário contendo informações sobre o uso do disco.
    """
    # Extrai os valores usados e livres
    labels = ['Usado', 'Livre']
    sizes = [usage['used'], usage['free']]
    # Define as cores para cada seção do gráfico
    colors = ['#ff9999','#66b3ff']
    # Define a explosão para destacar a seção 'Usado'
    explode = (0.1, 0)

    # Cria o gráfico de pizza
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Assegura que o gráfico seja desenhado como um círculo

    # Adiciona um título ao gráfico
    plt.title('Uso do Disco')

    # Adiciona a legenda com as informações de tamanho total, usado e livre
    plt.legend([
        f"Total: {format_size(usage['total'])}",
        f"Usado: {format_size(usage['used'])}",
        f"Livre: {format_size(usage['free'])}"
    ], loc="upper right")

    # Mostra o gráfico
    plt.show()
#coisinha dos 3 pontinhos que eu to botando sem motivo nenhum!!
def mensagembase(n):
    print('\b' * n + ' ' * n + '\b' * n, end='', flush=True)
def waiting_dots(wait, ndots=4, interval=0.5, message="Esperando", final_message=None):
    start = time.time()
    print(message, end="", flush=True)
    while time.time() - start < wait:
        for _ in range(ndots):
            print('.', end='', flush=True)
            time.sleep(interval)
        mensagembase(ndots)
        time.sleep(interval)
    if final_message is not None:
        mensagembase(len(message))
        print(final_message)
# //ERROS
class ParityCalculationException(
    Exception):  # Verifica se ocorre um erro de paridade, no caso,Se um número ímpar de bits (incluindo o bit de paridade) for transmitido incorretamente,
    # o bit de paridade estará incorreto, indicando assim que ocorreu um erro de paridade na transmissão.
    def __init__(self, block=None, experado=None, actual=None):
        self.block = block
        self.experado = experado
        self.actual = actual

        if block is None or experado is None or actual is None:  # receber um valor vazio
            msg = "Calculo de Paridade Incorreto!!"
        else:
            msg = "Calculo incorreto no \nbloco: "  # aqui fala qual bloco está com alguma disparidade
            for x in block:
                msg += x + " "
            msg += "\nEsperado:  " + repr(experado) + " (" + format(experado, '#010b') + ")\n"
            msg += "Atual:   " + repr(actual) + " (" + format(actual, '#010b') + ")\n"
        super(ParityCalculationException, self).__init__(msg)


# exceção geral, será utilizada nos casos abaixo
class DiskException(Exception):
    def __init__(self, msg):
        self.msg = msg
        super(DiskException, self).__init__(msg)


# Essa exceção ocorrerá quando o disco estiver cheio
class DiskFullException(DiskException):
    def __init__(self, disk_id):
        self.disk_id = disk_id
        super(DiskFullException, self).__init__("Erro! O disco selecionado '" + repr(disk_id) + "' está cheio")


# Erro na leitura de disco, vai ser usada no comando read ali em baixo
class DiskReadException(DiskException):
    def __init__(self, msg):
        self.msg = msg
        super(DiskReadException, self).__init__(msg)


# erro na reconstrução do disco
class DiskReconstructException(DiskException):
    def __init__(self, msg):
        self.msg = msg
        super(DiskReconstructException, self).__init__(msg)


# Erro nos dados transmitidos. No caso, os dados foram diferentes do esperado. (vamos usar isso com o comando de alterar os dados que foram impressos, em um teste)
class DataMismatchException(DiskException):
    def __init__(self, msg):
        self.msg = msg
        super(DataMismatchException, self).__init__(msg)


# --------------------------------------------------------------------------------------------------------------------------------------
# comandos base do disco
class Disco:
    def __init__(self, disk_id,
                 capacity=0):  # inicia a base do disco (ID, capacidade maxima e o conteudo a botar no disco, no caso a data ai
        self.disk_id = disk_id
        self.capacity = capacity
        self.data = []

    # comando para representar o disco e sua informação, basicamente informar o conteúdo do disco
    def __repr__(self):
        return repr(self.disk_id) + ":" + repr(self.data)

    # Comando de leitura
    def __len__(self):
        return len(self.data)

    # comando de igualdade
    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    # comando de negação
    def __ne__(self, other):
        return not self.__eq__(other)

    # Comando de Escrita
    def write(self, data):
        if (self.capacity > 0) and (len(self.data) + len(data) > self.capacity):
            raise DiskFullException(self.disk_id)  # exceção do disco cheio
        self.data.append(data)

    # comando de leitura
    def read(self, index):
        if index >= len(self.data):
            raise DiskReadException( #Exceção de leitura no disco
                "Impossível de ler o indicador : '" + repr(index) + "'  no disco :'" + repr(self.disk_id) +
                "': Isso se dá, pois o indicador está fora dos limites pré-estabelecidos")
        return self.data[index]


def split_data(data, size):  # separador de dados
    for i in range(0, len(data), size):
        yield data[i:i + size]
#-------------------------------------------------------------------------------------------------------------
#Classe para manipular os arquivos da raid (ler, escrever, transformar em string.. etc.)
class ArquivosdeRAID:
    data_B = [] #dados dos arquivos de bloco
    start_addr = None
    padding = 0
    def __init__(self, file_id, data): #iniciando as informações do arquivo
        self.id = file_id #identificação do arquivo
        self.data_S = data #dados
        self.data_B = self.converter_em_string(data) #data convertida em string

    # Comando de leitura
    def __len__(self):
        return len(self.data_B)

    # comando para representar o arquivo e sua informação
    def __repr__(self):
        return repr(self.id) + ": '" + self.data_S + "'"

    # comando de igualdade
    def __eq__(self, other):
        if type(other) is type(self):
            return self.data_B == other.data_B
        return False
    # comando de negação
    def __ne__(self, other):
        return not self.__eq__(other)

    #Comando para converter os dados em string.

    @staticmethod
    def converter_em_string(d):
        bin_list = []
        for x in d: #-> parte transformando a palavra em número (inteiro)
            bin_list.append(
                format(ord(x), bin_format))  # Modifica o caractere para inteiro e depois  para binário e adiciona no fim da lista
        return bin_list #retorna a lista em forma de binário
    @staticmethod
    def from_bits(file_id, b): #converter de binário pra inteiro e depois para string (processo reverso do de cima ai)
        ret_str = "" #define a variável como vazia, que vai receber as palavras
        for x in b:
            ret_str += chr(int(x, 2)) #o int transforma em inteiro, e depois o chr transforma em letra, ai soma, formando a string.
        return ArquivosdeRAID(file_id, ret_str)
#-------------------------------------------------------------------------------------------------------------
#Controlador do processo da RAID básico (classe abstrata)
class ControladorRAID(metaclass=ABCMeta): #se pah eu tenho q botar esse código em outra aba pra dar import, mas ai n sei se o prof iria aceitar(?)
    # o uso do abcmeta ai é pra criar classes de base abstratas, que são as classes que não contêm implementações de funções -> serve pra herança
    # iniciando e deixando o número de disco e os arquivos vazios
    arquivos = []
    disks = []

    def __init__(self, num_disks,disk_cap=0):  # atribui um valor para a variavel do numero de disco e o máximo de disco.
        self.num_disks = num_disks
        self.disk_cap = disk_cap
        for i in range(num_disks):
            self.disks.append(Disco(i, disk_cap))

    # leitura do disco do inicio
    def __len__(self):
        return len(self.disks[0])

    # Retorna uma linha de dados do disco
    def get_linhacd(self, index):
        block = []
        for i in range(len(self.disks)):
            try:
                block.append(self.disks[i].read(index))
            except IndexError:
                print(
                    "Este erro é gerado quando o valor do índice fornecido é negativo ou excede o comprimento da sequência")
                pass
        return block

    # comando de escrever o arquivo
    def escreve_arquivo(self, arq):
        if len(self.arquivos) == 0: #arquivo vazio
            arq.start_addr = 0
        else:
            arq.start_addr = len(self) #arquivo não vazio

        self.arquivos.append(arq)
        blocks = list(split_data(arq.data_B, len(self.disks) - 1)) #separa os dados do arquivo em blocos
        arq.padding = (len(self.disks) - 1) - len(blocks[-1]) #separa os blocos um do outro, para n ficar um monte de número binário desorganizado
        self.escreve_parte(arq.data_B + [format(0, '#010b')] * arq.padding) #escreve o fragmento de texto no hd
    #Comando para validar se o conteúdo do disco é... válido
    def validar_disco(self, orig_disks=None):
        for i in range(len(self)):
            # Esse comando  Valida a paridade de um bloco removendo cada item em sequência, calculando a paridade dos itens restantes  e comparando o resultado com o item removido.
            self.validar_paridade(self.get_linhacd(i))
        if orig_disks is not None:
            for i in range(len(orig_disks)):
                if orig_disks[i] != self.disks[i]:
                    raise DiskReconstructException("Reconstrução de disco falhou: Disco " + repr(i) + " está corrompido")
    @abstractmethod
    def escreve_parte(self, data):
        pass

    @abstractmethod
    def ler_todos_dados(self):
        pass

    @abstractmethod
    def ler_todos_arquivos(self):
        pass

    @abstractmethod
    def falhar_disco(self, disk_num):
        pass

    @abstractmethod
    def reconstruir_disco(self, disk_num):
        pass

    @abstractmethod
    def validar_paridade(self, disk_num):
        pass
#-------------------------------------------------------------------------------------------------------------------------------------------------------
#aqui é o controlador oficial, do RAID4
class ControladorRAID4:
    __metaclass__ = ControladorRAID #fazendo a herança dos dados da classe abstrata ControladorRAID
    disks = []
    arquivos = []

    def __init__(self, num_disks,
                 disk_cap=0):  # atribui um valor para a variavel do numero de disco e o máximo de disco.
        self.num_disks = num_disks
        self.disk_cap = disk_cap
        for i in range(num_disks):
            self.disks.append(Disco(i, disk_cap))

        # leitura do disco do inicio

    def __len__(self):
        return len(self.disks[0])
    def validar_disco(self, orig_disks=None):
        for i in range(len(self)):
            # Esse comando  Valida a paridade de um bloco removendo cada item em sequência, calculando a paridade dos itens restantes  e comparando o resultado com o item removido.
            self.validar_paridade(self.get_linhacd(i))
        if orig_disks is not None:
            for i in range(len(orig_disks)):
                if orig_disks[i] != self.disks[i]:
                    raise DiskReconstructException("Reconstrução de disco falhou: Disco " + repr(i) + " está corrompido")
    def get_linhacd(self, index):
        block = []
        for i in range(len(self.disks)):
            try:
                block.append(self.disks[i].read(index))
            except IndexError:
                print(
                    "Este erro é gerado quando o valor do índice fornecido é negativo ou excede o comprimento da sequência")
                pass
        return block
    def escreve_arquivo(self, arq):
        if len(self.arquivos) == 0: #arquivo vazio
            arq.start_addr = 0
        else:
            arq.start_addr = len(self) #arquivo não vazio

        self.arquivos.append(arq)
        blocks = list(split_data(arq.data_B, len(self.disks) - 1)) #separa os dados do arquivo em blocos
        arq.padding = (len(self.disks) - 1) - len(blocks[-1]) #separa os blocos um do outro, para n ficar um monte de número binário desorganizado
        self.escreve_parte(arq.data_B + [format(0, '#010b')] * arq.padding) #escreve o fragmento de texto no hd
    #Comando para validar se o conteúdo do disco é... válido
#!!!! repeti a parte acima pq n sei como fazer a herança de forma correta no python!!!
    #escreve uma sequencia de bits nos discos de RAID

    def escreve_parte(self,data):
        blocks = split_data(data, len(self.disks) - 1)
        for x in blocks:
        #Calcula o bit de paridade para o bloco x. Precisamos converter as strings bin em inteiros para usar a manipulação de bits para calcular o XOR
            parity_bit = self.calcular_paridade(x)
            self.validar_paridade(x + [format(parity_bit, bin_format)])
            parity_disk = self.calcular_paridade_disco(len(self))
        #O comando abaixo insire o bit de paridade no bloco na posição do disco de paridade atual
            x.insert(parity_disk, format(parity_bit, bin_format))
        # Escreve cada bloco de texto nos discos
            for i in range(len(x)):
                self.disks[i].write(x[i])
    #comando de ler a sequencia de bits nos discos de RAID, lendo todos os dados nos discos, ignorando bits de paridade e preenchimento. Não leva em conta discos ausentes.
    def ler_todos_dados(self):
        ret_str = ''
        for i in range(len(self)):
            for j in range(len(self.disks)):
                parity_disk = self.calcular_paridade_disco(i)
                if j != parity_disk:
                    ret_str += chr(int(self.disks[j].read(i), 2))  #Converte a string binária para inteiros, e depois para caracteres
            for k in range(len(self.arquivos)):
                if i == self.arquivos[k].start_addr - 1:
                    ret_str = ret_str[:len(ret_str) - self.arquivos[k - 1].padding]

        ret_str = ret_str[:len(ret_str) - self.arquivos[-1].padding]
        return ret_str
    #comando de ler todos os arquivos guardados nos discos de RAID
    def ler_todos_arquivos(self):
        ret_bits = []
        ret_arquivos = []
        for i in range(len(self)):
            for j in range(self.num_disks):
                parity_disk = self.calcular_paridade_disco(i)
                if j != parity_disk:
                    ret_bits.append(self.disks[j].read(i))
            for k in range(len(self.arquivos)):
                if i == self.arquivos[k].start_addr - 1:
                    ret_bits = ret_bits[:len(ret_bits) - self.arquivos[k - 1].padding]
                    ret_arquivos.append(ArquivosdeRAID.from_bits(k - 1, ret_bits))
                    ret_bits = []
        ret_bits = ret_bits[:len(ret_bits) - self.arquivos[-1].padding]
        ret_arquivos.append(ArquivosdeRAID.from_bits(self.arquivos[-1].id, ret_bits))
        return ret_arquivos
    #Simula uma falha de disco, por meio de uma remoção dele da lista
    def falhar_disco(self,disk_num):
        print('\033[31m'+"Disco " + repr(disk_num) + " falhou!!"+'\033[0m')
        del self.disks[disk_num]
    #Reconstroi o disco que foi falhado no comando acima
    def reconstruir_disco(self, disk_num):
        waiting_dots(3, message=('\033[32m'+"reconstruindo"+'\033[0m'), final_message="\033[31m"+"Completamente Reconstruido!"+"\033[0m'")
        if (self.num_disks - len(self.disks)) > 1:
            raise DiskReconstructException("Não foi possível reconstruir, muitos discos estão falhos e/ou ausentes!")

        new_disk = Disco(disk_num, self.disk_cap)
        for i in range(len(self.disks[0])):
            block = []
            for j in range(len(self.disks)):
                block.append(self.disks[j].read(i))
            self.validar_paridade(block + [format(self.calcular_paridade(block), bin_format)])

            new_disk.write(format(self.calcular_paridade(block), bin_format))
        self.disks.insert(disk_num, new_disk)
        self.validar_disco()
    #função para calcular o disco para armazenar bits de paridade para o bloco atual. No RAID-4 toda a paridade é armazenada em um único disco, então armazenamos no disco n-1
    def calcular_paridade_disco(self, index):
        return self.num_disks - 1
    #função para imprimir no terminal os dados em binário.
    def print_data(self):
        for x in self.disks:
            print("|   " + repr(x.disk_id) + "    ", end="")
        print("|")
        for i in range(len(self.disks)):
            print("---------", end="")
        print("-")
        for i in range(len(self.disks[0])):
            parity_disk = self.calcular_paridade_disco(i)
            for j in range(len(self.disks)):
                if i < len(self.disks[j]):
                    if self.disks[j].disk_id == parity_disk:
                        print("|" + self.disks[j].read(i)[2:], end="")
                        print(end="")
                    else:
                        print("|" + self.disks[j].read(i)[2:], end="")
                        print( end="")
            print("|", end="")
            for f in self.arquivos:
                if i == f.start_addr:
                    print("'\033[34m'<- Arquivo número:  " + repr(f.id)+'\033[0m', end="")
            print()
        print()
    #função para calcular o bit de paridade para o bloco. Precisamos converter as strings bin em inteiros para usar a manipulação de bits para calcular o XOR (já falei isso lá em cima ent n muda muita coisa.)
    @staticmethod
    def calcular_paridade(block):
        paridade_calculada = None
        for x in block:
            paridade_calculada = paridade_calculada ^ int(x, 2) if paridade_calculada is not None else int(x, 2)
        return paridade_calculada
    #Esse comando  Valida a paridade de um bloco removendo cada item em sequência, calculando a paridade dos itens restantes  e comparando o resultado com o item removido. (falei lá em cima tbm)
    @staticmethod
    def validar_paridade(block):
        for i in range(len(block)):
            parity = block.pop(i)
            calculated_parity = ControladorRAID4.calcular_paridade(block)
            if calculated_parity != int(parity, 2):
                raise ParityCalculationException(block, calculated_parity, int(parity, 2))
            block.insert(i, parity)
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#codigo da main aqui
arquivos = []
lista=[]
o=0
x=int(input("digite o número de discos (max 5)\n"))
y=int(input("digite o limite de discos (0 é o comum(ilimitado))\n"))
h=int(input("quantas frases a serem digitadas?\n"))
for o in range(0,h):
    z=input("Digite as frases a serem escritas\n")
    lista.append(' '+ z)

k=int(input("digite qual disco deve falhar.\n"))
falhartudo=int(input("quer falhar TODOS os discos? (0 pra não, 1 para sim)\n"))
m = bool(input("Deseja reconstruir o disco? True para sim e False(ou deixe em branco) pra não\n"))
pause = m
waiting_dots(6, message="\033[36m"+"configurando"+'\033[0m', final_message="terminado!")
def main():
#vou tentar fazer um código de Parser aqui pra ficar mais fácil a mudança dos dados, poderia ser feito pros outros argumentos, vou deixar comentado caso queira usar posteriomente
#👆 vou n


    num_disks=x
    disk_cap=y
    data = lista
    falha=k


    if disk_cap < 0:
        print("Capacidade do disco não pode ser menor que 0 bytes.")
    if falha >= num_disks:
        print ("não pode falhar o dico:  " + repr(falha) + ": Pois é um número invalido de disco")
    controller = ControladorRAID4(num_disks,disk_cap)
    #Escrever os arquivos no raid
    for i in range(len(data)):
        f = ArquivosdeRAID(i, data[i])
        arquivos.append(f)
        try:
            controller.escreve_arquivo(f)
        except DiskFullException as e:
            controller.print_data()
            sys.exit(e.msg)

    controller.print_data()
    print(controller.ler_todos_dados())
    orig_disks = list(controller.disks)

    if falhartudo==1:
        fail_disks(range(num_disks), controller, orig_disks, pause)
    else:
        fail_disks([falha], controller, orig_disks, pause)


    print(controller.ler_todos_dados())

def fail_disks(disks, controller, orig_disks, pause=False):
    for x in disks:
        controller.falhar_disco(x)
        controller.print_data()
        print(controller.ler_todos_dados())
        if pause==True:
            input("Pressione enter para continuar:(tem que pressionar 2x) \n ")
            controller.reconstruir_disco(x)
            controller.print_data()

        try:
            controller.validar_disco(orig_disks)
        except DiskReconstructException as e:
            print(e.msg)
main()
#usage = get_disk_usage() -> esses comandos pegam o hd do pc, e não fazem uma imagem da simulação
#plot_disk_usage(usage)
