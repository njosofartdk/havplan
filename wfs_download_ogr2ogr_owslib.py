##downloading wfs, 1. draft
##scriptet fungerer kun i qgis - hvis det køres direkte i en IDE, opstår der underlige fejl. 
## scriptet har dybest set 3 faser:
## 1. det tjekker om filen er brugbar og er en wfs
## 2. hvis den er det, kontakter den wfs-serveren og prøver at finde wfs-versionen og lagets navn påserveren
## 3. den downloader laget
import csv, os, subprocess
from owslib.wfs import WebFeatureService as wfsmod


# output folder hvor wfs-shapefilerne skal placeres
worksp = r"C:\havplan\projekter\havplans_temalag_7_arbjgrpmode_11_okt\data\input\havplans_data_til_7arbjdsmode"
wfsfolder = os.path.join(worksp, "wfs")
if not os.path.exists(wfsfolder):
    os.makedirs(os.path.join(wfsfolder))

#directory til og navnet på .csv filen der indeholder html links til wfs 
inputliste = r"C:/havplan/projekter/havplans_temalag_7_arbjgrpmode_11_okt/data/input/input_lists/oversigt_data_24_sep_7_internPC.csv" 

countwfs = 0


#aflæser .csv filen der indeholder informationer omkring hvordan hvert enkelt datasæt skal håndteres
with open(inputliste) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=';')
    readCSV = csv.DictReader(csvfile, delimiter=';')
    for row in readCSV:
        brugbar = row["brugbart ift. havplan laget?"]
        if brugbar.lower() == "ja":
            #hvis rækken (filen) i csv'en er brugbar, tjekkes det om det er en wfs
            wfs_check = row["wfs"]
            if wfs_check.lower() == "sand":
                countwfs += 1
                #assigner wfs filens navn og url/html linket til to variabler
                name = row["filnavn(wfs, dl, shp)"]
                url = row["wfs_url"]
                print ("leder efter: ", name, " i urlen: ", url)
                #sætter nogle generelle OGR2OGR configuration settings up i variabler, så man let kan tilkalde dem senere
                conf, confoptionuserpw, confoptionhttp, confirm, confoptionauth, basic = "--config", "GDAL_HTTP_USERPWD", "GDAL_HTTP_UNSAFESSL", "YES", "GDAL_HTTP_AUTH", "BASIC"
                form, getfeat, ver = "ESRI Shapefile", "&request=GetFeature", "&version="
                
                #outputtet får samme filnavn som på wfs-serveren
                outputfold = os.path.join(wfsfolder, name+".shp")
                
                #hvis brugernavn/password er nødvendigt, sættes det op i korrekt format til ogr2ogr og owslib
                pws = row["password?"]
                if pws.lower() == "ja":
                    print (name, "needs password:", pws)
                    login = row["brugernavn"]
                    password1 = row["password"]
                    userinfo= "{}:{}".format(login, password1)
                    wfs = wfsmod(str(url), username = login, password = password1)
                else: 
                    #qgis havde problemer med nedenstående specifikke link, så har sat det op så den kan håndtere det. 
                    if "https://arealinformation.miljoeportal.dk/gis/services/DAIdb/MapServer/WFSServer" in url:
                        version = "1.0.0"
                    else:
                        print (url)
                        wfs = wfsmod(str(url))
                        version =  (wfs.identification.version)

                    userinfo = None
                                
                #checking if password and https configurations are needed in ogrinfo command
                #connects to wfs and gathers information on the wfs
                if "https" in url and userinfo:    
                    cmd1 = [r"C:\OSGEO4W64\bin\ogrinfo.exe",conf, confoptionhttp, confirm, conf, confoptionauth, basic, conf, confoptionuserpw, userinfo , "WFS:"+url, "-so" ]
                elif "https" in url:
                    cmd1 = [r"C:\OSGEO4W64\bin\ogrinfo.exe",conf, confoptionhttp, confirm , "WFS:"+url, "-so" ]
                elif userinfo:
                    cmd1 = [r"C:\OSGEO4W64\bin\ogrinfo.exe", conf, confoptionauth, basic, conf, confoptionuserpw, userinfo , "WFS:"+url, "-so" ]
                else: 
                    cmd1 = [r"C:\OSGEO4W64\bin\ogrinfo.exe", "WFS:"+url, "-so" ]
                
                #trying to find the layers name in wfs
                p = subprocess.check_output(cmd1)
                k = [str(x).replace("b'","").replace("'","") for x in p.split()] 
                print (k)
                nameWprefix = ([x for x in k if name in x])[0]
                print (nameWprefix)                
                
                #typename/s skal håndteres forskelligt på wfs 1.x.0 og 2.0.0 servere. 
                if str(version) == "2.0.0":
                    typenamerequest = "&TYPENAMES="+nameWprefix
                else:
                    typenamerequest = "&TYPENAME="+nameWprefix
                    #tror ikke de to næste linjer er nødvendige mere. 
#                if name == "jupiter_boringer_ws":
#                    typenamerequest = "&layers="+name
                
                #checking if password and https are needed in ogr2ogr configuration download command
                
                if "https" in url and userinfo:    
                    cmd = [r"C:\OSGEO4W64\bin\ogr2ogr.exe",
                           conf, confoptionhttp, confirm,  conf, confoptionauth, basic, conf, confoptionuserpw, userinfo,
                        "-f",form, 
                       outputfold, 
                        "WFS:"+url+typenamerequest]
                elif "https" in url:
                        cmd = [r"C:\OSGEO4W64\bin\ogr2ogr.exe", 
                               conf, confoptionhttp, confirm,
                        "-f",form, 
                        outputfold, 
                        "WFS:"+url+typenamerequest]
                elif userinfo:
                        cmd = [r"C:\OSGEO4W64\bin\ogr2ogr.exe", 
                               conf, confoptionauth, basic, conf, confoptionuserpw, userinfo,
                        "-f",form, 
                        outputfold, 
                        "WFS:"+url+typenamerequest]
                else: 
                            cmd = [r"C:\OSGEO4W64\bin\ogr2ogr.exe",
                        "-f",form, 
                        outputfold, 
                        "WFS:"+url+typenamerequest]
                            
                print (cmd)
                #downloads layer from wfs, med command der er genereret i ovenstående script. 
                subprocess.check_call(cmd)

print ( countwfs)
