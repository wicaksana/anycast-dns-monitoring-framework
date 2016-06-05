var width = 531;
var height = 588;
var min_zoom = 0.1;
var max_zoom = 7;

// var color = d3.scale.category20();
var zoom = d3.behavior.zoom()
    .scaleExtent([min_zoom, max_zoom]);

var force = d3.layout.force()
    .charge(-750)
    .linkDistance(30)
    .size([width, height]);

var svg = d3.select("div#graph-main").append("svg")
    .attr("width", width)
    .attr("height", height);

d3.json("/graph", function(error, graph) {
    if (error) throw error;
    // console.log(graph);
    force
        .nodes(graph.nodes)
        .links(graph.links)
        .start();

    var link = svg.selectAll(".link")
        .data(graph.links)
        .enter().append("line")
        .attr("class", "link")
        .style("stroke-width", function(d) {
            return d.prepended * 3 + 1;
        });

    var node = svg.selectAll(".node")
        .data(graph.nodes)
        .enter().append("g")
        .attr("class", "node")
        .on('mouseover', mouseover)
        .on('mouseout', mouseout)
        .call(force.drag);

    node.append('circle')
        // .attr("cx", function(d) { return d.x; })
        // .attr("cy", function(d) { return d.y; })
        .attr('r', 8);

    node.append("text")
      .attr('x', 12)
      .attr('dy', '.35em')
      .style('stroke', 'none')
      .text(function(d) { return d.title; });

    force.on("tick", function() {
        link
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

      node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    });

    var dcx =

    function mouseover() {
        d3.select(this).select('circle').transition()
            .duration(500)
            .attr('r', 12);
    }

    function mouseout() {
        d3.select(this).select('circle').transition()
            .duration(500)
            .attr('r', 8);
    }
});