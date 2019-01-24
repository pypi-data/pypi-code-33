from .models import resnet,se_net

arch_list = ['resnet34','resnet50','resnet101','se_resnext101', 'senet154', 'se_resnet50', 'se_resnet101', 'se_resnet152',
           'se_resnext50_32x4d', 'se_resnext101_32x4d']

se_net_list = ['se_resnext101','se_resnext101', 'senet154', 'se_resnet50', 'se_resnet101', 'se_resnet152',
           'se_resnext50_32x4d', 'se_resnext101_32x4d']

def Model(arch,num_classes,pretrained=True):
    check_arch(arch)
    if arch in se_net_list:
        return se_net.get_model(arch,num_classes,pretrained=pretrained)
    if arch=='resnet34' or 'resnet50' or 'resnet101':
        return resnet.get_model(arch,num_classes,pretrained)
   

def check_arch(arch):
    if arch not in arch_list:
        print("Arch not present, choose from "+str(arch_list))

# class Serialization(nn.Module):         #WIP
# 	def __init__(self):
# 		super(Serialization,self).__init__()
# 	def save(self,filename):
# 		torch.save(self.state_dict(),filename)
# 	def load(self.filename):
# 		self.load_state_dict(torch.load(filename, map_location=lambda storage, loc: storage))
