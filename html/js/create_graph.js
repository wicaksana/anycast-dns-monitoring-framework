/**
 * Created by arif on 1-4-16.
 */

var r = 960 / 2;

var tree = d3.layout.tree()
        .size([360, r - 60])
        .separation(function (a, b) {
            return (a.parent == b.parent ? 10 : 20) / a.depth;
        });

var diagonal = d3.svg.diagonal.radial()
        .projection(function (d) {
            return [d.y, d.x / 180 * Math.PI];
        });

var vis = d3.select('.graph').append('svg') //change elt to '#astree_ok_1772722'
        .attr('width', r * 2)
        .attr('height', r * 2 - 150)
        .append('g')
        .attr('transform', 'translate(' + r + ',' + r + ')');

function create_as_tree(tree_data, elt, as_tree_type) { //as-tree 'fail' is special
    var nodes = tree.nodes(tree_data);

    vis.selectAll('path.link').remove(); //remove any link first
    var link = vis.selectAll('path.link')
        .data(tree.links(nodes))
        .enter().append('path')
        .attr('class', 'link')
        .attr('d', diagonal);

    link.classed('rootlink_' + as_tree_type, function (p) {
        return p.source.depth == 0; // make them hideable
    });

    vis.selectAll('g.node').remove(); //remove any node first
    var node = vis.selectAll('g.node')
        .data(nodes)
        .enter().append('g')
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

    node.append('circle')
        .attr('r', function (d) {
            return d.depth == 1 ? 6 : 3;
        });

    node.append('text')
        .attr('dx', function (d) {
            return d.x < 180 ? 8 : -8;
        })
        .attr('dy', '.31em')
        .attr('text-anchor', function (d) {
            return d.x < 180 ? 'start' : 'end';
        })
        .attr('transform', function (d) {
            return d.x < 180 ? null : 'rotate(180)';
        })
        .text(function (d) {
            return d.name;
        });

    if (as_tree_type == 'fail') {
        vis.selectAll('.node circle').classed('tr_results_ok', function (p) {
            return (p.tr_results == 'ok' && (p.depth > 0));
        });
        vis.selectAll('.node circle').classed('tr_results_fail', function (p) {
            return (p.tr_results == 'fail' && (p.depth > 0));
        });
        vis.selectAll('.node circle').classed('tr_results_mix', function (p) {
            return (p.tr_results == 'mix' && (p.depth > 0));
        });
    } else {
        vis.selectAll('.node circle').classed('tr_results_ok', function (p) {
            return (p.tr_results == 'ok' && (p.depth > 1));
        });
        vis.selectAll('.node circle').classed('tr_results_fail', function (p) {
            return (p.tr_results == 'fail' && (p.depth > 1));
        });
        vis.selectAll('.node circle').classed('tr_results_mix', function (p) {
            return (p.tr_results == 'mix' && (p.depth > 1));
        });
    }
}

var json_file = [
    '../datasets/output-control-noamster.json',
    '../datasets/output-control-amster.json'
];

var title = [
    'without Amsterdam instance',
    'with Amsterdam instance'
];

var toggle = true;

function myTimer() {
    d3.json(json_file[toggle == true? 0 : 1], function (json) {
        create_as_tree(json, '#astree_ok_1772722');
        d3.select(".title")
            .html(title[toggle == true ? 0 : 1]);
        toggle = !toggle;
    });
}

$(document).ready(function() {
    myTimer();
    var interval = setInterval(myTimer, 3000);
});