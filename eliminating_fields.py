import arcpy, os

arcpy.env.overwriteOutput = True

worksp = os.path.join(r"C:\havplan\havplan_data", "kategorier")
ru = "ru"
eu = "eu"
ik = "ng"

zone = r'C:\havplan\havplan_data\kategorier\final_24_07\havplan_temalag\eksisterende_udviklingszone_sngprt.shp'
1
#def unique_values(table, field):
#    with arcpy.da.SearchCursor(table, [field]) as cursor:
#        unique =  sorted({row[0] for row in cursor})
#        sektlist = []
#        for i in unique:
#            splitted = i.split(", ")
#            for x in splitted:
#                if x not in sektlist:
#                    sektlist.append(x)
#        return (sektlist)
#
#sektors = (unique_values(zone, "sektor_fnl"))
#for sektor in sektors:
#    
#    arcpy.SelectLayerByAttribute_management(zone, "", '"POLY_AREA" < 500 AND "sektor_fnl" LIKE {}'.format("'%{}%'".format(sektor)))
#    arcpy.Eliminate_management(zone, )
#    print (os.path.join(os.path.dirname(zone), "test_eliminate_fiskeri.shp")) 
tmpfile = "in_memory/tmpfile"
arcpy.MakeFeatureLayer_management(zone, tmpfile)
arcpy.SelectLayerByAttribute_management(tmpfile, "", '"POLY_AREA" < 500 AND "sektor_fnl" LIKE {}'.format("'%Fiskeri%'"))
output = (os.path.join(os.path.dirname(zone), "test_eliminate_fiskeri.shp")) 
arcpy.Eliminate_management(tmpfile, output, "", '"sektor_fnl" NOT LIKE {}'.format("'%Fiskeri%'"))
