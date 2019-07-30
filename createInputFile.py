import createInpFileFunc as create
import statusUpdateFunc as status
import actions 
rxn = '../R4/'
components = status.findStatus(rxn,side=True)
print(actions.actions('actions.txt',components))

#key = ['Hdr','Gem','Hss','Grd','Vec','Vib','IRC',
#
#
#        #necessaryInputs: 
#            #HEADER
#                #prevInpFile
#                #newInputFile
#                #runtyp
#                #parameters
#                #opttol
#                #nstep 
#                #npoint
#            #GEOM
#                #prevGeomDatFile
#                #newInputFile
#                #runtyp
#                #restart
#            #VEC
#                #prevVecDatFile
#                #newInputFile
#                #runtyp
#                #restart
#            #GRAD
#                #prevGradDatFile
#                #newInputFIle
#            #HESS
#                #prevHessDatFIle
#                #newInputFIle
#            #IRC
#                #prevIRCDatFIle
#                #newInputFIle
#            
#
#
#
#def main(components):
#    for leafNode in components:
#    # if leafNode == None:
#    # then continue
#    # print (no leaf node for ___ hand side
#
#        actionStatement = variables.actions[leafNode]
#        
#    
#        prevInpFile = actionStatement[2]
#        newInputFile = actionsStatment[3]
#    
#        with open(newInputFile,'w') as inp:
#            code = actions[1]
#
#            if 'Hdr' in code:     
#                create.header()
#            if 'Gem' in code:
#                create.geom()
#            if 'Hss' in code:
#                create.hess()
#            if 'Grd' in code:
#                create.grad()
#            if 'Vec' in code:
#                create.vec()
#            if 'Vib' in code:
#                create.vib()
#            if 'Irc' in code:
#                create.IRC()
#
# 
#    
#    
#    #etc...


