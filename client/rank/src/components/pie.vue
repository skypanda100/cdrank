<template>
    <div id='pieChart' class='pieChart'>
    </div>
</template>

<script>
    import util from '../libs/util';

    export default {
        name: 'pie',
        props: {
            pieData: {
                type: Array,
                default: []
            }
        },
        data () {
            return {
                pieChart: null
            };
        },
        watch: {
            'pieData': function (data) {
                this.makeChart();
            }
        },
        mounted () {
            this.initChart();
        },
        methods: {
            initChart () {
                if (util.isNull(this.pieChart)) {
                    this.pieChart = this.$echarts.init(document.getElementById('pieChart'), 'light');
                    this.pieChart.on('updateAxisPointer', (event) => {
                        let xAxisInfo = event.axesInfo[0];
                        if (xAxisInfo) {
                            let dimension = xAxisInfo.value + 1;
                            this.pieChart.setOption({
                                series: {
                                    id: 'pie',
                                    label: {
                                        formatter: '{b}: {@[' + dimension + ']} ({d}%)'
                                    },
                                    encode: {
                                        value: dimension,
                                        tooltip: dimension
                                    }
                                }
                            });
                        }
                    });
                } else {
                    this.pieChart.clear();
                }
            },
            createOption () {
                let option = {
                    legend: {},
                    tooltip: {
                        trigger: 'axis',
                        showContent: false
                    },
                    dataset: {
                        source: this.pieData
                    },
                    xAxis: {
                        type: 'category'
                    },
                    yAxis: {
                        gridIndex: 0
                    },
                    grid: {
                        top: '20px',
                        left: '50px',
                        width: '60%'
                    },
                    series: [
                        {type: 'line', smooth: true, seriesLayoutBy: 'row', color: '#696969'},
                        {type: 'line', smooth: true, seriesLayoutBy: 'row', color: '#B22222'},
                        {type: 'line', smooth: true, seriesLayoutBy: 'row', color: '#008B8B'},
                        {type: 'line', smooth: true, seriesLayoutBy: 'row', color: '#FFA500'},
                        {type: 'line', smooth: true, seriesLayoutBy: 'row', color: '#7B68EE'},
                        {
                            type: 'pie',
                            id: 'pie',
                            radius: '40%',
                            center: ['80%', '50%'],
                            label: {
                                formatter: '{b}: {@' + this.pieData[0][1] + '} ({d}%)'
                            },
                            encode: {
                                itemName: 'day',
                                value: this.pieData[0][1],
                                tooltip: this.pieData[0][1]
                            },
                            itemStyle: {
                                emphasis: {
                                    shadowBlur: 10,
                                    shadowOffsetX: 0,
                                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                                }
                            },
                            color: [
                                '#696969',
                                '#B22222',
                                '#008B8B',
                                '#FFA500',
                                '#7B68EE'
                            ]
                        }
                    ]
                };
                return option;
            },
            makeChart () {
                this.initChart();
                this.pieChart.setOption(this.createOption());
            }
        }
    };
</script>

<style scoped>
    .pieChart {
        height: 100%;
        width: 100%;
        transition: all 0.5s linear;
    }
</style>
