#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 10:28:53 2022

@author: suzanne
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import deque

def data_colorbar(num_colors,labels,figsize=(1,3),extend=None,outfile=None):

    if len(labels) != num_colors:
        print('There should be one color for each label.')
        return 
    # if extend =='both':
        
    #     num_colors +=2
    #     labels = deque(labels)
    #     labels.appendleft(' ')
    #     labels.append(' ')
    #     print(labels)

    allColorsList=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    # allTextColors=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    # trim and convert to cmap
    # if extend == 'both':
    #     ColorsList = (mpl.colors.ListedColormap(allColorsList[1:num_colors+1])).with_extremes(over=allColorsList[0],under=allColorsList[num_colors+1])
    # else:
    ColorsList = mpl.colors.ListedColormap(allColorsList[:num_colors])

    # if num_colors>4:
    #     fig,ax = plt.subplots(1,1,figsize=(num_colors,4))
    # else:
    #     fig,ax = plt.subplots(1,1)
    # plt.axes([0.1,0.8,0.8,0.1])
    fig,ax = plt.subplots(1,1,figsize=figsize)
    fig.subplots_adjust(bottom=0.8,left=0.1, right=0.9, top=0.9)

    # bounds = labels
    # norm = mpl.colors.BoundaryNorm(bounds, ColorsList.N)
    # fig.colorbar(
    #     mpl.cm.ScalarMappable(cmap=ColorsList, norm=norm),
    #     cax=ax,
    #     boundaries = labels[0]-0.5 + bounds + labels[-1+0.5],
    #     extend = extend,
    #     ticks=bounds,
    #     spacing = 'proportional',
    #     orientation = 'horizontal',
    #     label = 'first try',
    #     )


    
    # if extend is None:
    cb = mpl.colorbar.ColorbarBase(ax, orientation='horizontal',cmap=ColorsList, ticks=[], extend=extend)
    cb.ax.set_title(label='Nominal Temperature Sensor Depth (m)', fontsize=16)
    # elif extend == 'both':
    #     fig.colorabr(mpl.cm.ScalarMappable(cmap=ColorsList,extend=extend)
    # cb.set_under(allColorsList[0])
    # cb.set_over(allColorsList['r'])

    cb.ax.get_xaxis().set_ticks([])
    for ii,lab in enumerate(labels):
        if ii==7: ctext='silver'
        else: ctext='white'
        cb.ax.text((ii+0.5)/num_colors, 0.45, lab, ha='center', va='center',color=ctext,
                    fontsize=16, fontweight='bold')
    # cb.ax.set_xlabel(labels)
    # ax.set_title('Nominal Temperature Sensor Depth (m)',fontsize=20)
    plt.savefig(f'UPTEMPO/WebPlots/{outfile}',bbox_inches='tight')

    plt.show()
    

# print(mpl.__version__)
import numpy as np
num_cycles=13
print(np.arange(0,num_cycles,6))
exit(-1)
data_colorbar(1,['0.28'],outfile='PG-28cm.png',figsize=(1,1))
# data_colorbar(2,['0.0','5'],outfile='PG-5m.png')
# data_colorbar(5,['0.0','2.5','5.0','7.5','10.0'],outfile='PG-10m.png')
# data_colorbar(8, ['0','2.5','5','7.5','10','15','20','25'],outfile='PG-25m.png') #,extend='both')
# data_colorbar(17,['0','2.5','5','7.5','10','12.5','15','17.5','20','25','30','35','40','45','50','55','60'],outfile='PG-60m.png')

plt.show()
exit(-1)

