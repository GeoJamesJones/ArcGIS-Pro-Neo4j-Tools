import arcpy
import json
import os
from py2neo import Graph

def main():
    graph_connection = arcpy.GetParameterAsText(0)
    output_workspace = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(output_workspace)

    g = Graph(gc_tuple[0], auth=(gc_tuple[1], gc_tuple[2]))
    arcpy.AddMessage("Successfully connected to Graph!")

    closeness = "CALL algo.closeness('Airport', 'CONNECTION', {write:true, writeProperty:'closeness'})"
    betweenness = "CALL algo.betweenness('Airport','CONNECTION', {direction:'out',write:true, writeProperty:'betweenness'})"
    in_degree = 'CALL algo.degree("Airport", "CONNECTION", {direction: "incoming", writeProperty: "in-degree"})'
    out_degree = 'CALL algo.degree("Airport", "CONNECTION", {direction: "outgoing", writeProperty: "out-degree"})'
    pagerank = "CALL algo.pageRank('Airport', 'CONNECTION',{iterations:20, dampingFactor:0.85, write: true,writeProperty:'pagerank'})"

    # Checks to see if the output workspace is a file geodatabase.  If not, returns error and forces
    # user to use a file geodatabase. 
    if desc.dataType != 'Workspace':
        arcpy.AddError('Please select a file geodatabase to output your files.')
        exit()

    g.run(closeness)
    g.run(betweenness)
    g.run(in_degree)
    g.run(out_degree)
    g.run(pagerank)
    

if __name__ == "__main__":
    pass