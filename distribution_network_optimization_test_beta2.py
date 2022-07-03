# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 21:19:09 2021

@author: Administrator
"""



import pandas as pd
import gurobipy as grb
import time
start=time.time()
m=grb.Model()
#m.Params.MIPGap=1e-6
path='C:\\Users\\Administrator\\Desktop\\14_bus_data.xlsx'
edge_data=pd.read_excel(path)
bus_data=pd.read_excel(path,sheet_name=1)
edge_list=[]
r={};x={}
for i in range(len(edge_data)):
    temp=edge_data.iloc[i]
    start_bus=int(temp[0])
    end_bus=int(temp[1])
    r_pu=temp[2]
    x_pu=temp[3]
    edge_list.append((start_bus,end_bus))
    r[(start_bus,end_bus)]=r_pu
    x[(start_bus,end_bus)]=x_pu
edge_list=grb.tuplelist(edge_list)
p_load={};q_load={};c={}
for i in range(len(bus_data)):
    temp=bus_data.iloc[i]
    bus=int(temp[0])
    p_load[bus]=temp[1]/100
    q_load[bus]=temp[2]/100
    c[bus]=temp[3]/100
X=m.addVars(edge_list,vtype=grb.GRB.BINARY,name='X')
y=m.addVars(edge_list,name='y')
v_list=[i+1 for i in range(14)]
v=m.addVars(v_list,name='v')
p=m.addVars(edge_list,lb=-grb.GRB.INFINITY,name='p')
q=m.addVars(edge_list,lb=-grb.GRB.INFINITY,name='q')
l=m.addVars(edge_list,name='l')

p1=m.addVar(lb=-grb.GRB.INFINITY,name='p1')
q1=m.addVar(lb=-grb.GRB.INFINITY,name='q1')


m.update()
#m.setObjective(grb.quicksum(r[i,j]*(p[i,j]**2+q[i,j]**2) for i,j in edge_list))
m.setObjective(grb.quicksum(r[i,j]*l[i,j] for i,j in edge_list))
m.addConstr(grb.quicksum(X[i,j] for i,j in edge_list)==13)
#m.addConstr(p1==p.sum(1,'*')-p.sum('*',1)+p_load[1])
#m.addConstr(q1==q.sum(1,'*')-q.sum('*',1)+q_load[1]-c[1])
#m.addConstrs(p.sum(i,'*')-p.sum('*',i)+p_load[i]==0 for i in range(2,15))
#m.addConstrs(q.sum(i,'*')-q.sum('*',i)+q_load[i]-c[i]==0 for i in range(2,15))
m.addConstr(p1==p.sum(1,'*')-grb.quicksum(p[i,j]-r[i,j]*l[i,j] for i,j in edge_list.select('*',1))+p_load[1])
m.addConstr(q1==q.sum(1,'*')-grb.quicksum(q[i,j]-x[i,j]*l[i,j] for i,j in edge_list.select('*',1))+q_load[1]-c[1])
m.addConstrs(p.sum(k,'*')-grb.quicksum(p[i,j]-r[i,j]*l[i,j] for i,j in edge_list.select('*',k))+p_load[k]==0 for k in range(2,15))
m.addConstrs(q.sum(k,'*')-grb.quicksum(q[i,j]-x[i,j]*l[i,j] for i,j in edge_list.select('*',k))+q_load[k]-c[k]==0 for k in range(2,15))


M=1e4
m.addConstrs(y[i,j]==(1-X[i,j])*M for i,j in edge_list)
m.addConstrs(v[i]-v[j]<=y[i,j]+2*(r[i,j]*p[i,j]+x[i,j]*q[i,j])-(r[i,j]**2+x[i,j]**2)*l[i,j] for i,j in edge_list)
m.addConstrs(v[i]-v[j]>=-y[i,j]+2*(r[i,j]*p[i,j]+x[i,j]*q[i,j])-(r[i,j]**2+x[i,j]**2)*l[i,j] for i,j in edge_list)
s_max=10
l_max=10
for i,j in edge_list:
    temp1=grb.QuadExpr()
    temp2=grb.QuadExpr()
    temp1.addTerms(1,p[i,j],p[i,j])
    temp1.addTerms(1,q[i,j],q[i,j])
    temp2.addTerms(1,l[i,j],v[i])
    m.addQConstr(temp1<=temp2)
m.addConstrs(l[i,j]<=l_max*X[i,j] for i,j in edge_list)
'''
m.addConstrs(-X[i,j]*s_max<=p[i,j] for i,j in edge_list)
m.addConstrs(X[i,j]*s_max>=p[i,j] for i,j in edge_list)
m.addConstrs(-X[i,j]*s_max<=q[i,j] for i,j in edge_list)
m.addConstrs(X[i,j]*s_max>=q[i,j] for i,j in edge_list)
m.addConstrs(-2**0.5*X[i,j]*s_max<=p[i,j]+q[i,j] for i,j in edge_list)
m.addConstrs(2**0.5*X[i,j]*s_max>=p[i,j]+q[i,j] for i,j in edge_list)
m.addConstrs(-2**0.5*X[i,j]*s_max<=p[i,j]-q[i,j] for i,j in edge_list)
m.addConstrs(2**0.5*X[i,j]*s_max>=p[i,j]-q[i,j] for i,j in edge_list)
'''
m.addConstr(v[1]==1)
m.optimize()
for i,j in edge_list:
    if X[i,j].x==0:
        print('支路%s<-->%s断开'%(i,j))
end=time.time()
print('运行时间',end-start)






    

    


