/**
 * Created by arif on 1-4-16.
 *
 * References:
 *  - https://github.com/darkfiberiru/anycast-1     (base of this project)
 *  - http://bl.ocks.org/syntagmatic/4092944        (radial tree with transition)
 *  - http://bl.ocks.org/robschmuecker/7880033      (tree sort)
 */



// radius of the graph
var diameter = 960;
var padding = 120;

var tree = d3.layout.tree()
    .size([360, diameter - padding])
    .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

var diagonal = d3.svg.diagonal.radial()
    .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

var svg = d3.select("body").append("svg")
    .attr("width", diameter + padding * 2)
    .attr("height", diameter)
    .append("g")
    .attr("transform", "translate(" + (diameter + padding * 2) / 2 + "," + diameter / 2 + ")"); // put the graph to center

// move the selection to front or something. I don't really have the idea
d3.selection.prototype.moveToFront = function() {
    return this.each(function() {
        this.parentNode.appendChild(this);
    });
};

/**
 * create the radial tree. Similar to the one I developed before
 * @param json_data
 */
function tree_map(json_data) {
    // clean the JSON data first. Remove the original root node, and assign node '47065' as the root instead
    var root = json_data.children[0];
    
    var nodes = tree.nodes(root),
        links = tree.links(nodes);

    //-----------------------------------------------------------------------------------------------------------------
    // creating paths
    //-----------------------------------------------------------------------------------------------------------------
    // bind data to the paths
    var link = svg.selectAll(".link")
        .data(links);

    link
        .transition() //transition for each datasets refreshment
        .duration(600) //duration of link transition
        .attr("d", diagonal);

    // if the quantity of new data is larger than the old one, the surplus data ends up here
    link
        .enter().append("path")
        .attr("class", "link")
        .attr("d", diagonal)
        .style("opacity", 0)
        .transition()
        .duration(300) //duration to display the datasets
        .style("opacity", 1);

    // remove excessive elements ([new_data] < [old_data])
    link.exit()
        .transition()
        .duration(400)
        .style("opacity", 0)
        .remove(); //remove items

    //-----------------------------------------------------------------------------------------------------------------
    // creating nodes
    //-----------------------------------------------------------------------------------------------------------------
    var node = svg.selectAll(".node")
        .moveToFront()
        // .data(nodes, function(d) { return d.name + "-" + (d.parent ? d.parent.name : "root");});
        .data(nodes, function (d, i) {
            i++;
            if(d.parent) {
                return d.name + (d.parent.name == d.name ? '-' + i: '');
            }
            return d.name;
        });

    node.exit()
        .transition()
        .duration(400)
        .style("opacity", 0)
        .remove();

    node
        .transition()
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

    var g = node
        .enter().append("g")
        .attr("class", function (d) {
            if (d.depth == 0) {
                return "node centernode";
            }
            if (d.depth == 1) {
                return 'node rootnode';
            }
            return 'node';
        })
        .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; });

    g.append("circle")
        .attr("r", function (d) {
            return d.depth == 1 ? 6 : 3;
        })
        .style("opacity", 0)
        .transition()
        .duration(300)
        .style("opacity", 1);

    g.append("text")
        .attr("dx", function(d) { return d.x < 180 ? 8 : -8; })
        .attr("dy", ".31em")
        .attr("font-weight", "bold")
        .attr("fill", "black")
        .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
        .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
        .text(function(d) { return d.name; })
        .style("opacity", 0)
        .transition()
        .duration(1000)
        .style("opacity", 1);

}

d3.select(self.frameElement).style("height", diameter + "px");


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
function data_switch() {
    d3.json(json_file[toggle == true? 0 : 1], function (json_data) {
        tree_map(json_data);
        d3.select("#title")
            .html(title[toggle == true ? 0 : 1]);
        toggle = !toggle;
    });
}

$(document).ready(function() {
    data_switch();
    setInterval(data_switch, 4000); //switch data every 4 seconds
});