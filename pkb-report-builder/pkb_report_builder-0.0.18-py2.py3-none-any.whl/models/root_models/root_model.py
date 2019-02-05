import logging
import re
#account root model
class RootModel():
    def __init__(self,aggreement_value):
        try:
            self.aggreement_value =aggreement_value
            self.aggreement_number =''
            self.aggreement_counter =''

            self.parse_aggreement_value()
        except Exception as e:
            logging.error("Error"+str(e))


    #parse
    def parse_aggreement_value(self):
        try:
            ln_index = -1
            limit = 0
            copy_all =False
            for v_index in range(len(self.aggreement_value) - 1, 0, -1):
                let = self.aggreement_value[v_index]
                if re.match("^[A-Za-z0-9]*$", let):
                    ln_index+=1
                    ln_index=v_index
                else:
                    break

                if (limit>2):
                    ln_index=len(self.aggreement_value)
                    copy_all=True
                    break
                limit+=1

            if (ln_index>1):
                if (copy_all==False):
                    self.aggreement_number = str(self.aggreement_value)[0:ln_index-1]
                    l = len(self.aggreement_value)
                    self.aggreement_counter = str(self.aggreement_value)[ln_index:l]

                else:
                    self.aggreement_number = str(self.aggreement_value)[0:ln_index]



            else:
                self.aggreement_number = self.aggreement_value
            p=0

        except Exception as e:
            logging.error("Error"+str(e))
