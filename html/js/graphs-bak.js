/**
 * Created by arif on 1-4-16.
 *
 * References:
 *  - https://github.com/darkfiberiru/anycast-1     (base of this project)
 *  - http://bl.ocks.org/syntagmatic/4092944        (radial tree with transition)
 *  - http://bl.ocks.org/robschmuecker/7880033      (tree sort)
 *  - http://bl.ocks.org/d3noob/a22c42db65eb00d4e369    (tooltip)
 */


// move the selection to front or something. I don't really have any idea why I should do this
d3.selection.prototype.moveToFront = function() {
    return this.each(function() {
        this.parentNode.appendChild(this);
    });
};


/**
 * Initialize SVG for visualization
 * @param: diameter
 * @param: padding
 * @param: selector - CSS selector
 */
function Initialize_svg(diameter, padding, selector) {
    // radius of the graph
    this.diameter = diameter;
    this.padding = padding;

    this.tree = d3.layout.tree()
        .size([360, diameter - 2 * padding])
        .separation(function(a, b) {
            // return (a.parent == b.parent ? 1 : 2) / a.depth;
            if (a.parent == b.parent) {
                if (a.depth == 1) {
                    return 2 / a.depth;
                } else {
                    return 1 / a.depth;
                }
            }
            return 2 / a.depth;
        });

    this.diagonal = d3.svg.diagonal.radial()
        .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

    this.svg = d3.select(selector).append("svg")
        // .attr("width", diameter + padding * 2)
        .attr("width", '100%')
        // .attr("height", diameter + padding * 2);
        .attr("height", '100%');
        // .attr("viewBox", "0 0 50 20");

    // get div height and width
    var translate_x = d3.select(this.svg).style('width');
    console.log('translate_x: ' + translate_x);

    var translate_y = d3.select(this.svg).style('height');
    console.log('translate_y: ' + translate_y);
    // graph container
    this.container = this.svg.append("g")
        .attr("class", "container")
        .attr("transform", "translate(" + (diameter + padding * 2) / 2 + "," + (diameter + padding * 2) / 2 + ")"); // put the graph to center
        // .attr("transform", "translate(" + translate_x + "," + translate_y + ")"); // put the graph to center

    // links group
    this.link_group = this.container.append("g");

    // tooltip
    this.tip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
}


/**
 * create the radial tree. Similar to the one I developed before
 * @param tree
 * @param json_data
 */
function tree_map(json_data, tree) {
    //-----------------------------------------------------------------------------------------------------------------
    // creating paths
    //-----------------------------------------------------------------------------------------------------------------
    // clean the JSON data first. Remove the original root node, and assign node '47065' as the root instead
    var root = json_data.children[0];

    var nodes = tree.tree.nodes(root),
        links = tree.tree.links(nodes);

    // makes root nodes closer to the center
    nodes.forEach(function (d) {
        if(d.depth == 1)
            d.y = 0.5 * d.y;
    });

    // bind data to the paths
    var link = tree.link_group.selectAll(".link")
        .data(links);

    link
        .transition() //transition for each datasets refreshment
        .duration(600) //duration of link transition
        .attr("d", tree.diagonal);

    // if the quantity of new data is larger than the old one, the surplus data ends up here
    link
        .enter().append("path")
        .attr("class", "link")
        .attr("d", tree.diagonal)
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

    // hide links directly connected to center node
    // d3.selectAll('path.link')
    //     .filter(function (d) {
    //         return d.source.depth == 0 && d.target.depth == 1;
    //     })
    //     .classed("path-to-center", true);

    //-----------------------------------------------------------------------------------------------------------------
    // creating nodes
    //-----------------------------------------------------------------------------------------------------------------
    var counter = 0;
    var node = tree.container.selectAll(".node")
        .moveToFront()
        .data(nodes, function (d, i) {
            counter++;
            if(d.parent) {
                return d.name + (d.parent.name == d.name ? '-' + counter: '-' + d.parent.name);
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
        .on("mouseover", function (d) {
            tree.tip.transition()
                .duration(200)
                .style("opacity", .9);
            tree.tip.html('Node ID: ' + d.nodeid + '<br />' + 'Name: ' + d.name)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
        })
        .on("mouseout", function (d) {
            tree.tip.transition()
                .duration(400)
                .style("opacity", 0);
        })
        .style("opacity", 0)
        .transition()
        .duration(300)
        .style("opacity", 1);

    g.append("text")
        .attr("dx", function(d) { return d.x < 180 ? 1 : -1; })
        .attr("dy", ".31em")
        .attr("font-weight", "bold")
        .attr("fill", "black")
        .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
        .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
        .attr("class", 'small')
        .text(function(d) { return d.name; })
        .style("opacity", 0)
        .transition()
        .duration(1000)
        .style("opacity", 1);

    //-----------------------------------------------------------------------------------------------------------------
    // traversed path animation
    //-----------------------------------------------------------------------------------------------------------------
    node
        .on('mouseover', function (d, i) {
            // manipulate the circle
            d3.select(this).select("circle")
                .classed("hover", true)
                .attr("r", 6);

            // show the path
            var ancestors = [];
            var parent = d;
            while(parent.parent.depth > 0) {
                ancestors.push(parent);
                parent = parent.parent;
            }

            // enlarge ancestors
            tree.container.selectAll('g.node')
                .filter(function (d, i) {
                    return _.any(ancestors, function (p) {
                        return p == d && d.depth > 1;
                    });
                })
                .select('circle')
                .classed("hover", true)
                .attr("r", 6);

            // get the matched links
            tree.link_group.selectAll('path.link')
                .filter(function (d, i) {
                    return _.any(ancestors, function (p) {
                        return p == d.target;
                    });
                })
                .classed("selected", true)
                .moveToFront();
        })
        .on('mouseout', function (d, i) {
            d3.selectAll("circle")
                .classed("hover", false)
                .attr('r', function (d) {
                    return d.depth == 1 ? 6 : 3;
                });
            tree.link_group.selectAll('path.link')
                .classed('selected', false);
        });
}

// d3.select(self.frameElement).style("height", diameter + "px");

/**
 * switch JSON data betwen output-control-noamster.json and output-control-amster.json
 */
function data_switch(tree) {
    var selected_plane = document.getElementById("select-plane");
    var selected_option = selected_plane.options[selected_plane.selectedIndex].value;
    var selected_json_file;
    if (selected_option == 'control') {
        selected_json_file = json_file[0];
    } else {
        selected_json_file = json_file[1];
    }

    d3.json(selected_json_file[toggle == true? 0 : 1], function (json_data) {
        tree_map(json_data, tree);
        d3.select("#title")
            .html(title[toggle == true ? 0 : 1]);
        toggle = !toggle;
    });
}

//-----------------------------------------------------------------------------------------------------------------
// temporary: use control-plane JSON data (with & without amsterdam instance) to demonstrate the visualization
//            capability of noticing path changes
//-----------------------------------------------------------------------------------------------------------------
var json_file = [[
    '../datasets/output-control-noamster.json',
    '../datasets/output-control-amster.json'
], [
    '../datasets/output-data-noamster.json',
    '../datasets/output-data-amster.json'
]];


// Graph title, notifying the data used (with/without Amsterdam instance)
var title = [
    'without Amsterdam instance',
    'with Amsterdam instance'
];

// to switch between JSON data above
var toggle = true;


$(document).ready(function() {
    var tree_main = new Initialize_svg(960, 120, "div#graph-home.graph");
    data_switch(tree_main);

    // event listener on button 'switch'
    $('button#btn-switch.btn.btn-primary.pull-left')
        .click(function () {
            data_switch(tree_main);
        });

    // read http://eonasdan.github.io/bootstrap-datetimepicker/
    $('#compare-datepicker-1')
        .datetimepicker({
            defaultDate: moment()  // current date-time
        })
        .on('dp.hide', function (e) {
            console.log(e.date);
        });

    $('#compare-datepicker-2')
        .datetimepicker({
            defaultDate: moment()  // current date-time
        })
        .on('dp.hide', function (e) {
            console.log('date#2 changes to: ' + e.date);
        });

    var tree_compare_before = new Initialize_svg(960, 120, 'div#graph-compare-1.graph.col-md-6');
    d3.json(json_file[0][0], function (json_data) {
        tree_map(json_data, tree_compare_before);
    });

    var tree_compare_after = new Initialize_svg(960, 120, 'div#graph-compare-2.graph.col-md-6');
    d3.json(json_file[0][1], function (json_data) {
        tree_map(json_data, tree_compare_after);
    });
});