import csv, os
import arcpy
#opsætter en masse work enviroment ting 
arcpy.env.overwriteOutput = True
arcpy.env.outputMFlag = "Disabled"
arcpy.env.outputZFlag = "Disabled"
arcpy.env.extent = "MAXOF"


def cleaning_tables(fc, originfield, searchname):
    arcpy.AddField_management(fc, originfield, "TEXT")
    #lists all fields in feature class where fieldname variable is in
    fields = [f.name for f in arcpy.ListFields(fc) if searchname in f.name]
    #uses updatecursor to trawl through each row
    with arcpy.da.UpdateCursor(fc, fields) as cursor:
        for row in cursor:
            #accumulates all field values and puts them into the last field
            row[-1] = ", ".join(map(str, sorted([f for f in list(set(row)) if f != "" and f != " "])))
            cursor.updateRow(row)
    arcpy.DeleteField_management(fc, fields[:-1])
    
#tjekker om geometrien i featuren er "ren", ellers repareres den. 
def chkgeom(file):
    tbl = "in_memory/tablewitherrors"
    arcpy.CheckGeometry_management(file, tbl)
    if int(arcpy.GetCount_management(tbl)[0]) > 0:
        arcpy.RepairGeometry_management(file)
    arcpy.Delete_management(tbl)

#funktion der tilføjer et felt og udregner derefter den samme værdi i alle feltets rækker
def addfield(fil, fieldvalue, fieldname):
    arcpy.AddField_management(fil, fieldname, "TEXT") # str(row[14]) og "TEXT" med "LONG" skal udskiftes med bare row[x] når jeg har tilført et int. ID til hvert datasæt
    arcpy.CalculateField_management(fil, fieldname, "'{}'".format(str(fieldvalue).replace(", ", "-" )))    

def piler(filez, tema, temaforkort, sekt, dicts, dict2):
    fieldsdelete= [f.name for f in  arcpy.ListFields(filez) if f.name != "FID" and "Shape" != f.name]
    arcpy.DeleteField_management(filez, fieldsdelete)
    addfield(filez, tema, "tema1")
#    addfield(filez, sekt, "sektor1" )
#    addfield(filez, temaforkort, "kode1")
    chkgeom(filez)
    if dicts.get(sekt) == None: 
        dicts[sekt] = [filez]
    else: 
        dicts[sekt].append(filez)
    if dict2.get(sekt) == None: 
        dict2[sekt] = temaforkort


def categorizer(csvfilen, dirlists, filelist, anvendelsesklasse):
    countc = 0
    countf = 0
    classdict = {}
    temakodedict = {}
#   #aflæser .csv filen der indeholder informationer omkring hvordan hvert enkelt datasæt skal håndteres
    with open(csvfilen) as csvfile:
        readCSV = csv.DictReader(csvfile, delimiter=';')
        
        for row in readCSV:
            brugbar = row["brugbart ift. havplan laget?"]
    
            if brugbar.lower() == "ja": #hvis datasættet er brugbar, sæt en masse variabler
                filnavn = row["filnavn(wfs, dl, shp)"]
                category = row["CATEGORY"]
                sektor = row["sektor"]
                temanavn = row["tema"]
                temakode = row["forkortelse"]
                #hvis anvendelseskoden, f.eks "eu/ru" er længere end 2, dvs. den indeholder flere anveldeskoder, så bruges den første anvendelseskode
                if len(category) > 2:
                    category = category.split("/")[0].lower()
                else: 
                    category = category.lower()
                    
                if category == anvendelsesklasse.lower(): 
                    countc += 1
                    if filnavn.lower() in filelist:
                        countf += 1
                        filedir = dirlists[(filelist.index(filnavn.lower()))]
                        print("{} matches {}".format(filedir, filnavn))
                        
                        #laver temporary fil
                        tmpfile2 = "in_memory/tmp2{}".format(filnavn.replace("-","_").replace(" ", "_"))
                        arcpy.MultipartToSinglepart_management(filedir, tmpfile2)
                        desc = arcpy.Describe(tmpfile2)
                        if str(desc.ShapeType) != "Polygon": #hvis datasættet ikke er en polygon, men f.eks linjer elle rpunkter, laves der en lille buffer rundt om.
                            tmpfile = "in_memory/tmp{}buff".format(filnavn.replace("-","_").replace(" ", "_"))
                            buffsize = row["buffersize"]
                            print ("non-polygon found, buffer applied to it: ", buffsize)
                            arcpy.Buffer_analysis(tmpfile2,tmpfile, "{} Meters".format(buffsize))
                            arcpy.Delete_management(tmpfile2)
                            piler(tmpfile, temanavn, temakode, sektor, classdict,temakodedict)
                        else:
                            piler(tmpfile2, temanavn, temakode, sektor, classdict, temakodedict)
                    else:
                        if filnavn == "" or filnavn == " ":
                            countc -= 1

                        else:
                            print (filnavn, " is missing")
    print (countc - countf, " are missing")
    return classdict, temakodedict


#input der skal ændres på
inputworksp = r"C:\havplan\projekter\havplans_temalag_7_arbjgrpmode_11_okt\data\input\havplans_data_til_7arbjdsmode"

worksp = r"C:\havplan\projekter\havplans_temalag_7_arbjgrpmode_11_okt\data\intermediate"
#r"C:\Users\B039723\Documents\Filkassen\havplan\projekter\havplans_temalag_7_arbjgrpmode_11_okt\data\intermediate"
throw = "sectors"
final = "samlede"
clip = "clip"
liste = os.path.join(r"C:\Users\B039723\Documents\Filkassen\havplan\BaseData\lists","oversigt_data_24_sep_7_internPC.csv")

##laver to lister (lidt ineffektivt), 1) dirlist nideholder hele path'en til filen, 2) filelist indeholder filenavnet (samt extensionen ".shp")
filelist_UK = []
dirlist = []

#for root, dirs, files in os.walk(os.path.join(inputworksp, dataspace)):
for root, dirs, files in os.walk(inputworksp):
    for file in files:
        if file.endswith(".shp"):
            dirlist.append((os.path.join(root, file)))
            filelist_UK.append(file.lower().replace("ø", "oe")
            .replace("æ", "ae").replace("å", "aa").replace(".shp", ""))

anvendelseskoder = ["ru", "ti", "eu", "ng"]
#outputname = "reserverede_udviklingszone"
for anvendelseskode in anvendelseskoder:
    outputsp = anvendelseskode
    
    if not os.path.exists(os.path.join(worksp, outputsp)):
        os.makedirs(os.path.join(worksp, outputsp))
    if not os.path.exists(os.path.join(worksp, outputsp,throw )):
        os.makedirs(os.path.join(worksp, outputsp, throw))
    throwoutput = os.path.join(worksp, outputsp, throw)
    if not os.path.exists(os.path.join(worksp, outputsp, throw,clip )):
        os.makedirs(os.path.join(worksp, outputsp, throw,clip ))
    clipoutput = os.path.join(worksp, outputsp, throw,clip )
    if not os.path.exists(os.path.join(worksp, outputsp,final )):
        os.makedirs(os.path.join(worksp, outputsp, final))
    finaloutput = os.path.join(worksp, outputsp, final)
    
    filedict, temakodedict = categorizer(liste, dirlist, filelist_UK, anvendelseskode)
    print (temakodedict)
    sektordslv = "sektor_dsl"
    origindslv, origin = "tema_dsl", "tema"
    temakodedslv = "kode_dsl"
    fiddslv, fid = "fid_dslv", "fid_"
    sektorlist = []
    for key, value in filedict.items():
        print (key, " contains: ", value)
        keyz = str(key).replace(" ", "_").replace("(", "").replace(")","").replace("/", "_")
        output = os.path.join(throwoutput, anvendelseskode + "_" + keyz+".shp")

            #for hver sektor (olie/gas, vindenergi, fiskeri etc,)hvor der er mere end 1 datasæt,
            #laves der en union, som dissolves og "rengøres" for rækker med ens sektor og datasæt origin
            arcpy.Union_analysis(value, output, "", "", "NO_GAPS")  
            #i virkeligheden kunne "cleaning_tables" nok fjernes, da dens funktion løses senere
            cleaning_tables(output, origindslv, origin )
            cleaning_tables(output, fiddslv, fid)
            lyrz = "layer"
            arcpy.MakeFeatureLayer_management(output, lyrz, " !{}! <> -1 OR !SHAPE.AREA@SQUAREKILOMETERS! <= 1 AND !{}! = -1".format(fiddslv, fiddslv)
            arcpy.SelectLayerByAttribute_management (lyrz, "", "!{}! = -1".format(fiddslv))
            tmpelim = "in_memory/tmp3_elim"
            arcpy.Eliminate_management (lyrz, tmpelim )
            output2 = os.path.join(throwoutput, anvendelseskode + "_" + keyz+"dslv"+".shp")
            arcpy.Dissolve_management(tmpelim, output2, [origindslv], "", "SINGLE_PART")
            addfield(output2, str(key), sektordslv )
            addfield(output2, str(temakodedict[key]), temakodedslv)
            sektorlist.append(os.path.join(throwoutput, anvendelseskode + "_" + keyz+"dslv"+".shp"))
            arcpy.Delete_management(output)
        for i in value:         
            arcpy.Delete_management(i)
    print (sektorlist)
    for lyr in sektorlist:
        print (lyr)
        arcpy.Clip_analysis(lyr, r"C:\Users\B039723\Documents\Filkassen\havplan\BaseData\analysis_extent\final\merg_eez_geodk_sngprt_poly_removeland_dslv.shp", 
                            os.path.join(clipoutput,os.path.basename(lyr)))






