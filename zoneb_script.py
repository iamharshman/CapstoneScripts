#Create overlapping buffer rings from the edge of an inner buffer ring where,
#the outer buffer distance is from the input polygons.
#This is accomplished by erasing the outer ring with a temporary inner ring.
#The erase is performed for each input polygon to allow for overlapping polygons in the outer buffer.
#Each buffer ring from the final output is assigned an ID to correspond with the input polygons.
#IDs need to be populated in the input polygon prior to running the script


import arcpy

arcpy.env.overwriteOutput = True

#input polygon to be buffered
buildings = #[path to polygon]

#first buffer. store in memory
temp30ftBuffer = "in_memory/buffer30

#second buffer. store in memory
temp100ftBuffer = "in_memory/buffer100

#workspace to store output
workspace = #path to folder, gdb, or mdb

#output name
outputName = "ZONE_B"

#create the inner buffer from input polygons then create the second buffer
try:
    arcpy.Buffer_analysis(buildings,temp30ftBuffer,"30 FEET","FULL","ROUND","NONE","","PLANAR")
    print "done with 30ft"
except:
    print arcpy.GetMessages()
try:
    arcpy.Buffer_analysis(buildings,temp100ftBuffer,"100 FEET","FULL","ROUND","NONE","","PLANAR")
    print "done with 100ft"
except:
    print arcpy.GetMessages()

#need to make layers in order to do a selection set    
arcpy.MakeFeatureLayer_management(temp30ftBuffer,"buffer30Lyr")
arcpy.MakeFeatureLayer_management(temp100ftBuffer,"buffer100Lyr")

#create empty feature class for the final output
zoneB = arcpy.CreateFeatureclass_management(workspace,outputName,"POLYGON",temp100ftBuffer,"DISABLED","DISABLED",temp100ftBuffer)

#ID field name from input polygon to be assinged to the final buffers
BLDID = "ID"

#create cursor to search through the outer buffer
cursor = arcpy.SearchCursor(temp100ftBuffer)


for row in cursor:
    #get value of ID field
    id = row.getValue(BLDID)
    #create sql for selection query to issolate one record at a time
    sql = '"' + BLDID + '"' + '=' + str(id)
    #select the inner ring for the specific ID
    select30Ring = arcpy.SelectLayerByAttribute_management("buffer30Lyr","NEW_SELECTION",sql)
    #select the outer ring for the specific ID
    select100Ring = arcpy.SelectLayerByAttribute_management("buffer100Lyr","NEW_SELECTION",sql)
    #temp output for erase
    output = "in_memory/erase"
    #erase the outer ring where the inner ring overlaps
    eraseOutput = arcpy.Erase_analysis(select100Ring,select30Ring,output)
    #append the results from the erase to the created feature class
    arcpy.Append_management(eraseOutput,zoneB,"NO_TEST")
    del output

del cursor
print "done"
