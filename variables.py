# Specifically with this process, there needs to be a constant comparison between the number of highOpttol folders within the SadPoint folder and in the Hessian folder (they will either be the same, meaning the next step is to check the Hess results and move onto an IRC OR there is one more highOpttol folder in the SadPoint directory than in the Hess_final directory, signifiying a Hess_final calculation is due)...and so a variable equal to ZERO signifies the former and value of ONE signifies the latter
SP_HF_count = {'SadPoint/':0,'Hess_final/':0}

# Hard-coded (see README) adjacency lists (al) for decision tree
adjacency = {0:set([1, 2]), 1:set([3,4,5]), 2:set([]), 3:set([]), 4:set([6,7,8]), 5:set([]), 6:set([9,10,11,12]), 7:set([]),8:set([]),9:set([]),10:set([13,15,17]),11:set([14,16,18]),12:set([]),13:set([21,22]),14:set([19,20]),15:set([]),16:set([]),17:set([]),18:set([]),19:set([]),20:set([24,26]),21:set([23,25]),22:set([]),23:set([29,30]),24:set([27,28]),25:set([]),26:set([]),27:set([]),28:set([32,34,36]),29:set([31,33,35]),30:set([]),31:set([]),32:set([]),33:set([]),34:set([]),35:set([]),36:set([])}

# Dictionary of search terms revelant for finding each status (i.e. {##: [['<SEARCH_TERM_1>','<PATH_TO_FILE_OR_FOLDER>'],['<SEARCH_TERM_N>','<PATH_TO_FILE_OR_FOLDER>']], ...})

# The next Hess final highOpttol_N should be created once the next run is beginning while the SadPoint highOpttol_N should be created as soon as that run is completed (this should eventually be fixed so that the two are consistent with each other, this is simply a convention made to ease current edits)

# ^ Update: might be able to get rid of nodes 2 and 3 and have both cases where the highOpttol folder is created only when making another highOpttol case (as has always been down)

#THIS LINE WAS REMOVED: not len(os.listdir(path))#

#Might be the fix for nodes 19 and 22
#and (not Path(./Hess_RHS/).is_dir())

search = {0: ['fldr','SadPoint',''],
        1:['word','SUCCESSFUL','SadPoint/TS_SadPoint.dat'],
        2:['word','FAILURE TO LOCATE STATIONARY POINT', 'SadPoint/TS_SadPoint.log'],
        3:['fldr','Hess_final','not Path(path).is_file()'],
        4:['fldr','Hess_final',''],
        5:['fldr','Hess_final', '', 'not Path(path).is_dir()'],
        6:['word','1 IMAGINARY FREQUENCY','Hess_final/TS_Hess.log'],
        7:['word','IMAGINARY FREQUENCY','Hess_final/TS_Hess.log','int(line.strip()[0])>=2'],
        8:['word','ABNORMALLY','Hess_final/TS_Hess.log'],
        9:['fldr','IRC_backward', '', 'not Path(path).is_dir()'],
        10:['fldr','IRC_backward',''],
        11:['fldr','IRC_forward',''],
        12:['fldr','IRC_forward', '', 'not Path(path).is_dir()'],
        13:['word',' NORMALLY','IRC_backward/TS_IRCb.log', 'nodeExists and (grep("STOPPING BECAUSE GRADIENT IS BELOW OPTTOL", "TS_IRCb.log")=="")'],
        14:['word',' NORMALLY','IRC_forward/TS_IRCf.log','nodeExists and (grep("STOPPING BECAUSE GRADIENT IS BELOW OPTTOL", "TS_IRCf.log")=="")'],
        15:['word','ABNORMALLY','IRC_backward/TS_IRCb.log','nodeExists and (grep("STOPPING BECAUSE GRADIENT IS BELOW OPTTOL", "TS_IRCb.log")=="")'],
        16:['word','ABNORMALLY','IRC_forward/TS_IRCf.log','nodeExists and (grep("STOPPING BECAUSE GRADIENT IS BELOW OPTTOL", "TS_IRCf.log")=="")'],
        17:['word','STOPPING BECAUSE GRADIENT IS BELOW OPTTOL','IRC_backward/TS_IRCb.log'],
        18:['word','STOPPING BECAUSE GRADIENT IS BELOW OPTTOL','IRC_forward/TS_IRCf.log'],
        19:['fldr','Opt_RHS','','not Path(path).is_dir()'],
        20:['fldr','Opt_RHS',''],
        21:['fldr','Opt_LHS',''],
        22:['fldr','Opt_LHS','','not Path(path).is_dir() '],
        23:['word','SUCCESSFUL','Opt_LHS/TS_OptLHS.dat','Path("/Opt_LHS/README").is_file()'],
        24:['word','SUCCESSFUL','Opt_RHS/TS_OptRHS.dat','Path("/Opt_RHS/README").is_file()'],
        25:['word','FAILURE TO LOCATE STATIONARY POINT','Opt_LHS/TS_OptLHS.log','not Path("/Opt_LHS/README").is_file()'],
        26:['word','FAILURE TO LOCATE STATIONARY POINT','Opt_RHS/TS_OptRHS.log','not Path("/Opt_RHS/README").is_file()'],
        27:['fldr','Hess_RHS','','not Path(path).is_dir()'],
        28:['fldr','Hess_RHS',''],
        29:['fldr','Hess_LHS',''],
        30:['fldr','Hess_LHS','','not Path(path).is_dir()'],
        31:['word','ABNORMALLY','Hess_LHS/TS_Hess.log'],
        32:['word','ABNORMALLY','Hess_RHS/TS_Hess.log'],
        33:['word','NORMALLY','Hess_LHS/TS_Hess.log','not "IMAGINARY" in line'],
        34:['word','NORMALLY','Hess_RHS/TS_Hess.log','not "IMAGINARY" in line'],
        35:['word','IMAGINARY FREQUENCY','Hess_LHS/TS_Hess.log'],
        36:['word','IMAGINARY FREQUENCY','Hess_RHS/TS_Hess.log']
        }
# Dictionary of actions necessary for creating respective input files for discovered status
#actions = {
#         3:['ERROR: SadPoint not converged in highOpttol_N, exiting code!'],
#         5:['ERROR: SadPoint not converged, exiting code!'],
#         6:['Creating Final Hessian in highOpttol_N','HdrGemVec','TS_Hess.inp'],
#         9:['Creating First Final Hessian','HdrGemVec','TS_Hess.inp'],
#        10:['Creating restart (timeout?) run for abnormal Final Hessian','HdrGemVibVec','TS_Hess.inp'],
#        11:['Creating highOpttol_N run in SadPoint','HdrGemHssGrdVec','TS_SadPoint.inp'],
#        13:['Creating IRC backward run','HdrGemHssVec','TS_IRCb.inp'],
#        15:['Creating IRC forward run','HdrGemHssVec','TS_IRCf.inp'],
#        19:['Creating restart run for abnormal (or stopped grad) IRC backward calculation','HdrGemIrcHssGrdVec','TS_IRCb.inp'],
#        20:['Creating restart run for abnormal (or stopped grad) IRC forward calculation','HdrGemIrcHssGrdVec','TS_IRCf.inp'],
#        21:['Creating Opt_RHS geometry optimization','HdrGemVec','TS_OptRHS.inp'],
#        24:['Creating Opt_LHS geometry optimization','HdrGemVec','TS_OptLHS.inp'],
#        27:['Creating Opt_LHS restart run (Vec from min Energy)','HdrGemVec','TS_OptLHS.inp'],
#        28:['Creating Opt_RHS restart run (Vec from min Energy)','HdrGemVec','TS_OptRHS.inp'],
#        29:['Creating Hess_RHS run','HdrGemVec','TS_Hess.inp'],
#        32:['Creating Hess_LHS run','HdrGemVec','TS_Hess.inp'],
#        33:['Creating restart run for Hess LHS','HdrGemVibVec','TS_Hess.inp'],
#        34:['Creating restart run for Hess RHS','HdrGemVibVec','TS_Hess.inp'],
#        33:['Creating summary of necessary reactamt energies','smy','summaryLHS.txt'],
#        34:['Creating summary of necessary product energies','smy','summaryRHS.txt']
#        }

# If it is useful later on, the "codes" can be generalized (i.e. every case requires a 'Hdr' and 'Gem')

#codes = {'hess': 'Vec'
#        'hess rst': 'VibVec'
#        'sadpoint': 'HssGrdVec'
#


