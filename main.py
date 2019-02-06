from pandas import read_csv, Series, DataFrame
from re import findall, search

vesvoy_name = 'OC VesVoy' #'TO_VOYAGE'
ship_name = 'Name' #'VSL NAME'
cargo_name = 'Container' #['CONTAINER_ID']

cargos = {} #此处是cargo类与箱号的查询字典，直接用箱号查。包含一个数组，[0]为cargo类，[1]为毛重。
containers = [] #csv的每一行。
identities = {} #所有的id对应的container
myfilter = ['Name', 'OC VesVoy', 'Blno', 'Container', 'ML Seal', 'Size', 'Type', 'Gross weight', 'Net weight', 'Next Discharge', 'Operator', 'Temp_C', 'IMO', 'IMOCLS', 'UNNO', 'OOG front', 'OOG left', 'OOG rear', 'OOG right', 'OOG top']

class container: 
    def __init__(self, data):
        '''
            表格拆出来的类。
            container: 箱号
            vesvoy: 航次
            ship: 船名
            identity: 以船名+航次构成, 来分文本文档和表格。
            fromtext: 箱号所对应的cargo类，与netweight一起由cargo_list传入
            netweight: 毛重
            data: 表格中需要的部分, 传入全表格
        '''
        self.container = data['Container']
        identity = data['Name'] + ' ' + data['OC VesVoy']
        if identity in identities.keys():
            identities[identity].append(self)
        else:
            identities[identity] = [self]
        cargo_list = cargos[self.container]
        self.fromtext = cargo_list[0]
        self.netweight = cargo_list[1]
        self.data = self.process(data)
    
    def process(self, data):
        '''
        把数据修改并按顺序排列。
        '''
        newdata = {}
        for i in data.keys(): #找出不需要改的数据
            if i in myfilter:
                newdata[i] = data[i]
        if str(data['ML Seal']) != 'nan': #处理Seal
            newdata['ML Seal'] = data['ML Seal']
        elif str(data['Shipper Seal']) != 'nan':
            newdata['ML Seal'] = data['Shipper Seal']
        elif str(data['Customs Seal']) != 'nan':
            newdata['ML Seal'] = data['Customs Seal']
        else:
            newdata['ML Seal'] = ''
        newdata['Blno'] = self.fromtext.blno
        newdata['Net weight'] = self.netweight
        newdata['Next Discharge'] = newdata['Next Discharge'][0:5]
        return Series(newdata)

class cargo():
    def __init__(self, text):
        '''
            文本文档拆出来的类。
            text: 12-51全文本
            blno: 提单号 -> regex: ‘12:(.*?):’
            isadd: 是否被添加，默认False
            创建实例时向cargos字典添加自身所有的箱号
        '''
        self.text = text 
        self.blno = search('12:(.*?):', text).group(1)
        for i in findall("\n51:.*?'",text): #找51行
            container = search('51:[0-9]{3}:([A-Z]{4}[0-9]{7}[0]{0,1}):', i).group(1) #箱号
            netweight = round(float(search('51:.*?:.*?:.*?:.*?:.*?:.*?:(.*?):', i).group(1))) #毛重，删除前导零并四舍五入
            cargos[container] = [self, netweight]
        self.isadd = False

'''
读txt并处理
'''
txt = ''
with open('./file.txt', 'r') as f:
    txt = f.read()
head = txt.split('\n12')[0] #文本文档头
tail = '99' + txt.split('\n12')[-1].split('\n99')[1] #文本文档尾

for i in txt.split('\n12')[1 : ]:
    cargo(str('12' + i).split('\n99')[0])

'''
读csv并处理
'''
csv = read_csv('./file.csv')
for i in range(0, len(csv)):
    data = csv.iloc[i]
    if str(data['Name']) == 'nan':
        continue
    containers.append(container(data))

'''
输出txt
'''
for key in identities:
    text = head + '\n'
    for i in identities[key]:
        thiscargo = i.fromtext
        if thiscargo.isadd == False:
            text += thiscargo.text
    text = text + '\n' + tail
    with open(key + '.txt', 'w') as f:
        f.write(text)

'''
输出csv
'''
for key in identities:
    newcsv = DataFrame([i.data for i in identities[key]]).ix[:, myfilter]
    judges = ['Temp_C', 'IMOCLS', 'UNNO', 'OOG front', 'OOG left', 'OOG rear', 'OOG right', 'OOG top'] #按有无区分的
    flags = {'Temp_C': True, 'IMO': True, 'IMOCLS': True, 'UNNO': True, 'OOG front': True, 'OOG left': True, 'OOG rear': True, 'OOG right': True, 'OOG top': True}
    for i in range(0, len(newcsv)):
        for j in judges:
            if str(newcsv[j][i]) != 'nan' and str(newcsv[j][i]) != '0':
                flags[j] = False
        if str(newcsv['IMO'][i]) == 'Y':
            flags['IMO'] = False
    for i in flags:
        if flags[i]:
            newcsv.drop(columns=i, inplace=True)
    newcsv.rename(columns={'Blno': '提单号', 'Container': '箱号', 'ML Seal': 'SEAL NO.', 'Size': '尺寸', 'Type': '箱型', 'Gross weight': '毛重', 'Net weight': '总重', 'Next Discharge': '转运港', 'Operator': '箱主'}, inplace=True) 
    newcsv.to_csv(key+'.csv', encoding='ANSI')
