import rblk.scanner.txt as txtscaner
import rblk.tag.txt as tgtg
import elist.elist as elel

class Parser():
    def __init__(self,txt,tag_pairs):
        self.txt = txt
        if(isinstance(tag_pairs,dict)):
            pass
        else:
            tag_pairs = tgtg.str2pairs(tag_pairs)
        self.descmat = txtscaner.get_descmat(txt,tag_pairs=tag_pairs)
        self.depth = len(self.descmat)
        self.breadths = elel.mapiv(self.descmat,lambda i,layer:len(layer))
        self.text_mat = elel.matrix_map(self.descmat,lambda v,r,c:txt[v['si']:v['ei']])
    def srch4loc(self,tag):
        rslt = []
        for i in range(self.depth):
            for j in range(self.breadths[i]):
                ele_tag = self.descmat[i][j]['tag']
                if(tag == ele_tag):
                    loc = [i,j]
                    rslt.append(loc)
        return(rslt)
    def srch4blk(self,tag):
        rslt = []
        for i in range(self.depth):
            for j in range(self.breadths[i]):
                ele_tag = self.descmat[i][j]['tag']
                if(tag == ele_tag):
                    txt = self.text_mat[i][j]
                    rslt.append(txt)
        return(rslt)
    def srch4txt(self):
        return(self.srch4blk("null"))
    def lvsrch4blk_fromto(self,tag,from_lv,to_lv):
        from_lv = elel.uniform_index(from_lv,self.depth)
        to_lv = elel.uniform_index(to_lv,self.depth)
        rslt = []
        for i in range(from_lv,to_lv):
            for j in range(self.breadths[i]):
                ele_tag = self.descmat[i][j]['tag']
                if(tag == ele_tag):
                    txt = self.text_mat[i][j]
                    rslt.append(txt)
        return(rslt)
    def lvsrch4blk_from(self,tag,from_lv):
        to_lv = self.depth
        rslt = self.lvsrch4blk_fromto(tag,from_lv,to_lv)
        return(rslt)
    def lvsrch4blk_to(self,tag,to_lv):
        from_lv = 0
        rslt = self.lvsrch4blk_fromto(tag,from_lv,to_lv)
        return(rslt)
    def lvsrch4blk(self,tag,lv):
        rslt = self.lvsrch4blk_fromto(tag,lv,lv+1)
        return(rslt)
    def lvsrch4txt_fromto(self,from_lv,to_lv):
        return(self.lvsrch4blk_fromto("null",from_lv,to_lv))
    def lvsrch4txt_from(self,from_lv):
        return(self.lvsrch4blk_from("null",from_lv))
    def lvsrch4txt_to(self,to_lv):
        return(self.lvsrch4blk_to("null",to_lv))
    def lvsrch4txt(self,lv):
        rslt = self.lvsrch4blk_fromto("null",lv,lv+1)
        return(rslt)








    
    
        

