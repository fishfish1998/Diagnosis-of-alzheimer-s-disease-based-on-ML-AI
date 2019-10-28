
# coding: utf-8

# In[82]:


from aip import AipNlp
import codecs
import paramiko
import jieba
import time
import pandas as pd


# In[83]:


hostname='127.11.173.184'
port=22
username='hzm123'
password='Adobe20160706'
APP_ID = "17356269"
API_KEY = "G21lPBZCaaXbaQcU3vkwHL8S"
SECRET_KEY = "4Lou8RcG8Av6YGxE7qBijeCT2WcdeTm1"
cri=['VOB','SBV','CMP']


# In[84]:


def connection(hostname,port,username,password):
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname,port=port,username=username,password=password)
    transport = paramiko.Transport((hostname,port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return ssh,sftp


# In[85]:


def in_sen(sentence):
    f = codecs.open('test.txt','w+',encoding='utf-8')#必须事先知道文件的编码格式，这里文件编码是使用的utf-8 
    #sentence=input('请输入一句话：');
    sentence=sentence;
    sentence1=jieba.cut(sentence)
    sentence2=jieba.cut(sentence)
    f.write(' '.join(sentence1)) 
    f.close()
    ss=[]
    for s in sentence2:
        ss.append(s)
    num=len(ss)
    return num


# In[86]:


def cal_ppl(ssh,sftp,num):
    ssh=ssh;sftp=sftp;
    try:
        sftp.put('test.txt','/home/hzm123/test.txt')
    except:
        client=connection(hostname,port,username,password); ssh=client[0];sftp=client[1];
    cmd1='export PATH=$PATH:/home/hzm123/srilm;export PATH=$PATH:/home/hzm123/srilm/bin/i686-m64/;echo $PATH;ngram -ppl test.txt -debug 1 -order 3 -lm my.lm &>> result.txt'
    cmd2='rm test_ljq.txt'
    cmd3='rm result.txt '
    stdin, stdout, stderr = ssh.exec_command(cmd1)

    time.sleep(30)
    sftp.get('/home/hzm123/result.txt','result.txt')
    stdin, stdout, stderr = ssh.exec_command(cmd2)
    stdin, stdout, stderr = ssh.exec_command(cmd3)
    
    f_p1=codecs.open('result.txt','r+',encoding='utf-8') 
    lines = f_p1.readlines()     
    f_p1.close()
    
    i1=lines[5].find('ppl')
    i2=lines[5].find('ppl1')
    #print(i1,i2)
    #print(float(lines[5][i1+5:i2-1]))
   
    ppl=float(lines[5][i1+5:i2-1])/num
    return ppl
    


# In[87]:


def meaning(sentence,ssh,sftp):
    sentence=sentence;ssh=ssh;sftp=sftp;
    num=in_sen(sentence);
    ppl=cal_ppl(ssh,sftp,num);
    return ppl


# In[88]:


def syntax(sentence):
    client_syn= AipNlp(APP_ID, API_KEY, SECRET_KEY)
    struc=client_syn.depParser(sentence)
    li=pd.DataFrame(struc['items'])
    core=li[li['deprel']=='HED'].id
    test=li[li['head']==int(core)]['deprel'].values
    test=test.tolist()
    ingre_test=set(test).intersection(set(cri))
    if ingre_test:
        return True
    else:
        return False


# In[89]:


if __name__ == "__main__":
    try:
        client=connection(hostname,port,username,password); ssh=client[0];sftp=client[1];
    except:
        print("连接失败，请检查服务器状态")
    sentence=input('请输入一句话：');
    ppl=meaning(sentence,ssh,sftp)
    syn=syntax(sentence)
    if ppl<1100 and syn:
        print("您写的句子是可理解的")
    else:
        print("抱歉，您写的句子不能被理解：")
        if syn==False:
            print("句子缺少成分")
        if ppl>=1100:
            print("句子意思不明确，困惑度为：",ppl)


# In[ ]:




