import os, csv

csvfilen = csvfilen = os.path.join(r"E:\havplan_data\lists\correcting_overlap_analysis_list", "correcting.csv")
typelist = ["vind", "akva", "olie", "rastof", "infra"]
for anven in typelist:
    sektdict = {}
    anvendict = {}
    with open(csvfilen) as csvfile:
            readCSV = csv.DictReader(csvfile, delimiter=';')
            for row in readCSV:
                fid = row[anven]
                tblfid = row[anven+"_fid"]
                sekt1 = row[anven+"_sektor_fnl"]
                origin = row[anven+"_origin_fnl"]
                if anven != "olie":
                    sekt2 = row[anven+"_sektor_f_1"]
                    origin2 = row[anven+"_origin_f_1"]
                    if sektdict.get(tblfid) == None and (sekt1 != "" or sekt2 != ""): 
                        sektdict[tblfid] = [sekt1, sekt2]
                    elif sekt1 != "":
                        sektdict[tblfid].append(sekt1)
                    elif sekt2 != "": 
                        sektdict[tblfid].append(sekt2)
                        
                    if anvendict.get(tblfid) == None and (origin != "" or origin2 != ""): 
                        anvendict[tblfid] = [origin, origin2]
                    elif origin != "":
                        anvendict[tblfid].append(origin)
                    elif origin2 != "": 
                        anvendict[tblfid].append(origin2)
                else:
                    if sektdict.get(tblfid) == None and (sekt1 != ""): 
                        sektdict[tblfid] = [sekt1]
                    elif sekt1 != "":
                        sektdict[tblfid].append(sekt1)
                    if anvendict.get(tblfid) == None and (origin != ""): 
                        anvendict[tblfid] = [origin]
                    elif origin != "":
                        anvendict[tblfid].append(origin)
    
                        
    nycsvfile = open(os.path.join(r"E:\havplan_data\lists\correcting_overlap_analysis_list",anven+"_"+"testfile.txt"), "w")
    with open(csvfilen) as csvfile:
        readC = csv.DictReader(csvfile, delimiter=';')
        for row in readC:
            fid = row[anven]
            sektlist2 = []
            anvenlist2 = []
            if sektdict.get(fid)!= None:
                if len(sektdict[fid]) > 1:
                    sektlist1 =  [f.split(", ") for f in sektdict[fid] if f != " "]
                    for i in sektlist1:
                        for x in i:    
                            sektlist2.append(x.replace("_", " ").replace("aa", "å").replace("ae", "æ").replace("oe", "ø"))
                    print (sektlist2)
                    sektstr = ", ".join(list(set(sektlist2)))
                else:
                    sektstr = sektdict[fid][0]
                print (sektstr)
                
                if len(anvendict[fid]) > 1:
                    anvenlist1 =  [(f.split(", ")) for f in anvendict[fid] if f != " "]
                    for i in anvenlist1:
                        for x in i:    
                            anvenlist2.append(x.replace("_", " ").replace("aa", "å").replace("ae", "æ").replace("oe", "ø"))
                    print (anvenlist2)
                    anvenstr = ", ".join(list(set(anvenlist2)))
                else:
                    anvenstr = anvendict[fid][0]
                print (anvenstr)
                if fid != "":
                    nycsvfile.write("\n" +"{0}; {1}; {2}".format(fid, sektstr, anvenstr))
            else:
                nycsvfile.write("\n")
    nycsvfile.close()
            
            
            

#    print (sektdict)
#                print ("anvend: ", anven, " med fid: ", fid, " ", tblfid, " ", sekt1, " ",origin )