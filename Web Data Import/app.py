import numpy as np
import os
import re

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
  return render_template("home.html")
    
@app.route("/visualization", methods=["POST"])
def visualization():
  if request.method == 'POST':
    dataset = request.files["dataset"]
    filename = dataset.filename
    dataset.save(os.path.join("uploads", filename))
  
    filepath = f"uploads/{dataset.filename}"

    inputFile = open(filepath)
    file = inputFile.readlines(); inputFile.close()
    dataset = np.zeros((9,))
    for i in file:
      j = re.split("	|	|	|	" , str(i))
      del j[0]
      try:
        j = np.asarray(j[:9], dtype="float64")
        dataset = np.vstack((dataset, j))
      except:
        continue
    dataset = np.delete(dataset, 0, axis=0)

    #%% Elevation Adjustment, and Determine X and Z
    elevations = np.append(dataset[:, 1], [dataset[:, 3], dataset[:, 5], dataset[:, 7]])
    ABMN = np.append(dataset[:, 0], [dataset[:, 2], dataset[:, 4], dataset[:, 6]])

    y = np.zeros((len(ABMN),))
    xyz = np.vstack((ABMN, y, elevations)).T
    xyz = np.unique(xyz, axis=0)

    index = np.argsort(xyz[:, 0])
    xyz = xyz[index]

    xyz[:, 2] = xyz[:, 2] - min(xyz[:, 2])

    #%% Create the Tokens Matrix and Enter the Known Values
    tokens = np.zeros((len(dataset), 11))
    tokens[:, 0] = (dataset[:, 0]/5)+1
    tokens[:, 1] = (dataset[:, 2]/5)+1
    tokens[:, 2] = (dataset[:, 4]/5)+1
    tokens[:, 3] = (dataset[:, 6]/5)+1
    
    tokens[:, 8] = dataset[:, 8]

    tokens[:, 10] = 1
    
    #%% Python List
    file = []

    file.append(str(len(xyz)))
    file.append("# x y z")
    for line in xyz:
      file.append(f"{int(line[0])}  {int(line[1])}  {line[2]}")
    file.append(str(len(dataset)))
    file.append("# a b m n err i k r rhoa u valid")
    for line in tokens:
      file.append(f"{int(line[0])}	{int(line[1])}	{int(line[2])}	{int(line[3])}	{line[4]}	{line[5]}	{line[6]}	{line[7]}	{line[8]}	{line[9]}	{int(line[10])}")
    file.append("0")
    
    output_file = open(f"static/{filename[:len(filename)-4]}.txt", "w")
    for element in file:
      output_file.write(element + "\n")
    output_file.close()
    
    return render_template("visualization.html", filename=f"{filename[:len(filename)-4]}.txt")
    
if __name__ == '__main__':
  app.run(host="0.0.0.0", port=4000, debug=True)
