/**
 * Created by arif on 1-4-16.
 */

// radius of the graph
var r = 960 / 2;

// initialize the tree
var tree = d3.layout.tree()
        .size([360, r - 60])
        .separation(function (a, b) {
            return (a.parent == b.parent ? 10 : 20) / a.depth;
        });

// define the diagonal
var diagonal = d3.svg.diagonal.radial()
        .projection(function (d) {
            return [d.y, d.x / 180 * Math.PI];
        });

// define the SVG of the graph
var vis = d3.select('.graph').append('svg') //change elt to '#astree_ok_1772722'
        .attr('width', r * 2)
        .attr('height', r * 2 - 150)
        .append('g')
        .attr('transform', 'translate(' + r + ',' + r + ')');

// required
d3.selection.prototype.moveToFront = function() {
        return this.each(function() {
            this.parentNode.appendChild(this);
        });
    };

/**
 * create radial AS tree using JSON data from traceroute
 * @param tree_data JSON data
 */
function create_as_tree(tree_data) { //as-tree 'fail' is special
    var nodes = tree.nodes(tree_data);
    var links = tree.links(nodes);
    var as_tree_type = undefined;

    /******************************
     * create links
     ******************************/
    var link = vis.selectAll('path.link')
        .data(links);

    link.transition()
        .duration(600)
        .attr("d", diagonal);

    link.enter()
        .append('path')
        .attr('class', 'link')
        .attr('d', diagonal)
        .style("opacity",0)
        .transition()
        .duration(300)
        .style("opacity", 1);

    link.exit()
        .transition()
        .duration(400)
        .remove();

    link.classed('rootlink_' + as_tree_type, function (p) {
        return p.source.depth == 0; // make them hideable
    });

    /******************************
     * create nodes
     ******************************/
    var node = vis.selectAll('g.node')
        .moveToFront()
        .data(nodes);


    node.exit()
        .transition()
        .duration(400)
        .style("opacity", 0)
        .remove();

    node.transition()
        .duration(800)
        .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; });

    node.selectAll("text")
        .transition()
        .duration(800)
        .attr("font-weight", null)
        .attr("fill", "#555")
        .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
        .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
        .text(function(d) { return d.name; });

    var g = node.enter()
        .append('g')
        .attr('class', function (d) {
            if (d.depth == 0) {
                return "node centernode";
            }
            if (as_tree_type != 'fail' && d.depth == 1) {
                return 'node rootnode';
            }
            return 'node';
        }) //leave out any attribute related to mouse activity for simplicity
        .attr('transform', function (d) {
            return 'rotate(' + (d.x - 90) + ')translate(' + d.y + ')';
        });

    g.append('circle')
        .attr('r', function (d) {
            return d.depth == 1 ? 6 : 3;
        })
        .style("opacity" , 0)
        .transition()
        .duration(300)
        .style("opacity" , 1);

    g.append('text')
        .attr('dx', function (d) {
            return d.x < 180 ? 8 : -8;
        })
        .attr('dy', '.31em')
        .attr('font-weight' , 'bold')
        .attr('fill' , 'black')
        .attr('text-anchor', function (d) {
            return d.x < 180 ? 'start' : 'end';
        })
        .attr('transform', function (d) {
            return d.x < 180 ? null : 'rotate(180)';
        })
        .text(function (d) {
            return d.name;
        })
        .style('opacity' , 0)
        .transition()
        .duration(300)
        .style('opacity' , 1);

}

// temporary: use control-plane JSON data (with & without amsterdam instance) to demonstrate the visualization
//            capability of noticing path changes
var json_file = [
    '../datasets/output-control-noamster.json',
    '../datasets/output-control-amster.json'
];

// Graph title, notifying the data used (with/without Amsterdam instance)
var title = [
    'without Amsterdam instance',
    'with Amsterdam instance'
];

// to switch between JSON data above
var toggle = true;

/**
 * switch JSON data betwen output-control-noamster.json and output-control-amster.json
 */
function dataSwitch() {
    d3.json(json_file[toggle == true? 0 : 1], function (json) {
        create_as_tree(json, '.graph');
        d3.select("#title")
            .html(title[toggle == true ? 0 : 1]);
        toggle = !toggle;
    });
}

$(document).ready(function() {
    dataSwitch();
    var interval = setInterval(dataSwitch, 3000); //switch data every 3 seconds
});