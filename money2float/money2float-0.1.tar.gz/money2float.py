#!/usr/bin/env python
# coding: utf-8

# In[1]:


from decimal import *


# In[13]:


def money(text, places=2):
    if text:
        try:
            text = text.replace(",", "")
        except:
            pass
        try:
            text = text.replace("$", "")
        except:
            pass
        try:
            response = float(round(Decimal(text), places))
        except:
            response = 0
    else:
        response = 0
    return response


# In[ ]:
