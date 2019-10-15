# ArcGIS-Pro-Neo4j-Tools
 <br>

If you have not already, install github desktop and download the public ArcGIS-Pro-Neo4j-Tools repository.

Neo4j
1. Download and run the executable file (neo4j-desktop-offline-1.2.1-setup.exe)for neo4j desktop <br>
2. After opening Neo4j, scroll to the bottom of the My Project page and add both the "APOC" and "GRAPH ALGORITHMS" plugins. <br>
3.Add a new Graph called "Airports" and make the password "gis12345"
4. Click the Start button to start the Airports graph.

Python Command Prompt
1. In the start menu, search for the ArcGIS folder and open the Python Command Prompt <br>
2. In command prompt, run the "pip install py2neo" command. <br>
3. After that has installed, change your directory to the location of the github repository <br>
    ex. "cd C:\Users\User\Documents\GitHub\ArcGIS-Pro-Neo4j-Tools"
4. Next, run the following command: <br>
    "python import_air_traffic_data.py" <br>
    (this will take serveral minutes to load fully) <br>

ArcGIS Pro
1. In ArcGIS Pro, create a folder connection to the Github repository.
2. Expand this folder and the corrosponding toolbox, and open the "Extract all Nodes and Relationships tool".
3. Set the Output Workspace as any file gdb. Then run the tool. 