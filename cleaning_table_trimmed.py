import os
import arcpy

arcpy.env.overwriteOutput = True
arcpy.env.outputMFlag = "Disabled"
arcpy.env.extent = "MAXOF"

def fieldupdater(fk, fieldname):
    #lists all fields in feature class where fieldname variable is in
    fields = [f.name for f in arcpy.ListFields(fk) if fieldname in f.name]
    #uses updatecursor to trawl through each row
    with arcpy.da.UpdateCursor(fk, fields) as cursor:
        for row in cursor:
            #accumulates all field values and puts them into the last field
            row[-1] = ", ".join(map(str, sorted([f for f in list(set(row)) if f != "" and f != " "])))
            cursor.updateRow(row)
    arcpy.DeleteField_management(fk, fields[:-1])

    
def cleaning_tables(fc, sektorfield, originfield, temakodefield):
    fieldsdelete = [f.name for f in arcpy.ListFields(fc) if "FID_" in f.name]
    arcpy.DeleteField_management(fc, fieldsdelete)

    arcpy.AddField_management(fc, sektorfield, "TEXT")
    arcpy.AddField_management(fc, originfield, "TEXT")
    arcpy.AddField_management(fc, temakodefield, "TEXT")

    fieldupdater(fc,"tema" )
    fieldupdater(fc, "sektor")
    fieldupdater(fc, "kode")
#
#    fieldsdelete = [f.name for f in arcpy.ListFields(fc) if
#                    "sektor_" in f.name and f.name != sektorfield or f.name == "sektor"]     + [f.name for f in arcpy.ListFields(fc) 
#                    if "tema_" in f.name and f.name != originfield or f.name == "tema"] + [f.name for f in arcpy.ListFields(fc) 
#                    if "kode_" in f.name and f.name != temakodefield or f.name == "tema"]
#    arcpy.DeleteField_management(fc, fieldsdelete)

anvendelseskode = "ng"
outputname = "ng_union"

sektorfnl = "sektor"
originfnl = "tema"
temakodefnl = "kode"
finaldir = r"C:\havplan\projekter\havplans_temalag_7_arbjgrpmode_11_okt\data"
outputfnl = os.path.join(finaldir, "intermediate", anvendelseskode, "samlede", outputname+".shp")
outputfnldslv = os.path.join(finaldir, "output", outputname + "_dslv"+".shp")

print ("cleaning table")
cleaning_tables(outputfnl, sektorfnl, originfnl, temakodefnl)

print ("dissolving shapefile")
arcpy.Dissolve_management(outputfnl, outputfnldslv, [sektorfnl, originfnl, temakodefnl])
#arcpy.Delete_management(outputfnl)