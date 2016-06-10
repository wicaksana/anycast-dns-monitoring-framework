var width = 765;
var height = 588;
var minZoom = 0.1;
var maxZoom = 7;
var prevRoot = '';
var curRoot = '';

var color = d3.scale.category20();

var force = d3.layout.force()
    .charge(-750)
    .linkDistance(30)
    .size([width, height]);

var svg = d3.select("div#graph-main").append("svg")
    .attr("id", "svg-main-graph")
    .attr("width", width)
    .attr("height", height)
    .call(d3.behavior.zoom().scaleExtent([minZoom, maxZoom]).on('zoom', zoom));

var g = svg.append('g')
    .attr('id', 'container');

svg.style('cursor', 'move');

/**
 * on mouse over
 */
function mouseover() {
    d3.select(this).select('circle').transition()
        .duration(300)
        .attr('r', 12);
}

/**
 * on mouse out
 */
function mouseout() {
    d3.select(this).select('circle').transition()
        .duration(300)
        .attr('r', function (d) {
            if(d.degree == 0) { return 12; }
            else { return 8; }});
}

/**
 * zoom and panning features
 */
function zoom() {
    g.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
}

/**
 * if previous graph and current graph display different Root Server's catchment area, then clean all contents of <g>
 */
function resetGraph() {
    g.selectAll('*').remove();
}

function updateGraph(rootServer, version, timestamp) {
    var url = '/graph/' + rootServer + '/' + version + '/' + timestamp;

    prevRoot = curRoot;
    curRoot = rootServer;

    console.log('prevRoot:' + prevRoot + ' curRoot: ' + curRoot);
    if(prevRoot != curRoot) {
        resetGraph();
    }

    d3.json(url, function (error, graph) {
        if(error) throw error;

        force
            .nodes(graph.nodes)
            .links(graph.links)
            .on('tick', function () {
                link
                    .attr("x1", function(d) { return d.source.x; })
                    .attr("y1", function(d) { return d.source.y; })
                    .attr("x2", function(d) { return d.target.x; })
                    .attr("y2", function(d) { return d.target.y; });
                node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
            });

        var link = g.selectAll(".link");

        link = link.data(graph.links);
        link.enter()
            .insert("line")
            .attr("class", "link")
            .style("stroke-width", function(d) {
                return d.prepended * 3 + 1;
            });

        link.exit().remove();


        var node = g.selectAll(".node")
            .data(graph.nodes);

        node.enter().append("g")
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
            .text(function(d) { return d.title; })
            .style('font-size', function (d) {
                if(d.degree == 0) { return 14; }
                else { return 12; }
            });

        node.exit().remove();

        force.start();

    });

    $('#chart-title').text('Catchment area: ' + rootServer.toUpperCase() + '-Root server IPv' + version + ' 01-' + timestamp);
}

/***********************************************************************************************************************
 * sort of main function :|
 **********************************************************************************************************************/
$(document).ready(function () {
    updateGraph('i', '6', '02-2015');

    $('#datepicker')
        .datepicker({
            format: "mm-yyyy",
            startView: "months",
            minViewMode: "months",
            startDate: new Date(2004, 12)
            // endDate TBA
        });

    // event listener for btn-update
    $('#btn-update')
        .click(function () {
            var rootServer = $('#select-root-servers').val();
            var version = $('#select-ip-version').val();
            var timestamp = $('#select-time').val();
            updateGraph(rootServer, version, timestamp);
        });
});