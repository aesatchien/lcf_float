#! /c/Users/cjhill/AppData/Local/Continuum/miniconda3/python
# coding: utf-8

# In[1]:


import matplotlib
import matplotlib.pyplot as plt
import numpy as np


# In[5]:


# Data for plotting
t = np.arange(0.0, 2.0 * np.pi, 0.01)
s = np.sin(t)


# In[17]:


fig, ax = plt.subplots(figsize=(18,16))

ax.plot(t, s)

ax.set(xlabel='x', ylabel='sin(x)', 
       title='Plot of sin(x)')
ax.grid()

fig.savefig("test.png")
plt.show()


# In[ ]:




