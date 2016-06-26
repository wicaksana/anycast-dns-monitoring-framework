// var width = 765;
var width = 1024;
var height = 588;
var minZoom = 0.1;
var maxZoom = 7;
var prevRoot = '';
var curRoot = '';

var color = d3.scale.category20();

var force = d3.layout.force()
    .charge(-750)
    .linkDistance(3)
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

/**
 * update main graph
 * @param rootServer
 * @param version
 * @param timestamp
 */
function updateGraph(rootServer, version, timestamp) {
    var url = '/graph/' + rootServer + '/' + version + '/' + timestamp;

    prevRoot = curRoot;
    curRoot = rootServer;

    resetGraph();

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

    $('#chart-title').text('Catchment area: ' + rootServer.toUpperCase() + '-Root server (IPv' + version + ') 01-' + timestamp);
}

/**
 *
 * @param rootServer
 * @param timestamp
 */
function mutualPeers(rootServer, timestamp) {
    var url = '/mutual_peers/' + rootServer + '/' + timestamp;
    
    d3.json(url, function (error, data) {
        if(error) throw error;

        // console.log(data);
        
        d3.select('#result-common-peers').selectAll('code').remove();
        d3.select('#result-common-comp-similar').selectAll('code').remove();
        d3.select('#result-common-comp-inequal').selectAll('code').remove();
        d3.select('#result-common-comp-v4longer').selectAll('code').remove();
        d3.select('#result-common-comp-v4shorter').selectAll('code').remove();

        d3.select('#result-common-peers')
            .selectAll('span')
            .data(data['peers_mutual'])
            .enter()
            .append('code')
            .text(function (d) {
                return d + " ";
            });

        d3.select('#result-common-comp-similar')
            .selectAll('span')
            .data(data['peers_identical'])
            .enter()
            .append('code')
            .text(function (d) {
                return d + " ";
            });

        d3.select('#result-common-comp-inequal')
            .selectAll('span')
            .data(data['peers_diff_path'])
            .enter()
            .append('code')
            .text(function (d) {
                return d + " ";
            });

        d3.select('#result-common-comp-v4longer')
            .selectAll('span')
            .data(data['peers_v4_longer'])
            .enter()
            .append('code')
            .text(function (d) {
                return d + " ";
            });

        d3.select('#result-common-comp-v4shorter')
            .selectAll('span')
            .data(data['peers_v4_shorter'])
            .enter()
            .append('code')
            .text(function (d) {
                return d + " ";
            });

        var chartData = [{
            values: [data['peers_identical'].length, data['peers_diff_path'].length, data['peers_v4_longer'].length, data['peers_v4_shorter'].length],
            labels: ['identical AS path', 'different AS path', 'longer IPv4 AS path', 'shorter IPv4 AS path'],
            type: 'pie'
        }];
        var layout = {height: 500};
        Plotly.newPlot('result-common-bar', chartData, layout);
    });
}

/***********************************************************************************************************************
 * sort of main function :|
 **********************************************************************************************************************/
$(document).ready(function () {
    updateGraph('i', '6', '02-2015');

    //****************************************************
    // Main graph
    //****************************************************
    $('#datepicker')
        .datepicker({
            format: "mm-yyyy",
            startView: "months",
            minViewMode: "months",
            startDate: new Date(2004, 12),
            endDate: new Date(2016, 7)
        });

    // event listener for btn-update
    $('#btn-update')
        .click(function () {
            var rootServer = $('#select-root-servers').val();
            var version = $('#select-ip-version').val();
            var timestamp = $('#select-time').val();
            updateGraph(rootServer, version, timestamp);
        });

    //****************************************************
    // common peers
    //****************************************************
    $('#datepicker-common-peers')
        .datepicker({
            format: "mm-yyyy",
            startView: "months",
            minViewMode: "months",
            startDate: new Date(2004, 12),
            endDate: new Date(2016, 7)
        });
    
    // event listener for btn-common-peers
    $('#btn-common-peers')
        .click(function () {
            var rootServer = $('#select-root-servers-common').val();
            var timestamp = $('#select-time-common-peers').val();
            mutualPeers(rootServer, timestamp);
        });

});