/**
 * Created by arif on 14-7-16.
 */

// animating changes in force diagram http://bl.ocks.org/ericcoopey/6c602d7cb14b25c179a4
// modifying a force layout https://bl.ocks.org/mbostock/1095795

// var width = 960,
//     height = 500;
//
// var color = d3.scale.category10();
//
// var nodes = [],
//     links = [];
//
// var force = d3.layout.force()
//     .nodes(nodes)
//     .links(links)
//     .charge(-400)
//     .linkDistance(120)
//     .size([width, height])
//     .on("tick", tick);
//
// var svg = d3.select("div.chart-stage").append("svg")
//     .attr("width", width)
//     .attr("height", height);
//
// var node = svg.selectAll(".node"),
//     link = svg.selectAll(".link");
//
// // 1. Add three nodes and three links.
// setTimeout(function() {
//   var a = {id: "a"}, b = {id: "b"}, c = {id: "c"};
//   nodes.push(a, b, c);
//   links.push({source: a, target: b}, {source: a, target: c}, {source: b, target: c});
//   start();
// }, 0);
//
// // 2. Remove node B and associated links.
// setTimeout(function() {
//   nodes.splice(1, 1); // remove b
//   links.shift(); // remove a-b
//   links.pop(); // remove b-c
//   start();
// }, 3000);
//
// // Add node B back.
// setTimeout(function() {
//   var a = nodes[0], b = {id: "b"}, c = nodes[1];
//   nodes.push(b);
//   links.push({source: a, target: b}, {source: b, target: c});
//   start();
// }, 6000);
//
// function start() {
//   link = link.data(force.links(), function(d) { return d.source.id + "-" + d.target.id; });
//   link.enter().insert("line", ".node").attr("class", "link");
//   link.exit().remove();
//
//   node = node.data(force.nodes(), function(d) { return d.id;});
//   node.enter().append("circle").attr("class", function(d) { return "node " + d.id; }).attr("r", 8);
//   node.exit().remove();
//
//   force.start();
// }
//
// function tick() {
//   node.attr("cx", function(d) { return d.x; })
//       .attr("cy", function(d) { return d.y; })
//
//   link.attr("x1", function(d) { return d.source.x; })
//       .attr("y1", function(d) { return d.source.y; })
//       .attr("x2", function(d) { return d.target.x; })
//       .attr("y2", function(d) { return d.target.y; });
// }

var graph;

function myGraph() {
    // add and remove elements on the graph object
    this.addNode = function (id) {
        nodes.push({"id": id});
        update();
    };

    this.removeNode = function (id) {
        var i = 0;
        var n = findNode(id);
        while(i < links.length) {
            if((links[i]["source"] == n) || (links[i]["target"] == n)) {
                links.splice(i, 1);
            }
            else i++;
        }
        nodes.splice(findNodeIndex(id), 1);
        update();
    };

    this.removeLink = function (source, target) {
        for(var i = 0; i < links.length; i++) {
            if (links[i].source.id == source && links[i].target.id == target) {
                links.splice(i, 1);
                break;
            }
        }
        update();
    };

    this.removeallLinks = function () {
        links.splice(0, links.length);
        update();
    };

    this.addLink = function (source ,target, value) {
        links.push({"source": findNode(source), "target": findNode(target), "value": value});
        update();
    };

    var findNode = function (id) {
        for (var i in nodes) {
            if (nodes[i]["id"] === id) return nodes[i];
        }
    };

    // set up the D3 visualization in the specified element
    var w = 960;
    var h = 450;

    var color = d3.scale.category10();

    var vis = d3.select("div.chart-stage")
        .append("svg:svg")
        .attr("width", w)
        .attr("height", h)
        .attr("id", "svg")
        .attr("pointer-events", "all")
        .attr("viewBox", "0.0" + w + " " + h)
        .attr("perserveAspectRatio", "xMinYMid")
        .append("svg:g");

    var force = d3.layout.force();

    var nodes = force.nodes(),
        links = force.links();

    var update = function () {
        var link = vis.selectAll("line")
            .data(links, function (d) {
                return d.source.id + "-" + d.target.id;
            });

        link.enter().append("line")
            .attr("id", function (d) {
                return d.source.id + "-" + d.target.id;
            })
            .attr("stroke-width", function (d) {
                return d.value / 10;
            })
            .attr("class", "link");

        link.append("title")
            .text(function (d) {
                return d.value;
            });

        link.exit().remove();

        var node = vis.selectAll("g.node")
            .data(nodes, function (d) {
                return d.id;
            });

        var nodeEnter = node.enter().append("g")
            .attr("class", "node")
            .call(force.drag);

        nodeEnter.append("svg:circle")
            .attr("r", 12)
            .attr("id", function (d) {
                return "Node;" + d.id;
            })
            .attr("class", "nodeStrokeclass")
            .attr("fill", function (d) {
                return color(d.id);
            });

        nodeEnter.append("svg:text")
            .attr("class", "textClass")
            .attr("x", 14)
            .attr("y", ".31em")
            .text(function (d) {
                return d.id;
            });

        node.exit().remove();

        force.on("tick", function () {
            node.attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            });

            link.attr("x1", function (d) {
                return d.source.x;
            })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });
        });

        //restart the force layout
        force
            .gravity(0.01)
            .charge(-80000)
            .friction(0)
            .linkDistance(function (d) {
                return d.value * 10;
            })
            .size([w,h])
            .start();
    };

    // make it all go
    update();
}

function drawGraph() {
    graph = new myGraph("div.chart-stage");

    graph.addNode('Sophia');
    graph.addNode('Daniel');
    graph.addNode('Ryan');
    graph.addNode('Lila');
    graph.addNode('Suzie');
    graph.addNode('Riley');
    graph.addNode('Grace');
    graph.addNode('Dylan');
    graph.addNode('Mason');
    graph.addNode('Emma');
    graph.addNode('Alex');
    graph.addLink('Alex', 'Ryan', '20');
    graph.addLink('Sophia', 'Ryan', '20');
    graph.addLink('Daniel', 'Ryan', '20');
    graph.addLink('Ryan', 'Lila', '30');
    graph.addLink('Lila', 'Suzie', '20');
    graph.addLink('Suzie', 'Riley', '10');
    graph.addLink('Suzie', 'Grace', '30');
    graph.addLink('Grace', 'Dylan', '10');
    graph.addLink('Dylan', 'Mason', '20');
    graph.addLink('Dylan', 'Emma', '20');
    graph.addLink('Emma', 'Mason', '10');
    keepNodesOnTop();

    //callback for changes in the network
    var step = -1;
    function nextval() {
        step++;
        return 2000 + (1500 * step);
    }

    setTimeout(function () {
        graph.addLink('Alex', 'Sophia', '20');
        keepNodesOnTop();
    }, nextval());

    setTimeout(function() {
        graph.addLink('Sophia', 'Daniel', '20');
        keepNodesOnTop();
    }, nextval());

    setTimeout(function() {
        graph.addLink('Daniel', 'Alex', '20');
        keepNodesOnTop();
    }, nextval());

    setTimeout(function() {
        graph.addLink('Suzie', 'Daniel', '30');
        keepNodesOnTop();
    }, nextval());

    setTimeout(function() {
        graph.removeLink('Dylan', 'Mason');
        graph.addLink('Dylan', 'Mason', '8');
        keepNodesOnTop();
    }, nextval());

    setTimeout(function() {
        graph.removeLink('Dylan', 'Emma');
        graph.addLink('Dylan', 'Emma', '8');
        keepNodesOnTop();
    }, nextval());
}

drawGraph();


function keepNodesOnTop() {
    $(".nodeStrokeClass").each(function (index) {
        var gnode = this.parentNode;
        gnode.parentNode.appendChild(gnode);
    });
    function addNodes() {
        d3.selec("svg")
            .remove();
        drawGraph;
    }
}