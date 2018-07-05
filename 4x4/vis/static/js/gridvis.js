function gridData(graph) {
    console.log(graph);
    var data = new Array();
    var xpos = 1; //starting xpos and ypos at 1 so the stroke will show when we make the grid below
    var ypos = 1;
    var width = 50;
    var height = 50;
    var size = 4;

    // iterate for rows 
    for (var row = 0; row < size; row++) {
        data.push( new Array() );

        // iterate for cells/columns inside rows
        for (var column = 0; column < size; column++) {
            data[row].push({
                x: xpos,
                y: ypos,
                width: width,
                height: height,
                color: graph[row][column]
            })
            // increment the x position. I.e. move it over by 50 (width variable)
            xpos += width;
        }
        // reset the x position after a row is complete
        xpos = 1;
        // increment the y position for the next row. Move it down 50 (height variable)
        ypos += height; 
    }
    return data;
}




function showGraph(id, iter){
$.get("/getgraph?id="+id, function(graph, header) {
  graph = JSON.parse(graph);
  var gd = gridData(graph); 

  var c10 = d3.scaleOrdinal(d3.schemeCategory10);

  d3.select("#gridsvg"+iter).selectAll("*").remove();
  var grid = d3.select("#gridsvg"+iter);
  
  var row = grid.selectAll(".row")
    .data(gd)
    .enter().append("g")
    .attr("class", "row");

  var column = row.selectAll(".square")
    .data(function(d) { return d; })
    .enter().append("rect")
    .attr("class","square")
    .attr("x", function(d) { return d.x; })
    .attr("y", function(d) { return d.y; })
    .attr("width", function(d) { return d.width; })
    .attr("height", function(d) { return d.height; })
    .style("fill", function(d) { return c10(d.color);})
    .style("stroke",function(d) { return "#ffffff"});
  });
}

