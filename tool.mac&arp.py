#tool v2.0
import re,sys,getopt
import pandas as pd
#=========================定义正则表达式关键字================================
ip='[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*'
macCisco='([0-9a-fA-F]{4}\.){2}[0-9a-fA-F]{4}'
macHW='([0-9a-fA-F]{4}-){2}[0-9a-fA-F]{4}'
begenvoidnum='^\s\s*\d\d*\s*'
# intname='[a-zA-Z]*(\d/)+\d+'
intname='[a-zA-Z]*\d+'

def usage():
    print('\n使用说明:    \n')
    print('本工具用于将网络设备log中的arp表和mac地址表抓取并链接查询，合并成一张拥有ip mac port vlan的excel表格。\n避免寻找ip、mac和设备物理端口之间关联关系时的大量重复劳动')
    print('      -a      :指定含有ARP信息的文本')
    print('      -m      :指定含有MAC地址信息的文本')
    print('      -c      :指定MAC地址文件为Cisco')
    print('      -h      :指定MAC地址文件为HuaWei\n')
    print('  example:\n')
    print('      python test.py -a <inputfile_ARP.txt> -m <inputfile_MAC.txt> -c\n')
    print('  输入文件须为文本，扩展名可以是.txt.log等\n  处理后的excel文件将存放在<inputfile_MAC>路径下\n  如有报错，则需要使用pip install pandas 和 pip install openpyxl用于输出excel文件')

#=========================convert方法，遍历txt转换成Excel=======================
def convert(inputArp,inputMac,macXX):
    arpKey=r'\s*\Dnternet\s*'+ip+'\s*'+'.*'+'\s*'+macXX+'\s*ARPA\s*Vlan[0-9]*'
    macKey=begenvoidnum+macXX+'\s*'+'.*'+intname

    dfArp=pd.DataFrame(columns=['Address','Age','MAC','Type','Interface'])
    dfMac=pd.DataFrame(columns=['Vlan','MAC','Type','Int'])
    file0=open(inputArp,encoding='utf-8')
    #匹配ARP表
    for s in file0.readlines():
        match = re.search(arpKey,s)
        if match:
            s=match.group(0)
            #去除换行符
            if s[-1] == '\n':
                s = s[:-1]
            #分列建行，追加到表
            info=re.split(r'\s+',s)
            dic = {
                #Cisco文本里会多一个无意义项，因此从第[1]个元素开始取值
                'Address': info[1],
                'Age': info[2],
                'MAC': info[3],
                'Type': info[4],
                'Interface': info[5],
            }
            dfArp=dfArp.append(dic,ignore_index=True)
    file0.close()

    #匹配MAC地址表
    file1=open(inputMac,encoding='utf-8')
    for s in file1.readlines():
        match = re.search(macKey,s)
        if match:
            s=match.group(0)
            #去除换行符
            if s[-1] == '\n':
                s = s[:-1]
            #分列建行，追加到表
            info=re.split(r'\s+',s)
            dic = {
                'Vlan': info[1],
                'MAC': info[2],
                'Type': info[3],
                'Int': info[-1],    #某些版本存在多个无意义项，因此只取最后一个元素
            }
            dfMac=dfMac.append(dic,ignore_index=True)
            # dfMac.to_excel(inputMac+'.AAAA.xlsx',index=False)
        else:
            continue
    file1.close()
    dfOut = pd.merge(dfMac,dfArp,on='MAC',how='left')
    dfOut.to_excel(inputMac+'.Convert.xlsx',index=False)

def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],'a:m:ch3')
    except getopt.GetoptError:
        usage()
        sys.exit(3)
    for opt,filename in opts:
        if opt == '-a':
            inputArp=filename
        elif opt =='-m':
            inputMac=filename
        elif opt =='-c':       
            version='verC'    
            convert(inputArp,inputMac,macCisco)
        elif opt =='-h':
            version='verHW'
            convert(inputArp,inputMac,macHW)    
main()