#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2014年7月22日

@author: zhouzhichao
'''

import random
try:
    import Image, ImageDraw
except ImportError as e:
    from PIL import Image, ImageDraw


INF = float('inf')
CHARN, CHARB ='□', '■'
NBP, BBP = -1,0 #False, True
BPARR=(BBP, NBP)

dataCoding = 'utf-8'
outputDir = '../../output'



from galois import GaloisField
from bchcode import BCHCoder
from bitutil import xbin, strXor


class QRDataEncoder(object):
    GF      = GaloisField(module = 0x11d)
    ModeSupported = ('digit', 'alphadigit', 'kanji', 'chinese', '8-bit')
    def __init__(self, version = 1, mode=None):
        self.version = version
        self.mode    = '8-bit'
        self.setMode(mode)
    def setMode(self, name):
        if name in QRDataEncoder.ModeSupported:
            self.mode = name            
    @staticmethod
    def chooseMode(content):
        '''
            为指定内容选取编码模式
        '''
        if isinstance(content, float):
            return 'alphadigit'
        if isinstance(content, int):
            return 'digit'
        if isinstance(content, str):
            content = content.decode(dataCoding)

        filters = {'digit':     QRDataEncoder.isEncodableInDigit,
                   'alphadigit':QRDataEncoder.isEncodableInAlphadigit,
                   'kanji':     QRDataEncoder.isEncodableInKanji
        }

        for mode in ('digit', 'kanji'):#, 'alphadigit'  not in use
            OK, func = True, filters[mode]
            for x in content:
                if not func(x):
                    OK = False
                    break
            if OK: 
                return mode
        return '8-bit'
            
    @staticmethod
    def isEncodableInDigit(x):
        '''
            判断字符x是否是0-9的数字
        '''
        return 0x30<=ord(x)<=0x39
    @staticmethod
    def isEncodableInAlphadigit(x):
        '''
            判断字符x是否是字母或数字
        '''
        x = ord(x)
        return x != 0x2c and (0x2a<=x<=0x39 or 0x40<=x<0x5a or 0x60<=x<0x7a or x in (0x20, 0x24, 0x25))
    @staticmethod
    def isEncodableInKanji(x):
        '''
            判断字符x是否是汉字
        '''
        try:
            ochar = x.encode('gbk')
            char = [ord(ochar[0]), ord(ochar[1])]
        except:
            return False
        if 0xA1<=char[1]<=0xFE:
            return 0xA1<=char[0]<=0xAA or 0xB0<=char[0]<=0xFA
        return False        
    def getTagCode(self, name=None):
        dataList = {'eci':'0111',   'digit':'0001', 'alphadigit':'0010',
                    '8-bit':'0100', 'kanji':'1101', 'link':'0011',
                    'fnc1':'0101',  'fnc1.':'1001', 'end':'0000',
                    'chinese':'1101'
                    }
        if not name:
            name = self.mode 
        name = name.lower()
        return dataList.get(name)
    def isFitVersion(self, ver):
        if 1<=ver<=40:
            ver, versec = (ver+7)/17, (self.version+7)/17
            return ver-versec
        return None
    def shiftVersion(self,verdiff):
        self.version += 17*verdiff
    @staticmethod
    def fillContent(data, length):
        ldata = len(data)
        rest = ldata % 8
        ldata /= 8
        if rest != 0: 
            data += '0'*(8-rest)
            ldata += 1
        if length > ldata:
            length -= ldata
            ll = length / 2
            data += '1110110000010001' * ll
            if length % 2: data += '11101100'
        return data
    @staticmethod
    def getLenOfMarkLen(version, mode):
        mode = mode.lower()
        if mode in ('digit', 'alphadigit', 'chinese','kanji'):
            return int((version+7)/17)*2 + {'d':10,'a':9,'c':8,'k':8}[mode[0]]
        if mode == '8-bit':
            return 8 if version<10 else 16
        else:
            return 0
    def getLengthMarkLen(self, mode=None):
        if not mode: 
            mode = self.mode
        return QRDataEncoder.getLenOfMarkLen(self.version, mode)
    def encodeInDigitMode(self, content):
        mode, leng = 'digit', len(content)

        gumi, data = leng/3, ''
        for i in xrange(gumi):
            i = i*3
            text = content[i:i+3]
            data += xbin(text,10)
        rest = leng % 3
        if rest > 0:
            data += xbin(content[-rest:], 3*rest+1)
        # byte counter begin
        lml = self.getLengthMarkLen(mode)
        data = xbin(leng, lml) +data
        data = self.getTagCode(mode)+ data
        assert len(data) == 4+lml+10*gumi+3*rest+(1 if rest else 0)
        return data
    def assumeLenDigitMode(self, content):
        leng = len(content)
        gumi, rest = leng / 3, leng % 3         
        return 4+self.getLengthMarkLen('digit')+10*gumi+(0,4,7)[rest]
    def encodeInAlphaDigitMode(self, content):
        def getADIndex(char):
            asc = ord(char)
            if 0x30<=asc<0x39:
                value = asc-0x30
            elif 0x41<=asc<=0x5A:
                value = asc-0x37 #asc-0x41+10
            else:
                value = ' $%*+-./'.index(char) + 36
            return value
        mode, leng, content = 'alphadigit', len(content), content.upper()
        gumi, lml = leng/2, self.getLengthMarkLen(mode)
        data = self.getTagCode(mode)+xbin(leng, lml) 
        for i in xrange(gumi):
            i *= 2
            text = content[i:i+3]
            value = getADIndex(text[0]) * 45 + getADIndex(text[1])
            data += xbin(value,11)
        rest = leng % 2
        if rest > 0:
            data += xbin(getADIndex(content[-1]), 6)
        assert len(data) == 4 + lml + 11*gumi + 6*rest
        return data 
    def assumeLenAlphaDigitMode(self, content):
        leng = len(content)
        gumi, rest = leng / 2, leng % 2  
        return 4 + self.getLengthMarkLen('alphadigit') + 11*gumi + 6*rest
    def encodeIn8BitMode(self, content):
        mode = '8-bit'
        leng, lml = len(content), self.getLengthMarkLen(mode)
        data = self.getTagCode(mode) + xbin(leng, lml)
        for i in content:
            data += xbin(ord(i), 8)        
        assert len(data) == 4+lml+8*leng
        return data
    def assumeLen8BitMode(self, content):
        return 4+self.getLengthMarkLen('8-bit')+8*len(content)
    def encodeInKanjiMode(self, content):
        def translate(char):
            ochar = char.encode('gbk')
            char = [ord(ochar[0]), ord(ochar[1])]
            if 0xA1<=char[0]<=0xAA and 0xA1<=char[1]<=0xFE:
                value = (char[0]-0xA1)*0x60+(char[1]-0xA1) 
            elif 0xB0<=char[0]<=0xFA and 0xA1<=char[1]<=0xFE:
                value = (char[0]-0xA6)*0x60+(char[1]-0xA1)
            else:
                value = 64
            return xbin(value, 13) 
        mode, content = 'kanji', content.decode(dataCoding)
        leng, lml = len(content), self.getLengthMarkLen(mode)
        data = self.getTagCode(mode) +'0001'+ xbin(leng, lml) 
        for i in content:
            data += translate(i)
        assert len(data) == 8+lml+13*leng
        return data
    def assumeLenKanjiMode(self, content):
        return 8+self.getLengthMarkLen('kanji')+13*len(content.decode(dataCoding))
    def assumeLength(self, content):
        funcs= {'alphadigit': self.assumeLenAlphaDigitMode, 
                '8-bit':      self.assumeLen8BitMode,
                'digit':      self.assumeLenDigitMode,
                'kanji':      self.assumeLenKanjiMode,
                'chinese':    self.assumeLenKanjiMode
                }
        return funcs[self.mode](content)
    def encodeData(self, content):
        funcs= {'alphadigit': self.encodeInAlphaDigitMode, 
                '8-bit':      self.encodeIn8BitMode,
                'digit':      self.encodeInDigitMode,
                'kanji':      self.encodeInKanjiMode,
                'chinese':    self.encodeInKanjiMode
                }
        return funcs[self.mode](content)
    def encode(self, content):
        pass
    
    # def getRates(self, pn): #Galois field  
    #     if pn < 1: return    
    #     result = [0] * (pn + 1)
    
    #     for k in xrange(1, pn):
    #         for i in xrange(k, 0, -1):
    #             result[i] = self.GF.add(result[i] + k, result[i-1])
    #         result[0] += k
    #     result[0] = self.GF.mod(result[0])
    #     return result          
    
    def encodeCheckCode(self, data, length):
        # rates = map(lambda x: self.GF.getValue(x), self.getRates(length))
        rates = QRDataEncoder.GF.getRates(length)
        # rates = self.GF.encodeRates(length)
        buf = [0] * length
        ldata = len(data) // 8        
        for i in xrange(ldata):
            elem = eval('0b'+data[8*i: 8*i+8])
            busbuf = buf[-1] ^ elem
            for j in xrange(length-1, -1, -1):
                # j = length-1-j
                # tmp = self.GF.mul(busbuf, rates[j])
                tmp = QRDataEncoder.GF.mul(busbuf, rates[j])
                if j > 0:
                    buf[j] = buf[j-1] ^ tmp
                else:
                    buf[j] = tmp 
        return ''.join(map(lambda x: xbin(x,8), buf[::-1]))

    def encodeBlocksCheckCode(self, data, pieces):
        idx, result = 0, []
        for pair in pieces:
            datalen = pair[0]-pair[2]
            for _ in xrange(pair[1]):          
                msg = data[idx*8: 8*(idx+datalen)]
                result.append(msg + self.encodeCheckCode(msg, pair[2]))
                idx += datalen
        return result 
    



class QRMaster(object):
    '''
        LMQH四个等级的分块数
    '''
    LMQH_BlockList=((0,0,0,0),
                    (1,1,1,1),      #1
                    (1,1,1,1),      #2
                    (1,1,2,2),      #3
                    (2,1,4,2),      #4
                    (2,1,4,4),
                    (4,2,4,4),
                    (4,2,5,6),
                    (4,2,6,6),
                    (5,2,8,8),
                    (5,4,8,8),      #10
                    (5,4,11,8),
                    (8,4,11,10),
                    (9,4,16,12),
                    (9,4,16,16),
                    (10,6,18,12),
                    (10,6,16,17),
                    (11,6,19,16),
                    (13,6,21,18),
                    (14,7,25,21),
                    (16,8,25,20),   #20
                    (17,8,25,23),
                    (17,9,34,23),
                    (18,9,30,25),
                    (20,10,32,27),
                    (21,12,35,29),
                    (23,12,37,34),
                    (25,12,40,34),
                    (26,13,42,35),
                    (28,14,45,38),
                    (29,15,48,40),  #30
                    (31,16,51,43),
                    (33,17,54,45),
                    (35,18,57,48),
                    (37,19,60,51),
                    (38,19,63,53),
                    (40,20,66,56),
                    (43,21,70,59),
                    (45,22,74,62),
                    (47,24,77,65),
                    (49,25,81,68))  #40
    '''
        LMQH四个等级的分块的校验码字节数
    '''
    Check_Length = ((0,0,0,0),
                    (10,7,17,13),   #1
                    (16,10,28,22),  #2
                    (26,15,22,18),  #3
                    (18,20,16,26),  #4
                    (24,26,22,18),
                    (16,18,28,24),
                    (18,20,26,18),
                    (22,24,26,22),
                    (22,30,24,20),
                    (26,18,28,24),  #10
                    (30,20,24,28),
                    (22,24,28,26),
                    (22,26,22,24),
                    (24,30,24,20),
                    (24,22,24,30),
                    (28,24,30,24),
                    (28,28,28,28),
                    (26,30,28,28),
                    (26,28,26,26),
                    (26,28,28,30),  #20
                    (28,30,28,26),
                    (28,28,24,30),
                    (28,30,30,30),
                    (28,30,30,30),
                    (28,26,30,30),
                    (28,28,30,28),
                    (28,30,30,30),  #27 之后都是(28,30,30,30)
                    (28,30,30,30),
                    (28,30,30,30),
                    (28,30,30,30),  #30
                    (28,30,30,30),
                    (28,30,30,30),
                    (28,30,30,30),
                    (28,30,30,30),
                    (28,30,30,30),
                    (28,30,30,30),
                    (28,30,30,30),
                    (28,30,30,30),
                    (28,30,30,30),
                    (28,30,30,30))  #40
    '''
        Mask掩模生成函数
    '''
    MaskFuncsList = ((lambda x,y: (x+y)%2==0),
                    (lambda x,y: x%2==0),
                    (lambda x,y: y%3==0),
                    (lambda x,y: (x+y)%3==0),
                    (lambda x,y: (x/2+y/3)%2==0),
                    (lambda x,y: (x*y)%2+(x*y)%3==0),
                    (lambda x,y: ((x*y)%2+(x*y)%3)%2==0),
                    (lambda x,y: ((x*y)%3+(x+y)%2)%2==0)
                    )
    def __init__(self):
        pass
    @staticmethod 
    def size(version):
        '''
            返回指定版本QR码的像素边长
        '''
        return 4*version+17 if 1<=version<=40 else None
    @staticmethod 
    def size2version(size):
        '''
            返回指定QR码的像素边长对应的版本
        '''
        return (size-17)/4 if 21<=size<=177 and size%4==1 else 0
    @staticmethod 
    def anchorLevel(version):
        '''
            返回指定版本QR码的描点矩阵的阶
        '''
        return int(version/7)+2 if 1 < version <= 40 else 0
    @staticmethod 
    def funcpatBlock(version):
        if 1 <= version <= 40:
            al = QRMaster.anchorLevel(version)
            counter = 25*(al**2-3) if al > 0 else 0
            if al > 2:
                counter -= 10*(al-2)
            counter += (QRMaster.size(version)-16)*2
            return counter + 192
        return 0
    @staticmethod
    def dataAreaBlock(version):
        if 1<=version<=40:
            return QRMaster.size(version)**2-31-(36 if version>6 else 0)-QRMaster.funcpatBlock(version)
        return 0
    @staticmethod 
    def getVersionAndQualityByDataLength(length, qualevel=None):
        if type(qualevel) is not str:
            qualevel = 'L'
        qualevel = qualevel.upper()
        if qualevel not in 'LMQH': 
            qualevel = 'L'
        qualevels = {'L':(2,3,0,1), 'M':(2,3,0), 'Q':(2,3), 'H':(2,)}[qualevel] 
        for i in xrange(40):
            ver = i+1
            for j in qualevels:
                if length <= QRMaster.dataCaps(ver, j):
                    return (ver, j)
        return None
    @staticmethod 
    def getInfo(version, quality = None):
        info = {'forblock': 31,
                'size':QRMaster.size(version),
                'version': version,
                'verblock': 36 if version > 6 else 0,
                'block': QRMaster.funcpatBlock(version),
                'anchor level': QRMaster.anchorLevel(version),
                'content': None,
                'datablock':{'L':QRMaster.splitBlocks(version,1),
                             'M':QRMaster.splitBlocks(version,0),
                             'Q':QRMaster.splitBlocks(version,3),
                             'H':QRMaster.splitBlocks(version,2)
                             }
                }
        
        info['quality'] = 'MLHQ-'[quality%4 if quality is not None else 4]
        info['anchors'] = info['anchor level']**2-3 if info['anchor level'] > 1 else 0
        info['fvsize'] = info['verblock'] + info['forblock']
        info['data'] = info['size']**2 - info['fvsize'] - info['block']
        info['rest'] = info['data'] % 8
        info['capacity'] = info['data'] / 8
        return info
    @staticmethod
    def dataCaps(version, quality):
        '''
            计算指定版本、容错质量的QR码的信息容量
        '''
        if 1<=version<=40 and 0<=quality<4:
            return QRMaster.dataAreaLength(version) - QRMaster.checkCodeLength(version, quality)
        else: return 0
    @staticmethod
    def dataAreaLength(version): 
        '''
            计算指定版本QR码的信息容量
        '''
        return QRMaster.dataAreaBlock(version)/8   
    @staticmethod
    def checkCodeLength(version, quality):
        '''
            计算指定版本、容错质量的QR码的纠错码长度
        '''
        return QRMaster.LMQH_BlockList[version][quality]*QRMaster.Check_Length[version][quality]
    @staticmethod
    def splitBlocks(version, quality):
        if 1<=version<=40 and 0<=quality<4:
            total = QRMaster.dataAreaBlock(version)/8      #数据空间的总字节数
            tn = QRMaster.LMQH_BlockList[version][quality]     #分块数
            chkcode = QRMaster.Check_Length[version][quality]
            num, last = total / tn, total % tn
            if last == 0:
                return ((num, tn, chkcode),)
            else:
                return ((num, tn-last, chkcode),(num+1, last, chkcode)) 
        else:
            return None


class QRCoder(QRMaster):
    def __init__(self):
        self.__version   = 1
        self.__versionToSize()
        self.__matrix    = None
        self.__error     = 0
        self.__quality   = 0
        self.__mask      = 0
    def __getitem__(self, idx):
        class __QRCodeRow:
            def __init__(self, row):
                self.__row = row
            def __getitem__(self, idx):
                return self.__row[idx]
        return __QRCodeRow(self.__matrix[idx])
    def __repr__(self):
        buf = ''
        if self.__matrix:
            for i in self.__matrix:
                buf += ''.join(map(lambda x:'#'if x==BBP else' ',i))+'\n'
        return buf 
    @property
    def Version(self):
        return self.__version
    @Version.setter
    def Version(self, ver):
        if ver != self.__version and 1<= ver <=40:
            self.__version   = ver
            self.__versionToSize()
            self.__matrix    = None
            self.__error     = 0
            self.__quality   = 0
            self.__mask      = 0
    @property
    def Quality(self):
        return self.__quality

    @Quality.setter
    def Quality(self, qua):
        if type(qua) is str and len(qua):
            qua = qua.upper()[0]
            if qua not in 'LMQH': return
            qua = {'L':1,'M':0,'H':2,'Q':3}[qua] 
        self.__quality   = qua % 4

    @property 
    def Mask(self):
        return self.__mask
    @Mask.setter
    def Mask(self, mask):
        self.__mask      = mask % 8

    @property
    def Size(self):
        return self.__size

    def fitData(self, length, level='L'):
        ver_qua = super(QRCoder, self).getVersionAndQualityByDataLength(length, level)
        self.setVersionQuality(ver_qua)
    def setVersionQuality(self, ver_qua):
        if ver_qua and len(ver_qua) == 2:
            self.Version = ver_qua[0]
            self.Quality = ver_qua[1]
    
    def printOnConsole(self):
        Black, White, End = "\033[40;30m", "\033[47;37m", "\033[0m"

        if self.__matrix:
            import os
            h, w = map(int, os.popen("stty size").read().strip().split())
            l = min(h, w//2)
            if l < self.Size:
                print "console size is not enough."
                return

            margin = (w - self.Size*2) // 2
            print White+" "*w
            for l in self.__matrix:
                lc = l[0]
                buf = " "*margin
                buf += Black if lc == BBP else White
                for c in l:
                    if c != lc:
                        buf += Black if c == BBP else White
                    buf += "  "
                    lc = c
                if lc == BBP: buf += White
                print buf
            print End

    def checkCodeLength(self):
        return super(QRCoder, self).checkCodeLength(self.__version, self.__quality)
    def dataCaps(self):
        return super(QRCoder, self).dataCaps(self.__version, self.__quality)
    def piecesInfo(self):
        return self.splitBlocks(self.__version, self.__quality)
    def prepare(self):
        if self.__error or self.__matrix: return
        self.__matrix = [[NBP]*self.__size for _ in xrange(self.__size)]
    def showMatrix(self):
        if self.__error or not self.__matrix: return
        for i in self.__matrix:
            print ''.join(map(lambda x: CHARB if x else CHARN, i))
    def outputMatrixPicture(self, path, unit=4, margin=0, grid=False):
        if self.__error or not self.__matrix: return

        width = self.__size*unit + (1 if grid else 0)
        img = Image.new("RGB", (width+margin*2, width+margin*2), 0xFFFFFF)
        draw = ImageDraw.Draw(img)
        for i in xrange(self.__size):
            for j in xrange(self.__size):
                draw.rectangle(((i*unit+margin, j*unit+margin),((i+1)*unit+margin,(j+1)*unit+margin)), self.__matrix[j][i])
        if grid:
            for i in xrange(self.__size+1):
                draw.line((margin, i*unit + margin, width+margin, i*unit + margin),fill=0xbebebe, width=1)
                draw.line((i*unit + margin, width+margin, i*unit + margin, margin),fill=0xbebebe, width=1)
        img.save(path)
    def __versionToSize(self):
        self.__size = super(QRCoder, self).size(self.__version)
        if self.__size is None:
            self.__error = 132
        return self.__size 
   
    def anchorLevel(self):
        return super(QRCoder, self).anchorLevel(self.__version) if self.__error == 0 else None
    def functionPatternAreaBlock(self):
        if self.__error: return None
        if 1 <= self.__version <= 40:
            al = self.anchorLevel()
            counter = 25*(al**2-3) if al > 0 else 0
            if al > 2:
                counter -= 2*5*(al-2)
            counter += (self.__size - 16)*2
            return counter + 64 * 3
        return 0
    def __isOnAnchor(self, x, y):
        al = self.anchorLevel()
        if al < 2 or x<4 or y<4: return False
        disArr = self.__anchorDistritionList(al-1)
        lx, ly = 0, 0
        x -= 4        
        if x >= disArr[0]:
            x -= disArr[0]
            lx = 1
        y -= 4        
        if y >= disArr[0]:
            y -= disArr[0]
            ly = 1
        unit = disArr[-1]
        x, lx = x%unit, lx+x/unit
        y, ly = y%unit, ly+y/unit    
        al -= 1
        if (lx == 0 and ly == al) or (lx == al and ly == 0):
            return False
        else:
            return x<5 and y<5
    def __isDataArea(self, x, y):
        if self.__error: return False
        if self.__size <= y or 0 > y: return False
        if self.__size <= x or 0 > x: return False
        if x == 6 or y == 6: return False
        if x < 9 and (y < 9 or y >= self.__size-8): return False
        if x >= self.__size-8 and y < 9: return False
        if self.__version > 6:  #
            if x < 6 and y >= self.__size-11: return False
            if y < 6 and x >= self.__size-11: return False
            return not self.__isOnAnchor(x,y)
        if self.__version > 1:
            if self.__size-10< x <=self.__size-5 and self.__size-10< y <=self.__size-5: return False
        return True
    def dataAreaPosition(self): 
        '''
            数据区坐标迭代器
        '''
        if self.__error: return
        x = y = self.__size - 1
        column = self.__size -2
        ydir = -1
        while column >= 0:
            yield (y, x)
            if x > column:
                x -= 1
            else:
                y += ydir
                x += 1
            while not self.__isDataArea(x, y) and column >= 0:
                if x > column:
                    x -= 1
                else:
                    y += ydir
                    x += 1
                    if not (0 <= y <self.__size):
                        ydir, y = (1, 0) if y < 0 else (-1, self.__size-1)
                        column -= 2
                        if column == 5: column = 4
                        x = column+1
              
    def __anchorDistritionList(self, anchor=None):
        if not anchor: anchor = self.anchorLevel()-1
        sideLength = self.__size-13
        unit = float(sideLength) / anchor
        iunit = int(unit)
        anchor -= 1
        if unit == 26.4: unit = 26
        if unit > iunit: iunit+=1
        unit = iunit + iunit % 2
        sf = sideLength - unit*anchor
        return [sf]+[unit]*anchor
    def versionAnchorDistrition(self):  
        if self.__error: return
        anchor = self.anchorLevel()-1
        if anchor < 1: return
        diffarr = self.__anchorDistritionList(anchor)
        x = 6
        for i in xrange(anchor):
            y = 6 
            for j in xrange(anchor):
                if not(i == 0 and j ==0):
                    yield (x,y)
                y += diffarr[j]
            if i != 0:
                yield (x,y)
            x += diffarr[i]
        y = 6
        for i in xrange(anchor):
            y += diffarr[i]
            yield (x, y)

    def __setSingleCorner(self,x,y):
        for i in xrange(7):
            self.__matrix[x][y+i] = BBP
            self.__matrix[x+6][y+i] = BBP
        for i in xrange(1, 6):
            self.__matrix[x+i][y] = BBP
            self.__matrix[x+i][y+1] = NBP
            self.__matrix[x+i][y+5] = NBP
            self.__matrix[x+i][y+6] = BBP
        for i in xrange(2, 5):
            self.__matrix[x+1][y+i] = NBP
            self.__matrix[x+2][y+i] = BBP
            self.__matrix[x+3][y+i] = BBP
            self.__matrix[x+4][y+i] = BBP
            self.__matrix[x+5][y+i] = NBP
    def setCorner(self):
        if self.__error or not self.__matrix: return
        leng = lsize = self.__size -1
        lsize -= 6
        self.__setSingleCorner(0,0)
        self.__setSingleCorner(lsize,0)
        self.__setSingleCorner(0,lsize)
        lsize -= 1
        for i in xrange(8):
            self.__matrix[7][i] = NBP 
            self.__matrix[lsize][i] = NBP
            self.__matrix[7][leng-i] = NBP 
        for i in xrange(7):
            self.__matrix[i][7] = NBP 
            self.__matrix[i][lsize] = NBP
            self.__matrix[leng-i][7] = NBP        
    def __setSingleAnchor(self, x, y):
        x -= 2
        y -= 2
        for i in xrange(5):
            self.__matrix[x][y+i] = BBP
            self.__matrix[x+4][y+i] = BBP
        for i in xrange(1, 4):
            self.__matrix[x+i][y] = BBP
            self.__matrix[x+i][y+4] = BBP
            self.__matrix[x+i][y+1] = NBP
            self.__matrix[x+i][y+3] = NBP
        self.__matrix[x+1][y+2] = self.__matrix[x+3][y+2] = NBP
        self.__matrix[x+2][y+2] = BBP
    def setAnchor(self):
        if self.__error or not self.__matrix: return
        vad = self.versionAnchorDistrition()
        if vad:
            for i in vad:
                self.__setSingleAnchor(i[0], i[1])
    def setRuler(self):
        if self.__error or not self.__matrix: return
        for i in xrange(8, self.__size-8):
            self.__matrix[i][6] = self.__matrix[6][i] = BPARR[i%2] 
    def setFormatInfo(self):
        '''
            设置掩码格式、容错质量等信息
        '''
        if self.__error or not self.__matrix: return
        data = xbin(self.__quality,2) + xbin(self.__mask,3)
        bch = BCHCoder(15, 5, '10100110111')
        data += bch.encode(data)
        data = strXor(data, '101010000010010')
        data = map(lambda x: x!='0', data) 
        for i in xrange(8):
            self.__matrix[8][i if i<6 else i+1] = BBP if data[i] else NBP
            self.__matrix[self.__size-i-1][8] = BBP if data[i] else NBP
        for i in xrange(7):
            i += 8
            self.__matrix[15-(i if i<9 else i+1)][8] = BBP if data[i] else NBP
            self.__matrix[8][self.__size-15+i] = BBP if data[i] else NBP
        self.__matrix[self.__size-8][8] = BBP
    def setVersionInfo(self):
        """
            setFormatInfo
        """
        if self.__error or not self.__matrix: return
        if self.__version < 7: return
        data = xbin(self.__version, 6)
        bch = BCHCoder(18, 6, '1111100100101')
        chkcode = bch.encode(data)
        data = map(lambda x: x!='0', (data+chkcode)[::-1])
        startColumn = self.__size-11 
        for i in xrange(18):
            self.__matrix[startColumn+i%3][i/3] =  BBP if data[i] else NBP
            self.__matrix[i/3][startColumn+i%3] =  BBP if data[i] else NBP       
    def getInfo(self):
        return super(QRCoder, self).getInfo(self.__version, self.__quality)
    def randMatrix(self):
        for i in xrange(self.__size):
            for j in xrange(self.__size):
                self.__matrix[i][j] ^= BPARR[random.randint(0,10)%2]
    def beginACode(self, v=0, q=None):
        if v: self.Version = v
        if q is not None: self.Quality = q
        self.prepare()
        self.setCorner()
        self.setAnchor()
        self.setRuler()
        self.setVersionInfo()  
        return True
    
    def generateMask(self):
        return super(QRCoder, self).MaskFuncsList[self.__mask]
    def fillData(self, datas):
        pieceInfo = self.piecesInfo()
        totalGumi = pieceInfo[0][1]
        dataRest, dataNotFix = -1, True
        if len(pieceInfo) == 2:
            totalGumi += pieceInfo[1][1]
            dataRest = totalGumi * (pieceInfo[0][0] - pieceInfo[0][2]) * 8
        assert totalGumi == len(datas)
        idx, ibyte, igroup, gidx = 0, 0, 0, 0
        func = self.generateMask()
        for i in self.dataAreaPosition():
            x, y = i
            if ibyte*8+gidx >= len(datas[igroup]):
                cdata = '0'
            else:
                cdata = datas[igroup][ibyte*8+gidx]
            self.__matrix[x][y] = BBP if (cdata=='1')^func(x,y) else NBP

            idx += 1
            gidx += 1
            if idx % 8 == 0: 
                igroup += 1
                gidx = 0
                if not dataNotFix and igroup == pieceInfo[0][1]:
                    ibyte += 1
                if igroup == totalGumi:
                    igroup = 0
                    if dataNotFix:
                        ibyte += 1
                        if dataRest == idx:
                            igroup = pieceInfo[0][1]
                            dataRest += pieceInfo[1][1] * 8
                            dataNotFix = False
                
                
    def evaluate(self):
        _matrix = self.__matrix
        sumv, sumx = 0, 0
        DsSum = 0
        BBPCount = 0
        DsRate = (0,1,1,3,1,1)
        for i in xrange(self.__size):
            continous = [1, 1]
            DsDsD = [[],[]]
            if _matrix[i][0] == BBP: 
                BBPCount += 1
            for j in xrange(1, self.__size):
                if _matrix[i][j] == BBP: 
                    BBPCount += 1

                # scan every column
                if _matrix[i][j] == _matrix[i][j-1]:
                    continous[0] += 1
                else:
                    if _matrix[i][j] == NBP or DsDsD[0]:
                        DsDsD[0].append(continous[0])
                        if len(DsDsD[0]) > 1:
                            if DsDsD[0][0]*DsRate[len(DsDsD[0])] == DsDsD[0][-1]:
                                if len(DsDsD[0]) == 5:
                                    DsSum += 1 
                                    DsDsD[0] = []
                            else:
                                DsDsD[0] = DsDsD[0][2:]if len(DsDsD[0])>=4 else []
                                    
                    if continous[0] > 5:
                        sumv += continous[0] - 2
                    continous[0] = 1

                # scan every row
                if _matrix[j][i] == _matrix[j-1][i]:
                    continous[1] += 1
                else:
                    if _matrix[i][j] == NBP or DsDsD[1]:
                        DsDsD[1].append(continous[1])
                        if len(DsDsD[1]) > 1:
                            if DsDsD[1][0]*DsRate[len(DsDsD[1])] == DsDsD[1][-1]:
                                if len(DsDsD[1]) == 5:
                                    DsSum += 1 
                                    DsDsD[1] = []
                            else:
                                DsDsD[1] = DsDsD[1][2:]if len(DsDsD[1])>=4 else []
                                    
                    if continous[1] > 5:
                        sumv += continous[1] - 2
                    continous[1] = 1

                if i == 0: continue
                # scan M*N blocks
                curBit = _matrix[i][j]
                if curBit == _matrix[i-1][j] and \
                    curBit == _matrix[i][j-1] and \
                    curBit == _matrix[i-1][j-1]:
                    sumx += 1
        
        k = abs(100.0*BBPCount / self.__size**2 - 50)//5
        return 40*DsSum + sumv + 10*k + sumx*3


def drawBlockColor(v, m):
    qrc = QRCoder()
    qrc.beginACode(v)  
    qrc.setFormatInfo()
     
    idx = 0
    colors = (0xff,0xff00,0xff0000,0xffff,0xffff00,0xff00ff,0x7f,0x7f00,0x7f0000)
    for pos in qrc.dataAreaPosition():
        x, y = pos
        if idx/8%2 == 1: #/8 in (356, 390):
            qrc.__matrix[x][y] = colors[(idx/16)%len(colors)]
        if idx/8 == 16*4+8:
            qrc.__matrix[x][y] = 0 #colors[(idx/16)%len(colors)]
        idx += 1
         
    return qrc

def drawMaskCode(v, m, full=None):
    qrc = QRCoder()

    if full:
        qrc.beginACode(v)
    else:
        qrc.Version = v
        qrc.prepare()
    qrc.Mask = m
    
    func = qrc.generateMask()
    for pos in qrc.dataAreaPosition():
        x, y = pos
        qrc.__matrix[x][y] = BBP if func(x,y) else NBP
    return qrc     
    
     
def QREncode(data, level=None, mode=None, qrcode=False):
    if mode is None:
        mode = QRDataEncoder.chooseMode(data)

    qrd = QRDataEncoder(mode=mode)
    vq = None
    while True:
        ldata = qrd.assumeLength(data)
        lbyte = ldata / 8 + (1 if ldata % 8 else 0)
        vq = QRMaster.getVersionAndQualityByDataLength(lbyte, level)
        vdiff = qrd.isFitVersion(vq[0])
        if vdiff == 0:
            break
        qrd.shiftVersion(vdiff)
          
    prdata = qrd.encodeData(data)
    prdata = qrd.fillContent(prdata, QRMaster.dataCaps(*vq))    #

    pinfo = QRMaster.splitBlocks(*vq)
    datas = qrd.encodeBlocksCheckCode(prdata, pinfo)


    qrc = QRCoder()
    qrc.beginACode(*vq)
      
    minscore, minmask = INF, 0
    for mask in xrange(8):
        qrc.Mask = mask
        qrc.fillData(datas) 
        qrc.setFormatInfo()

        score = qrc.evaluate()
        if score < minscore:
            minscore, minmask = score, mask

    qrc.Mask = minmask
    qrc.fillData(datas) 
    qrc.setFormatInfo()

    return qrc
    
if __name__ == '__main__': 
    pass
            