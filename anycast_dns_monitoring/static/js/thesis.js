/**
 * Created by arif on 22-6-16.
 */
// var trace1 = {
//   x: ['giraffes', 'orangutans', 'monkeys'],
//   y: [20, 14, 23],
//   name: 'SF Zoo',
//   type: 'bar'
// };
//
// var trace2 = {
//   x: ['giraffes', 'orangutans', 'monkeys'],
//   y: [12, 18, 29],
//   name: 'LA Zoo',
//   type: 'bar'
// };
//
// var data = [trace1, trace2];
// console.log(data);
// var layout = {barmode: 'stack'};

// Plotly.newPlot('chart-03', data, layout);

function updateThesisMainDegree(root) {
    var url = '/stacked-bar/' + root;
    d3.json(url, function (error, data) {
        var plottedData4 = data['ipv4'];
        var plottedData6 = data['ipv6'];
        // console.log(plottedData4);
        var layout4 = {
            barmode: 'stack',
            title: root.toUpperCase() + '-Root Server Peer Degree Distribution (IPv4)',
            yaxis: {
                title: 'Number of peers',
                titlefont: {
                    size: 16,
                    color: 'rgb(107, 107, 107)'
                }
            }
        };

        var layout6 = {
            barmode: 'stack',
            title: root.toUpperCase() + '-Root Server Peer Degree Distribution (IPv6)',
            yaxis: {
                title: 'Number of peers',
                titlefont: {
                    size: 16,
                    color: 'rgb(107, 107, 107)'
                }
            }
        };

        Plotly.newPlot('chart-thesis-main-ipv4', plottedData4, layout4);
        Plotly.newPlot('chart-thesis-main-ipv6', plottedData6, layout6);

        $('#title-thesis-main').text(root.toUpperCase() + '-Root Server - Peer Degree Distribution');
    });
}

function updateThesisMainAvg(root) {
    var url = '/boxplot/' + root;
    d3.json(url, function (error, data) {
        var plottedData4 = data['ipv4'];
        var plottedData6 = data['ipv6'];

        var layout4 = {
            title: root.toUpperCase() + '-Root Server Path Average (IPv4)',
            showlegend: false
        };
        var layout6 = {
            title: root.toUpperCase() + '-Root Server Path Average (IPv6)',
            showlegend: false
        };

        Plotly.newPlot('chart-thesis-main-ipv4', plottedData4, layout4);
        Plotly.newPlot('chart-thesis-main-ipv6', plottedData6, layout6);
    });
}

// default
updateThesisMainDegree('a');


$('#btn-thesis-main')
    .click(function () {
        var root = $('#select-thesis-main-root').val();
        var type = $('#select-thesis-main-type').val();

        if(type == 'peer-degree') {
            updateThesisMainDegree(root);
        } else {
            updateThesisMainAvg(root);
        }
    });

// d3.slider().on("slide", function(evt, value) {
//   d3.select('#chart-04').text(value);
// })