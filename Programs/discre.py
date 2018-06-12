#! /anaconda3/envs/splitwavepy/bin/python

# Welcome to discre.py. This script (or maybe module??) is for testing whether
# SKS SKKS pairs exhibit matching or discrepent splitting. This will be done
# by using the splitting measured for each phase to correct the splitting on
# the other.
### Imports
import numpy as np
import pandas as pd
import obspy as ob
#import splitwavepy as sw
import matplotlib.pyplot as plt
from stack import Stacker,plot_stack
from glob import glob
from datetime import datetime
from matplotlib import gridspec
# Maybe some others

###############################################################################
class Tester:

    def __init__(self,pr,path,stack_done=False):


        date_time_convert = {'TIME': lambda x: str(x),'DATE': lambda x : str(x)}
        if stack_done is False:
            self.pairs = pd.read_csv(pr,delim_whitespace=True,converters=date_time_convert)
        elif stack_done is True:
            self.p2 = pd.read_csv(pr,delim_whitespace=True,converters=date_time_convert)
        self.path =path

        self.lam2 = []

    def pair_stack(self):
        ''' Runs Stacker for all the desired pairs (a .pairs file)'''

        print('Running')
        for i,f in enumerate(self.pairs.DATE.values):
            #rint('It {}, time is {} '.format(i,str(datetime.now())))
            # First get the right DATE,TIME and STATION
            date,time,stat = self.pairs.DATE[i], self.pairs.TIME[i], self.pairs.STAT[i]
            fstem = '{}_{}_{}'.format(stat,date,time)

            lam2_stem = glob('{}/{}/SKS/{}??_SKS.lam2'.format(self.path,stat,fstem))
            print('{}/{}/SKS/{}??_SKS.lam2'.format(self.path,stat,fstem))
            if len(lam2_stem) is not 0:
                # I.e if glob has managed to find the sks lam2 surface file
                sks_lam2 = glob('{}/{}/SKS/{}??_SKS.lam2'.format(self.path,stat,fstem))[0]
                skks_lam2 = glob('{}/{}/SKKS/{}??_SKKS.lam2'.format(self.path,stat,fstem))[0]
                Stk = Stacker(sks_lam2,skks_lam2,fstem)
                lam2.append(Stk.sol[-1])
            else:
                fstem2 = '{}_{}'.format(stat,date)
                sks_lam2 = glob('{}/{}_*_SKS.lam2'.format(self.path,fstem2))[0]
                skks_lam2 = glob('{}/{}_*_SKS.lam2'.format(self.path,fstem2))[0]
                # Now for a sanity check
                if (len(sks_lam2) is not 0) or (len(skks_lam2) is not 0):
                    Stk = Stacker(sks_lam2,skks_lam2)
                    lam2.append(Stk.sol[-1])
                else:
                    #print('lam2 surfaces cannot be found, skipping')
                    pass
    #        Now lets get the lambda 2 values
        print('Lam2 max: {} Lam2 min: {}'.format(max(lam2),min(lam2)))

        self.lam2 = lam2

    def plot_lam2(self,x):
        print('Plotting')

        plt.plot(x,self.lam2,'k.')
        plt.ylabel('lambda 2 values')
        plt.yticks(np.arange(0,2,step=0.2))
        plt.ylim([0,2])
        plt.show()

    def discrepancy_plot(self,nplots=2,**kwargs):
        '''Top level plotting function for surfaces to look for discrepancy in Splitting'''
        self.l2 = self.p2.sort_values(by='LAM2',ascending=True)
        print(self.l2)
        # Find indecies of events we want to plot
        samps = np.round(np.arange(0,len(self.l2),round((len(self.l2)/nplots))))
        for s in samps:
            print(s)
            stat,date,time = self.l2.STAT.values[s],self.l2.DATE.values[s], self.l2.TIME.values[s]
            fast_sks,dfast_sks,lag_sks,dlag_sks = self.l2.FAST_SKS.values[s],self.l2.DFAST_SKS.values[s],self.l2.TLAG_SKS.values[s],self.l2.DTLAG_SKS.values[s]
            fast_skks,dfast_skks,lag_skks,dlag_skks = self.l2.FAST_SKKS.values[s],self.l2.DFAST_SKKS.values[s],self.l2.TLAG_SKKS.values[s],self.l2.DTLAG_SKKS.values[s]

            l_path = '{}/{}/{}_{}_{}'.format(self.path,stat,stat,date,time)
            self.lam2_surface(l_path)

            fig = plt.figure(figsize=(8,8))
            gs = gridspec.GridSpec(3,2)
            ax0 = plt.subplot(gs[0,0])
            ax0.set_title(r'SKS $\lambda _2$ surfaces')
            C0 = ax0.contour(self.T,self.F,self.sks_lam2,[1,2,3,4,5,10,15,20,50,100],colors='k')
            ax0.clabel(C0,C0.levels,inline=True,fmt ='%2.0f')
            ax0.plot([lag_sks-dlag_sks,lag_sks+dlag_sks],[fast_sks,fast_sks],'b-')
            ax0.plot([lag_sks,lag_sks],[fast_sks-dfast_sks,fast_sks+dfast_sks],'b-')
            ax0.set_ylim([-90,90])
            ax0.set_xlim([0,4])
            ax0.set_yticks([-90,-60,-30,0,30,60,90])
            # ax0.contourf(self.sks_lam2,cmap='magma_r')
            ax1 = plt.subplot(gs[0,1])
            C1 = ax1.contour(self.T,self.F,self.skks_lam2,[1,2,3,4,5,10,15,20,50,100],colors='k')
            ax1.clabel(C1,C1.levels,inline=True,fmt ='%2.0f')
            # ax1.contourf(self.skks_lam2,cmap='magma')
            ax1.plot([lag_skks-dlag_skks,lag_skks+dlag_skks],[fast_skks,fast_skks],'b-')
            ax1.plot([lag_skks,lag_skks],[fast_skks-dfast_skks,fast_skks+dfast_skks],'b-')
            ax1.set_ylim([-90,90])
            ax1.set_xlim([0,4])
            ax1.set_yticks([-90,-60,-30,0,30,60,90])
            ax1.set_title(r'SKKS $\lambda _2$ surfaces')
            ax2 = plt.subplot(gs[1:,:])
            self.show_stacks(ax2,'{}/{}'.format(self.path,stat),'{}_{}_{}'.format(stat,date,time))
            plt.title(r'Event {}_{}_{}. $\lambda$ 2 value = {}'.format(stat,date,time,self.l2.LAM2.values[s]))

        # Read Lam2 surfaces for SKS and SKKS
        # self.lam2_surface(stem)


        plt.show()

    def write_lam2(self):
        '''Adds lam2 values to pairs'''
        l2df = {'LAM2' : self.lam2}
        ldf = pd.DataFrame(l2df)
        pairs['LAM2'] = ldf

        pairs.to_csv('/Users/ja17375/Shear_Wave_Splitting/Sheba/Results/Jacks_Split/Accepted_SKS_SKKS_all_w_lam2.pairs',sep=' ')

        self.p2 = pairs

    def lam2_surface(self,fstem):
        ''' Function to read  SKS and SKKS .lam2 surface files from sheba '''
        sks =glob('{}??_SKS.lam2'.format(fstem))
        skks = glob('{}??_SKKS.lam2'.format(fstem))
        # print(skks)
        self.sks_lam2 = np.loadtxt(sks[0],skiprows=4)
        self.skks_lam2 = np.loadtxt(skks[0],skiprows=4)

        nfast,nlag = self.sks_lam2.shape ;
        lag_max = 4.
        [self.T,self.F] = np.meshgrid(np.linspace(0,lag_max,num=nlag),np.arange(-90,91,1)) ;

    def show_stacks(self,ax,path,evt):
        '''Function to find and plot desired surface stacks based on the LAMDA2 value '''
        ### Plot Min Lamnda 2

        with open('{}/sheba_stack.sol'.format(path),'r') as reader:
            head = reader.readline()  #Reads headers
            S = reader.readline().split() # Reads solution
            fast,dfast = float(S[0]), float(S[1])
            lag,dlag = float(S[2]),float(S[3])
            nsurf = float(S[4])
            lag_step = float(S[5])
            lam2 = S[6]
            # print(lam2)
        # Read surface
        err = np.loadtxt('{}/sheba_stack.err'.format(path))
        nfast,nlag = err.shape ;
        lag_max = (nlag) * lag_step ;
        [T,F] = np.meshgrid(np.arange(0,lag_max,lag_step),np.arange(-90,91,1)) ;

        C = ax.contour(T,F,err,[1,2,3,4,5,10,15,20,50,100],colors='k')
        ax.set_ylabel(r'Fast,$\phi$, (deg)')
        ax.set_xlabel(r'Lag ,$\delta$ t, (sec)')
        ax.plot([lag-dlag,lag+dlag],[fast,fast],'b-')
        ax.plot([lag,lag],[fast-dfast,fast+dfast],'b-')
        ax.clabel(C,C.levels,inline=True,fmt ='%2.0f')
        # ax.set_title(r'Event {}. $\lambda$ 2 value = {}'.format(evt,lam2))




if __name__ == '__main__':
    print('This is discre.py')
    p = '/Users/ja17375/Shear_Wave_Splitting/Sheba/Results/Jacks_Split/Accepted_SKS_SKKS_all.pairs'
    path = '/Users/ja17375/Shear_Wave_Splitting/Sheba/Runs/Jacks_Split'
    t = Tester(p,path)
    lam2 =  pair_stack(p,path)
    p2 = write_lam2(p,lam2) # p2 contians lam2 values

    show_stacks(p2)
    #print(lam2)
    #plot_lam2(p.index.values,lam2)
