import csv, os, arcpy

csvfilen = os.path.join(r"C:\Users\B039723\Dropbox\havplan_python\samplacering", "samplac_dictreaderfmt_new.csv")

fc = os.path.join(#r"C:\havplan\havplan_data\kategorier\ru\final", "reserverede_udviklingszone_dslv_onlyintersectingsektors_w_EUID_n_IK.shp"
       r"C:\havplan\havplan_data\kategorier\final_24_07\ru_clip_zones", "ru_Transportdslv_cut_eu_ik.shp"
        )
rows_of_interest = [2
        ]
rows_of_interest[:] = [x - 1 for x in rows_of_interest]

def value_assigner(anvendelsesformer):
    with open(csvfilen) as csvfile:
        readCSV = csv.DictReader(csvfile, delimiter=';')
        rowcount = 0
        minimumsam = 99
        for row in readCSV:
            rowcount += 1
            if rowcount in (rows_of_interest):
                print ("sammenligner datasættene med anvendelsesformerne: ", row["titel"])
                for i in anvendelsesformer:
                    
                    row_vals = [value for key, value in row.items() if i.lower() in key.lower().replace(" ", "_")]
                    print (row_vals)
                    if not row_vals:
                        row_vals = [99]
                    min_row_val = min(row_vals)
                    if int(min_row_val) < int(minimumsam):
                        minimumsam = min_row_val
                    
        return (minimumsam)


fieldnames = ([f.name for f in arcpy.ListFields(fc) if 
               "origin"
               #"origin_f_"
               in f.name])
if len(fieldnames)< 2:
    num_of_cat = 1
else:
    num_of_cat = 2
    
fieldnam ="sameksist2"
if len(arcpy.ListFields(fc,fieldnam))==0:  
    arcpy.AddField_management(fc, fieldnam, "LONG")
fieldnames = fieldnames + [fieldnam]    

with arcpy.da.UpdateCursor(fc, fieldnames) as cursor:
        print (fieldnames)
        for row in cursor:
            rowlist = []
            eu = row[0].split(", ")
            if num_of_cat > 1:
                
                ik = row[1].split(", ")
                ikeu = sorted([f for f in (eu + ik) if f not in (" ", "")])
                sameksistens = row[2]
                print ("\n","rækken indeholder datasættene: ", ikeu)
                if not ikeu:
                    row[2] = 99
                else:
                    va =  (value_assigner(ikeu))
                    print (va)
                    row[2] = int(va)
            else:
                ikeu = sorted([f for f in eu if f not in (" ", "")])
                sameksistens = row[1]
                print ("\n",ikeu)
                va =  (value_assigner(ikeu))
                print (va)
                row[1] = int(va)
            cursor.updateRow(row)
            
        