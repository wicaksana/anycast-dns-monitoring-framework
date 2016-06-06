var width = 765;
var height = 588;
var min_zoom = 0.1;
var max_zoom = 7;

var color = d3.scale.category20();

var force = d3.layout.force()
    .charge(-750)
    .linkDistance(30)
    .size([width, height]);

var svg = d3.select("div#graph-main").append("svg")
    .attr("width", width)
    .attr("height", height)
    .call(d3.behavior.zoom().scaleExtent([min_zoom, max_zoom]).on('zoom', zoom));

var g = svg.append('g')
    .attr('id', 'container');

svg.style('cursor', 'move');

d3.json("/graph/i/6/02-2015", function(error, graph) {
    if (error) throw error;
    console.log(graph);
    force
        .nodes(graph.nodes)
        .links(graph.links)
        .start();

    var link = g.selectAll(".link")
        .data(graph.links)
        .enter().append("line")
        .attr("class", "link")
        .style("stroke-width", function(d) {
            return d.prepended * 3 + 1;
        });

    var node = g.selectAll(".node")
        .data(graph.nodes)
        .enter().append("g")
        .attr("class", "node")
        .on('mouseover', mouseover)
        .on('mouseout', mouseout)
        .call(force.drag);

    node.append('circle')
        .attr('r', function (d) {
            if(d.degree == 0) { return 12; }
            else { return 8; }
        })
        .style('fill', function (d) {
            return color(d.degree);
        });

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


    function mouseover() {
        d3.select(this).select('circle').transition()
            .duration(300)
            .attr('r', 12);
    }

    function mouseout() {
        d3.select(this).select('circle').transition()
            .duration(300)
            .attr('r', function (d) {
            if(d.degree == 0) { return 12; }
            else { return 8; }
        });
    }
});

function zoom() {
    g.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
}

function getData() {
    // get data
}

$(document).ready(function () {
    var d = new Date();
    var selectedDate = (d.getMonth() + 1).toString() + '-' + d.getFullYear();

    $('#datepicker')
        .datepicker({
            format: "mm-yyyy",
            startView: "months",
            minViewMode: "months",
            startDate: new Date(2004, 12)
            // endDate TBA
        })
        .on('changeDate', function (d) {
            selectedDate = $('#select-time').val();
        });

    // event listener for btn-update
    $('#btn-update')
        .click(function () {
            getData();
        });

});