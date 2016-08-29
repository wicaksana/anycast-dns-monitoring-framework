/**
 * Created by arif on 14-7-16.
 */

var width = 1024;
var height = 560;
var minZoom = 0.1;
var maxZoom = 7;

/**
 * on mouse over
 */
function mouseover() {
    // enlarge the circle
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


d3.selection.prototype.moveToFront = function() {
    return this.each(function(){
        this.parentNode.appendChild(this);
    });
};

/**
 * zoom and panning features
 */
// function zoom() {
//     g.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
// }

/**
 * if previous graph and current graph display different Root Server's catchment area, then clean all contents of <g>
 */
function resetGraph(g) {
    g.selectAll('*').remove();
}

var color = d3.scale.category20();

/**
 * initialize graph
 * @param selector
 * @param version
 * @constructor
 */
function InitializeGraph(selector, version) {
    var id = 'svg-comparison-v' + version;
    this.prevRoot = '';
    this.curRoot = '';

    // this.color = d3.scale.category20();

    this.force = d3.layout.force()
        .charge(-750)
        .linkDistance(3)
        .size([width, height]);

    this.svg = d3.select(selector).append("svg")
        .attr("id", id)
        .attr("width", width)
        .attr("height", height)
        .call(d3.behavior.zoom().scaleExtent([minZoom, maxZoom]).on('zoom', zoom));

    // graph container
    this.g = this.svg.append('g')
        .attr('class', 'container')
        .attr('id', 'container-' + version);

    this.svg.style('cursor', 'move');

    function zoom() {
        // this.g.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
         d3.select('#' + id + ' g.container').attr("transform", "translate(" + d3.event.translate +  ")scale(" + d3.event.scale + ")");
    }

}

/**
 * update main graph
 * @param tree
 * @param rootServer
 * @param version
 * @param timestamp
 */
function updateGraph(tree, rootServer, version, timestamp) {
    var url = '/graph/' + rootServer + '/' + version + '/' + timestamp;

    tree.prevRoot = tree.curRoot;
    tree.curRoot = rootServer;

    resetGraph(tree.g);

    d3.json(url, function (error, graph) {
        if(error) throw error;

        // console.log(graph);
        tree.force
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

        var link = tree.g.selectAll(".link");

        link = link.data(graph.links);
        link.enter()
            .insert("line")
            .attr("class", "link")
            .style("stroke-width", function(d) {
                return d.prepended * 3 + 1;
            });

        link.exit().remove();


        var node = tree.g.selectAll(".node")
            .data(graph.nodes);

        node.enter().append("g")
            .attr("class", "node")
            .on('mouseover', function (d) {
                //enlarge the circle
                d3.select(this).select('circle').transition()
                    .duration(300)
                    .attr('r', 12);
            })
            .on('mouseout', function (d) {
                // normalize the circle
                d3.select(this).select('circle').transition()
                    .duration(300)
                    .attr('r', function (d) {
                        if(d.degree == 0) { return 12; }
                        else { return 8; }});
            })
            .call(tree.force.drag);

        // draw circle, except for Root Server
        node.filter(function (d) {
            return d.degree != 0;
        })
            .append('circle')
            .attr('r', 8)
            .style('fill', function (d) {
                return color(d.degree);
            });

        // mark Root Server with star icon
        node.filter(function (d) {
            return d.degree == 0;
        })
            .append("image")
            .attr("xlink:href", "/static/star.ico")
            .attr("x", -18)
            .attr("y", -18)
            .attr("width", 30)
            .attr("height", 30);


        node.append("text")
            .attr('x', 12)
            .attr('dy', '.35em')
            .style('stroke', 'none')
            .text(function(d) { return d.title; })
            .style('font-size', function (d) {
                if(d.degree == 0) { return 20; }
                else { return 18; }
            });

        node.exit().remove();

        tree.force.start();
    });
}

/**
 * Get mutual peers
 * @param rootServer
 * @param timestamp
 */
function mutualPeers(rootServer, timestamp) {
    var url = '/mutual_peers/' + rootServer + '/' + timestamp;

    d3.json(url, function (error, data) {
        if(error) throw error;

        // console.log(data);

        d3.select('#result-comparison').selectAll('span').remove();

        d3.select('#result-comparison')
            .selectAll('span')
            .data(data['peers_mutual'])
            .enter()
            .append('span')
            .attr('class', 'badge')
            .attr("data-poload", function (d) {
                return '/as_info/json?' + 'timestamp=' + timestamp + "&asn=" + d + '&root=' + rootServer ;
            })
            .attr("data-placement", "top")
            .style('background', function (d) {
                for(var i = 0; i < data['peers_diff_path'].length; i++) {
                    if(data['peers_diff_path'][i] == d) {
                        return '#EF6F6C';
                    }
                }
                for(var i = 0; i < data['peers_identical'].length; i++) {
                    if(data['peers_identical'][i] == d) {
                        return '#668B8B';
                    }
                }
                for(var i = 0; i < data['peers_v4_longer'].length; i++) {
                    if(data['peers_v4_longer'][i] == d) {
                        return '#F79744';
                    }
                }
                for(var i = 0; i < data['peers_v4_shorter'].length; i++) {
                    if(data['peers_v4_shorter'][i] == d) {
                        return '#1ABC9C';
                    }
                }
            })
            .text(function (d) {
                return d;
            })
            .on('mouseover', function (d) {
                // highlight the path and enlarge circles along the path
                // console.log(d);
                $.getJSON('/path/json',
                    {
                        timestamp: timestamp,
                        asn: d,
                        root: rootServer
                    },
                    function (data) {
                        // console.log('AS ' + d.title + ': ' + data.path4);
                        var path4 = data.path4;
                        var path6 = data.path6;

                        // enlarge circle and text along the path
                        // * IPv4
                        var circle4 = d3.select('#container-4').selectAll('.node')
                            .filter(function (e) {
                                return _.contains(path4, parseInt(e.title));  // for nodes in the path...
                            });

                        // make it black
                        circle4
                            .select('circle')
                            .moveToFront()
                            .style('fill', '#000000')
                            .transition()
                            .duration(300)
                            .attr('r', 16);

                        // enlarge the title
                        circle4
                            .select('text')
                            .moveToFront()
                            .style('font-size', 24);
                        
                        // * IPv6
                        var circle6 = d3.select('#container-6').selectAll('.node')
                            .filter(function (e) {
                                return _.contains(path6, parseInt(e.title));  // for nodes in the path...
                            });
                        
                        circle6
                            .select('circle')
                            .style('fill', '#000000')
                            .transition()
                            .duration(300)
                            .attr('r', 16);
                        
                        circle6
                            .select('text')
                            .moveToFront()
                            .style('font-size', 24);
                        
                        // dim circles and texts along the path
                        // IPv4
                        d3.select('#container-4').selectAll('.node')
                            .filter(function (e) {
                                return !_.contains(path4, parseInt(e.title));  // for nodes not in the path...
                            })
                            .select('circle')
                            .style('fill', '#D9DCD9');

                        d3.select('#container-4').selectAll('.node')
                            .filter(function (e) {
                                return !_.contains(path4, parseInt(e.title));  // for nodes not in the path...
                            })
                            .select('text')
                            .style('fill', '#D9DCD9');

                        // IPv6
                        d3.select('#container-6').selectAll('.node')
                            .filter(function (e) {
                                return !_.contains(path6, parseInt(e.title)); // for nodes not in the path..
                            })
                            .select('circle')
                            .style('fill', '#D9DCD9');

                        d3.select('#container-6').selectAll('.node')
                            .filter(function (e) {
                                return !_.contains(path6, parseInt(e.title));  // for nodes not in the path...
                            })
                            .select('text')
                            .style('fill', '#D9DCD9');

                        // Highlight paths
                        // IPv4
                        for(i = 0; i < path4.length - 1; i++) {
                            var source = path4[i];
                            var target = path4[i + 1];
                            
                            // emphasize the intended path
                            d3.select('#container-4').selectAll('.link')
                                .filter(function (e) {
                                    // console.log(e);
                                    return e.source.title == source.toString() && e.target.title == target.toString();
                                })
                                .moveToFront()
                                .classed("emphasized", true);
                            
                            // dim all other paths
                            d3.select('#container-4').selectAll('.link')
                                .filter(function (e) {
                                    // console.log(e);
                                    return e.source.title != source.toString() || e.target.title != target.toString();
                                })
                                .classed("dimmed", true);
                        }

                        // IPv6
                        for(i = 0; i < path6.length - 1; i++) {
                            source = path6[i];
                            target = path6[i + 1];

                            // emphasize the intended path
                            d3.select('#container-6').selectAll('.link')
                                .filter(function (e) {
                                    // console.log(e);
                                    return e.source.title == source.toString() && e.target.title == target.toString();
                                })
                                .classed("emphasized", true);


                            // dim all other paths
                            d3.select('#container-6').selectAll('.link')
                                .filter(function (e) {
                                    // console.log(e);
                                    return e.source.title != source.toString() || e.target.title != target.toString();
                                })
                                .classed("dimmed", true);
                        }
                });
            })
            .on('mouseout', function (d) {
                // normalize the circle
                d3.select('#container-4').selectAll('.node')
                    .select('circle')
                    .style('fill', function (d) {
                        return color(d.degree);
                    })
                    .transition()
                    .duration(300)
                    .attr('r', 12);

                d3.select('#container-4').selectAll('.node')
                    .select('text').transition()
                    .duration(300)
                    .style('font-size', 18);

                d3.select('#container-6').selectAll('.node')
                    .select('circle')
                    .style('fill', function (d) {
                        return color(d.degree);
                    })
                    .transition()
                    .duration(300)
                    .attr('r', 12);

                d3.select('#container-6').selectAll('.node')
                    .select('text').transition()
                    .duration(300)
                    .style('font-size', 18);

                // normalize the text
                d3.select('#container-4').selectAll('.node')
                    .select('text')
                    .style('fill', '#000000');

                d3.select('#container-6').selectAll('.node')
                    .select('text')
                    .style('fill', '#000000');

                // normalize the path
                d3.select('#container-4').selectAll('.link')
                    .classed('emphasized', false)
                    .classed('dimmed', false);

                d3.select('#container-6').selectAll('.link')
                    .classed('emphasized', false)
                    .classed('dimmed', false);
            });

        // display AS information on hover
        $('*[data-poload]')
            .mouseenter(function() {
                var e = $(this);
                // console.log(e);
                // console.log(e.data('poload'));
                e.off('hover');
                $.get(e.data('poload'),function(d) {
                    e.popover({
                        title: d.as_info,
                        content: 'IPv4 path: ' + d.path4 + '<br /> IPv6 path: ' + d.path6 + '<br /> Peering at: ' + d.collector,
                        html: true
                    })
                        .popover('show');
                });
                setTimeout(function () {
                    $(e[0]).popover('hide');
                }, 2000);
            })
            .mouseleave(function() {
                $(this).popover('hide');
            });


    });
}

/**
 * Update the title
 * @param rootServer
 * @param ts
 */
function updateTitle(rootServer, ts) {
    $('#title').text('Mutual peers (IPv4/IPv6) of ' + rootServer.toUpperCase() + '-Root Server: 01-' + ts);
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// "main" function
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
$(document).ready(function () {
    var graphV4 = new InitializeGraph('#graph-comparison-ipv4', 4);
    var graphV6 = new InitializeGraph('#graph-comparison-ipv6', 6);

    $('#datepicker')
        .datepicker({
            format: "mm-yyyy",
            startView: "months",
            minViewMode: "months",
            startDate: new Date(2008, 2),
            endDate: new Date(2016, 6)
        });

    updateGraph(graphV4, 'a', '4', '06-2016');
    updateGraph(graphV6, 'a', '6', '06-2016');
    mutualPeers('a', '06-2016');
    updateTitle('a', '06-2016');

    $('#btn-comparison')
        .click(function () {
            var rootServer = $('#select-root-servers').val();
            var timestamp = $('#select-time').val();

            console.log(rootServer);
            updateGraph(graphV4, rootServer, '4', timestamp);
            updateGraph(graphV6, rootServer, '6', timestamp);
            mutualPeers(rootServer, timestamp);
            updateTitle(rootServer, timestamp);
        });

});