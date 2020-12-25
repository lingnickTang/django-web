import json
import time
import sys
from channels.generic.websocket import WebsocketConsumer

sys.path.append(r"D:\Download\Github\pipeline_sim_copy")
from global_variables import *


#fetch stage
##Part 1 Description from HCL file
def set_f_pc():
    global f_pc
    if M_icode == IJXX and not M_Cnd: f_pc = M_valA
    elif W_icode == IRET: 
        f_pc = W_valM
    else: f_pc = F_predPC


def set_f_icode():
    global f_icode
    if imem_error: f_icode = INOP
    else: f_icode = imem_icode

def set_f_ifun():
    global f_ifun
    if imem_error: f_ifun = FNONE
    else: f_ifun = imem_ifun
    
def set_instr_valid():
    global instr_valid
    instr_valid = f_icode in (INOP, IHALT, IRRMOVQ, IIRMOVQ, IRMMOVQ, IMRMOVQ, IOPQ, IJXX, ICALL, IRET, IPUSHQ, IPOPQ)
    
    if f_icode == IOPQ : instr_valid = f_ifun in range(4)
    elif f_icode == IJXX or f_icode == ICMOVXX : instr_valid = f_ifun in range(7)

def set_f_stat():
    global f_stat
    if imem_error: f_stat = SADR
    elif not instr_valid: f_stat = SINS
    elif f_icode == INOP: f_stat = SBUB
    elif f_icode == IHALT: f_stat = SHLT
    else: f_stat = SAOK

def set_need_regids():
    global need_regids
    need_regids = f_icode in (IRRMOVQ, IOPQ, IPUSHQ, IPOPQ, IIRMOVQ, IRMMOVQ, IMRMOVQ)

def set_need_valC():
    global need_valC
    need_valC = f_icode in ( IIRMOVQ, IRMMOVQ, IMRMOVQ, IJXX, ICALL)

def set_f_predPC():
    global f_predPC
    if f_icode in (IJXX, ICALL): f_predPC = f_valC
    else: f_predPC = f_valP


##Part 2 Description for immidiate num from text book pages which is undefined in HCL

def set_imem_icode_and_ifun():
    global imem_icode, imem_ifun
    if imem_error : return
    imem_icode = mem[f_pc] >> 4
    imem_ifun = mem[f_pc] - (imem_icode<<4)

def set_f_rA_rB_valC():
    global f_rA,f_rB,f_valC
    if imem_error: return
    cur_pc = f_pc+1
    if need_regids:
        f_rA = mem[cur_pc]>>4
        f_rB = mem[cur_pc] - (f_rA<<4)
    else:
        f_rA = RNONE
        f_rB = RNONE
    if need_valC:
        f_valC = 0
        for i in range(1,9):
            f_valC = (f_valC<<8) + mem[f_valP-i]
        if f_valC >> 63:
            f_valC = -((1<<64)-f_valC)
    

def set_imem_error_beginprog():
    global imem_error
    imem_error = 0   
    if f_pc >= 0x1000 or f_pc <0 or mem[f_pc] == -1: 
        imem_error = 1  

def set_imem_error_inprog():
    global imem_error
    if imem_error: return
    if -1 in mem[f_pc: f_valP] : imem_error = 1

def set_f_valP():
    global f_valP
    f_valP = f_pc + 1 + need_regids + 8*need_valC

#decode stage
##Part 1 Description from HCL file
def set_d_srcA():
    global d_srcA
    if D_icode in (IRRMOVQ, IRMMOVQ, IOPQ, IPUSHQ): d_srcA = D_rA
    elif D_icode in (IPOPQ, IRET): d_srcA = RRSP
    else: d_srcA = RNONE

def set_d_srcB():
    global d_srcB
    if D_icode in (IOPQ, IRMMOVQ, IMRMOVQ): d_srcB = D_rB
    elif D_icode in (IPUSHQ, IPOPQ, ICALL, IRET): d_srcB = RRSP
    else: d_srcB = RNONE

def set_d_dstE():
    global d_dstE
    if D_icode in (IRRMOVQ, IIRMOVQ, IOPQ): d_dstE = D_rB
    elif D_icode in (IPUSHQ, IPOPQ, ICALL, IRET): d_dstE = RRSP
    else: d_dstE = RNONE

def set_d_dstM():
    global d_dstM
    if D_icode in (IMRMOVQ, IPOPQ): d_dstM = D_rA
    else: d_dstM = RNONE

def set_d_valA():
    global d_valA
    if D_icode in (ICALL, IJXX): d_valA = D_valP
    elif d_srcA == e_dstE and not E_bubble: d_valA = e_valE
    elif d_srcA == M_dstM: d_valA = m_valM
    elif d_srcA == M_dstE: d_valA = M_valE
    elif d_srcA == W_dstM: d_valA = W_valM
    elif d_srcA == W_dstE: d_valA = W_valE
    else: d_valA = d_rvalA

def set_d_valB():
    global d_valB
    if d_srcB == e_dstE: d_valB = e_valE
    elif d_srcB == M_dstM: d_valB = m_valM
    elif d_srcB == M_dstE: d_valB = M_valE
    elif d_srcB == W_dstM: d_valB = W_valM
    elif d_srcB == W_dstE: d_valB = W_valE
    else: d_valB = d_rvalB

##Part 2 Description for immidiate num from text book pages which is undefined in HCL
def set_d_reg():
    global R
    R[W_dstE] = W_valE
    R[W_dstM] = W_valM

def set_d_rvalA():
    global d_rvalA
    d_rvalA = R[d_srcA]

def set_d_rvalB():
    global d_rvalB
    d_rvalB = R[d_srcB]

def set_d_stat():
    global d_stat
    d_stat = D_stat 

def set_d_icode():
    global d_icode
    d_icode = D_icode

def set_d_ifun():
    global d_ifun
    d_ifun = D_ifun

def set_d_valC():
    global d_valC
    d_valC = D_valC 

##Part 3 Description from extern variables or should be defined in other stages

#execute stage
##Part 1 HCL
def set_aluA():
    global aluA
    if E_icode in (IRRMOVQ, IOPQ) : aluA = E_valA
    elif E_icode in (IIRMOVQ, IRMMOVQ, IMRMOVQ) : aluA = E_valC
    elif E_icode in (ICALL, IPUSHQ) : aluA = -8
    elif E_icode in (IRET, IPOPQ) : aluA = 8

def set_aluB():
    global aluB
    if E_icode in (IRMMOVQ, IMRMOVQ, IOPQ, ICALL, IPUSHQ, IRET, IPOPQ): aluB = E_valB
    elif E_icode in (IRRMOVQ, IIRMOVQ): aluB = 0

def set_alufun():
    global alufun
    if E_icode == IOPQ : alufun = E_ifun
    else : alufun = ALUADD

def set_set_cc():
    global set_cc
    set_cc = E_icode == IOPQ and not m_stat in (SADR, SINS, SHLT) and not W_stat in (SADR, SINS, SHLT)

def set_e_valA(): #pass valA through stage to connect the previous and the next stage
    global e_valA
    e_valA = E_valA

def set_e_dstE():
    global e_dstE
    if E_icode == IRRMOVQ and not e_Cnd : e_dstE = RNONE
    else: e_dstE = E_dstE 

##Part 2
def set_e_stat():
    global e_stat
    e_stat = E_stat

def set_e_icode():
    global e_icode
    e_icode = E_icode

def set_e_Cnd():
    global e_Cnd, ifun_error
    if E_ifun == 0 : e_Cnd = 1
    elif E_ifun == 1: e_Cnd = (SF^OF) or ZF
    elif E_ifun == 2: e_Cnd = SF^OF
    elif E_ifun == 3: e_Cnd = ZF
    elif E_ifun == 4: e_Cnd = not ZF
    elif E_ifun == 5: e_Cnd = not (SF^OF)
    elif E_ifun == 6: e_Cnd = not (SF^OF) and not ZF
    else:ifun_error = 1

def set_e_dstM():
    global e_dstM
    e_dstM = E_dstM

def set_e_valE():
    global e_valE, ifun_error
    if alufun == ALUADD: e_valE = aluB + aluA
    elif alufun == ALUSUB: e_valE = aluB - aluA
    elif alufun == ALUAND: e_valE = aluB & aluA
    elif alufun == ALUXOR: e_valE = aluB ^ aluA
    else : ifun_error = 1
        
def set_CC():
    global ZF,SF,OF
    if set_cc:  #need to update CC 对于有符号溢出
        ZF = (e_valE == 0)
        SF = (e_valE < 0)
        OF = (aluA < 0 == aluB < 0) and (e_valE < 0 != aluA < 0)

#memory stage
##Part 1 HCL
def set_mem_addr():
    global mem_addr
    if M_icode in (IRMMOVQ, IPUSHQ, ICALL, IMRMOVQ) :
        mem_addr = M_valE
    elif M_icode in (IPOPQ, IRET):
        mem_addr = M_valA

def set_mem_read():
    global mem_read
    mem_read = M_icode in (IMRMOVQ, IPOPQ, IRET)

def set_mem_write():
    global mem_write
    mem_write = M_icode in (IRMMOVQ, IPUSHQ, ICALL)

def set_m_stat():
    global m_stat
    if dmem_error : m_stat = SADR
    else: m_stat = M_stat

##Part 2 text book
def set_m_valE():
    global m_valE
    m_valE = M_valE

def set_m_dstE():
    global m_dstE
    m_dstE = M_dstE

def set_m_dstM():
    global m_dstM
    m_dstM = M_dstM

def set_dmem_error():
    global dmem_error
    dmem_error = 0
    if mem_read:
        if mem_addr+7 > 0x1000 or mem_addr < 0:
            dmem_error = 1
        if -1 in mem[mem_addr:mem_addr+8]:
            dmem_error = 1
    if mem_write:
         if mem_addr+7 > 0x1000 or mem_addr < 0:
            dmem_error = 1

def read_dmem():
    global m_valM
    m_valM = M_valA
    if dmem_error or not mem_read:return
    m_valM = 0
    i = 1
    while i <= 8:
        m_valM = (m_valM<<8) + mem[mem_addr+8-i]
        i += 1
    if m_valM>>63:                 
        m_valM = -((1<<64)-m_valM)

def write_dmem():
    global mem
    if dmem_error or not mem_write: return
    tmp = M_valA
    for i in range(8):
        mem[mem_addr+i] = tmp & 0xff
        tmp >>= 8

def set_m_icode():
    global m_icode
    m_icode = M_icode

#write back stage
def set_w_dstE():
    global w_dstE
    w_dstE = W_dstE

def set_w_valE():
    global w_valE
    w_valE = W_valE

def set_w_dstM():
    global w_dstM
    w_dstM = W_dstM 

def set_w_valM():
    global w_valM
    w_valM = W_valM 

def set_Stat():
    global Stat,program_out
    if W_stat == SBUB : Stat = SAOK
    else : Stat = W_stat
    if Stat != SAOK:
        program_out = 1

#pipeline register control
def set_F_bubble():
    global F_bubble
    F_bubble = 0

def set_F_stall():
    global F_stall
    F_stall = E_icode in (IMRMOVQ, IPOPQ) and E_dstM in (d_srcA, d_srcB) or IRET in (D_icode, E_icode, M_icode)

def set_D_stall():
    global D_stall
    D_stall = E_icode in (IMRMOVQ, IPOPQ) and E_dstM in (d_srcA, d_srcB)

def set_D_bubble():
    global D_bubble
    D_bubble = (E_icode == IJXX and not e_Cnd) or not (E_icode in (IMRMOVQ, IPOPQ) and E_dstM in (d_srcA, d_srcB)) and IRET in (D_icode, E_icode, M_icode)

def set_E_stall():
    global E_stall
    E_stall = 0

def set_E_bubble():
    global E_bubble
    E_bubble = (E_icode == IJXX and not e_Cnd) or E_icode in (IMRMOVQ, IPOPQ) and E_dstM in (d_srcA, d_srcB)

def set_M_stall():
    global M_stall
    M_stall = 0

def set_M_bubble():
    global M_bubble
    M_bubble = m_stat in (SADR, SINS, SHLT) or W_stat in (SADR, SINS, SHLT)

def set_W_stall():
    global W_stall
    W_stall = W_stat in (SADR, SINS, SHLT)

def set_W_bubble():
    global W_bubble
    W_bubble = 0

#define set_reg_and_immu
def set_F_reg():
    global F_predPC
    if F_stall: return
    F_predPC = f_predPC

def set_f_imme():
    set_f_pc()
    set_imem_error_beginprog()
    set_imem_icode_and_ifun()
    set_f_icode()
    set_f_ifun()
    set_instr_valid()
    set_need_regids()
    set_need_valC()
    set_f_valP()
    set_imem_error_inprog()
    set_f_rA_rB_valC()
    set_f_predPC()
    set_f_stat()

def set_D_reg():
    global D_stat, D_icode, D_ifun, D_rA, D_rB, D_valC, D_valP
    if D_stall: return
    D_icode = f_icode 
    D_stat = f_stat
    if D_bubble: 
        D_stat = SBUB
        D_icode = INOP
    if D_stat != SAOK: return

    D_ifun = f_ifun  
    D_rA = f_rA 
    D_rB = f_rB 
    D_valC = f_valC 
    D_valP = f_valP 

def set_d_imme():
    set_d_reg()
    set_d_stat()
    set_d_icode()

    if d_stat != SAOK:
        return

    set_d_ifun()
    set_d_dstE()  
    set_d_dstM()
    set_d_srcB()
    set_d_srcA()
    set_d_rvalA()
    set_d_rvalB()
    set_d_valA()
    set_d_valB()
    set_d_valC()


def set_E_reg():
    global E_stat, E_icode, E_ifun, E_valC, E_valA, E_valB, E_dstE, E_dstM, E_srcA, E_srcB
    E_stat = d_stat
    E_icode = d_icode
    if E_bubble: 
        E_stat = SBUB
        E_icode = INOP
    if E_stat != SAOK: return

    E_ifun = d_ifun
    E_valC = d_valC
    E_valA = d_valA
    E_valB = d_valB
    E_dstE = d_dstE
    E_dstM = d_dstM
    E_srcA = d_srcA
    E_srcB = d_srcB

def set_e_imme():
    set_e_stat()
    set_e_icode()
    if e_stat != SAOK: return

    set_aluA()
    set_aluB()
    set_alufun()
    set_set_cc()
    set_e_valE()
    set_CC()
    set_e_Cnd()
    set_e_valA()
    set_e_dstE()
    set_e_dstM()

def set_M_reg():
    global M_stat, M_icode, M_Cnd, M_valE, M_valA, M_dstE, M_dstM

    M_stat = e_stat
    M_icode = e_icode
    if M_bubble: 
        M_stat = SBUB
        M_icode = INOP
    if M_stat != SAOK:return

    M_Cnd = e_Cnd 
    M_valE = e_valE
    M_valA = e_valA
    M_dstE = e_dstE
    M_dstM = e_dstM

def set_m_imme():
    global m_stat
    set_m_icode()
    if M_stat != SAOK:
        m_stat = M_stat
        return
    set_mem_read()
    set_mem_write()
    set_mem_addr()
    set_dmem_error()
    read_dmem()
    write_dmem()
    set_m_valE()
    set_m_dstE()
    set_m_dstM()
    set_m_stat()

def set_W_reg():
    global W_stat, W_icode, W_valE, W_valM, W_dstE, W_dstM
    if W_stall: return

    W_stat = m_stat
    W_icode = m_icode
    W_valE = m_valE
    W_valM = m_valM
    W_dstE = m_dstE
    W_dstM = m_dstM

def set_w_imme():  
    set_w_dstE()
    set_w_valE()
    set_w_dstM()
    set_w_valM()
    set_Stat()

def set_bubble_and_stall():
    set_F_bubble()
    set_F_stall()
    set_D_bubble()
    set_D_stall()
    set_E_bubble()
    set_E_stall()
    set_M_bubble()
    set_M_stall()
    set_W_bubble()
    set_W_stall()
#end definition

def initial():
    global program_out,R,mem
    global W_stat, W_icode, W_valE, W_valM, W_dstE, W_dstM
    global M_stat, M_icode, M_Cnd, M_valE, M_valA, M_dstE, M_dstM
    global E_stat, E_icode, E_ifun, E_valC, E_valA, E_valB, E_dstE, E_dstM, E_srcA, E_srcB
    global D_stat, D_icode, D_ifun, D_rA, D_rB, D_valC, D_valP
    global F_predPC
    global ZF,SF,OF,Stat

    W_icode, W_valE, W_valM, W_dstE, W_dstM = (0 for i in range(5))
    M_icode, M_Cnd, M_valE, M_valA, M_dstE, M_dstM = (0 for i in range(6))
    E_icode, E_ifun, E_valC, E_valA, E_valB, E_dstE, E_dstM, E_srcA, E_srcB = (0 for i in range(9))
    D_icode, D_ifun, D_rA, D_rB, D_valC, D_valP = (0 for i in range(6))

    for i in range(16): R[i] = 0
    for i in range(0x1000): mem[i] = 0
    program_out = 0
    F_predPC = 0x000
    Stat, D_stat, E_stat, M_stat, W_stat = SBUB, SBUB, SBUB, SBUB,SBUB
    ZF,SF,OF = -1,-1,-1

 #路径考虑清楚
       
def singleRun():
    if not program_out:

        set_w_imme()
        set_m_imme()
        set_e_imme()
        set_d_imme()
        set_f_imme()

        set_bubble_and_stall()
        
        set_W_reg()
        set_M_reg()
        set_E_reg()
        set_D_reg()
        set_F_reg()

    return 1
        #waste += D_bubble or E_bubble or F_stall or D_bubble 
        #print("circles:",clock,"instruction:",clock-waste,"CPI:",clock/(clock-waste))

def input(inputData:str):
    global mem
    initial()
    if(len(inputData) <= 3): return 0
    dataList = inputData.split('\n')
    try:
        for each_line in dataList:
            instr_line = each_line.split('|')[0]
            if len(instr_line) == 0: continue
            if(instr_line[0] != ' ' and instr_line[0] != '\t'):
                addr_tar = instr_line.split(':')
                begin_address = int(addr_tar[0],16)        #把16进制的字符串变成数字
                target  = addr_tar[1]
                index = 0
                while target[2*index+1] != ' ' and target[2*index+1] != '\t':
                    mem[begin_address+index] = int(target[2*index+1:2*index+3],16)
                    index += 1
                '''
            for i in range(index):
                print("%x" % mem[begin_address+i],end=' ')
            print()
    print() 
'''
    except:
        return 0
    else:
        return 1

class IDEConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        isData = text_data_json['isData']
        if isData:
            data = text_data_json['inputData']
            isValid = input(data)
        else:
            interval = text_data_json['interval']
            time.sleep(interval)
            isValid = singleRun()
        self.sendData(isValid)

    def sendData(self, isValid):
        self.send(text_data=json.dumps({

            "isValid": isValid,

            "rax": hex(R[0]), "rcx": hex(R[1]), "rdx": hex(R[2]),
            "rbx": hex(R[3]), "rsp": hex(R[4]), "rbp": hex(R[5]),
            "rsi": hex(R[6]), "rdi": hex(R[7]), "r8": hex(R[8]),
            "r9": hex(R[9]), "r10": hex(R[10]), "r11": hex(R[11]),
            "r12": hex(R[12]), "r13": hex(R[13]), "r14": hex(R[14]),

            "W_stat": S[W_stat], "W_icode":hex(W_icode), "W_valE":hex(W_valE), "W_valM":hex(W_valM), "W_dstE":W_dstE,"W_dstM":W_dstM,
            "M_stat": S[M_stat], "M_icode":hex(M_icode), "M_Cnd":M_Cnd, "M_valE":hex(M_valE), "M_valA":hex(M_valA), "M_dstE":M_dstE,"M_dstM":M_dstM,
            "E_stat": S[E_stat], "E_icode":hex(E_icode), "E_ifun":hex(E_ifun), "E_valC":hex(E_valC),"E_valA":hex(E_valA), "E_valB":hex(E_valB), "E_dstE":E_dstE,"E_dstM":E_dstM,"E_srcA":E_srcA,"E_srcB":E_srcB,
            "D_stat": S[D_stat], "D_icode":hex(D_icode), "D_ifun":hex(D_ifun),"D_rA":hex(D_rA),"D_rB":hex(D_rB), "D_valC":hex(D_valC),"D_valP":hex(D_valP),
            "F_predPC": hex(F_predPC),

            "ZF":str(ZF), "SF":str(SF), "OF":str(OF),
            "Stat":S[Stat],

            "program_out":program_out,
        }))
