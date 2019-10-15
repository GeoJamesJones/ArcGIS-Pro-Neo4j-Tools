import arcpy
import json
import os
from py2neo import Graph
from ast import literal_eval

def main():
    graph_connection = arcpy.GetParameterAsText(0)
    output_workspace = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(output_workspace)
    gc_tuple = literal_eval(graph_connection)

    g = Graph(gc_tuple[0], auth=(gc_tuple[1], gc_tuple[2]))
    arcpy.AddMessage("Successfully connected to Graph!")

    closeness = "CALL algo.closeness('Airport', 'CONNECTION', {write:true, writeProperty:'closeness'})"
    betweenness = "CALL algo.betweenness('Airport','CONNECTION', {direction:'out',write:true, writeProperty:'betweenness'})"
    in_degree = 'CALL algo.degree("Airport", "CONNECTION", {direction: "incoming", writeProperty: "in-degree"})'
    out_degree = 'CALL algo.degree("Airport", "CONNECTION", {direction: "outgoing", writeProperty: "out-degree"})'
    pagerank = "CALL algo.pageRank('Airport', 'CONNECTION',{iterations:20, dampingFactor:0.85, write: true,writeProperty:'pagerank'})"
    base_cypher = "START source=node(*) MATCH (source)-[r]->(target) RETURN source,r.airline,target;"

    # Checks to see if the output workspace is a file geodatabase.  If not, returns error and forces
    # user to use a file geodatabase. 
    if desc.dataType != 'Workspace':
        arcpy.AddError('Please select a file geodatabase to output your files.')
        exit()

    arcpy.AddMessage("Calculating closesness centrality.")
    g.run(closeness)
    arcpy.AddMessage("Calculating betweenness centrality.")
    g.run(betweenness)
    arcpy.AddMessage("Calculating in-degree centrality.")
    g.run(in_degree)
    arcpy.AddMessage("Calculating out-degree centrality.")
    g.run(out_degree)
    arcpy.AddMessage("Calculating pagerank centrality.")
    g.run(pagerank)

    results = g.run(base_cypher).data()

    arcpy.AddMessage('Starting ingest of data')

   # Sets the spatial reference for the output feature class to WGS 1984.
    sr = arcpy.SpatialReference(4326)

    # Creates the necessary feature classes
    arcpy.AddMessage("Creating feature classes")
    arcpy.CreateFeatureclass_management(output_workspace, 'Nodes_Centrality', "POINT", None, "DISABLED", "DISABLED", sr)
    arcpy.CreateFeatureclass_management(output_workspace, 'Edges', "POLYLINE", None, "DISABLED", "DISABLED", sr)
    node_fc = os.path.join(output_workspace, "Nodes_Centrality")
    edge_fc = os.path.join(output_workspace, "Edges")
    # Adds the necessary fields to the feature class
    arcpy.management.AddFields(node_fc, "name TEXT # 255 # #;location TEXT # 255 # #;state TEXT # 255 # #;country TEXT # 255 # #;start_date DATE;code TEXT # 10 # #; betweenness DOUBLE; closeness DOUBLE; in_degree DOUBLE; out_degree DOUBLE; pagerank DOUBLE")
    arcpy.management.AddFields(edge_fc, "source_node TEXT 'Source Node' 255 # #;target_node TEXT 'Target Node' 255 # #;airline TEXT # 150 # #")
    
    # Fields to be edited when creating the Insert Cursor objects for the node and edge tables
    node_fields = ["SHAPE@XY", "name", "location", "state", "country", "start_date", "code", "betweenness", "closeness", "in_degree", "out_degree", "pagerank"]
    edge_fields = ["SHAPE@", "source_node", "target_node", "airline"]

    # Creates an instance of the Insert Cursor to add rows to the Nodes Table
    node_cursor = arcpy.da.InsertCursor(node_fc, node_fields)

    # Creates an instance of the Insert Cursor to add rows to the Edges Table
    edge_cursor = arcpy.da.InsertCursor(edge_fc, edge_fields)

    # Dictionary to store nodes to allow for a look up of coordinates for edge creation
    node_dict = {}

    # List object to store the base node/edge rows.  This is used in case a user wants to calculate
    # any of the centrality scores so the feature class can be edited in one swoop. 
    node_rows = []
    edge_rows = []

    completed_nodes = []

    edges = []

    arcpy.AddMessage("Querying nodes and edges.")

    count = 0
    for r in results:
        count +=1
        source = dict(r['source'])
        target = dict(r['target'])
        airline = r["r.airline"]
        
        if count <= 10:
            arcpy.AddMessage(airline)

        edges.append((source['code'], target['code']))
        node_dict[target['code']] = (target['lon'], target['lat'])
        node_dict[source['code']] = (source['lon'], source['lat'])

        if source["code"] not in completed_nodes:
            source_row = [(float(source['lon']), float(source['lat'])),
                source["name"],
                source["location"],
                source["state"],
                source["country"],
                source["start_date"],
                source["code"],
                source["betweenness"],
                source["closeness"],
                source["in-degree"],
                source["out-degree"],
                source["pagerank"]]

            completed_nodes.append(source['code'])
            node_rows.append(source_row)

        if target['code'] not in completed_nodes:
            target_row = [(float(target['lon']), float(target['lat'])),
                            target["name"],
                            target["location"],
                            target["state"],
                            target["country"],
                            target["start_date"],
                            target["code"],
                            target["betweenness"],
                            target["closeness"],
                            target["in-degree"],
                            target["out-degree"],
                            target["pagerank"]]

            completed_nodes.append(target['code'])

            node_rows.append(target_row)

        # Construct geometry of the edge
        source_point = arcpy.Point(float(node_dict[source['code']][0]), float(node_dict[source['code']][1]))
        target_point = arcpy.Point(float(node_dict[target['code']][0]), float(node_dict[target['code']][1]))
        line = arcpy.Polyline(arcpy.Array([source_point, target_point] ))

        row = [line,source['name'],target['name'], airline]
        
        edge_rows.append(row)

    arcpy.AddMessage("Adding rows to Node Feature Class")
    
    arcpy.AddMessage("Adding nodes.")
    for row in node_rows:
        try:
            node_cursor.insertRow(row)
        except Exception as e:
            arcpy.AddMessage(row)
            arcpy.AddError(e)
            exit()
    
    # Delete the node cursor since it is no longer needed.
    del node_cursor

    arcpy.AddMessage("Adding edges.")

    # Adds items to the Edges feature class
    arcpy.AddMessage("Adding rows to Edge Feature Class")
    for row in edge_rows:
        try:
            edge_cursor.insertRow(row)
        except Exception as e:
            arcpy.AddError("Error on adding edges, exiting.")
            arcpy.AddError(e)
            exit()


    # Delete the edge cursor since it is no longer needed.
    del edge_cursor

if __name__ == "__main__":
    main()