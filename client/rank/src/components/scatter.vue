<template>
    <div id='scatterChart' class='scatterChart'>
    </div>
</template>

<script>
    import util from '../libs/util';

    export default {
        name: 'scatter',
        props: {
            scatterData: {
                type: Array,
                default: []
            }
        },
        data () {
            return {
                scatterChart: null,
                xAxisData: [],
                yAxisData: [],
                seriesData1: [],
                seriesData2: []
            };
        },
        watch: {
            'scatterData': function (data) {
                this.makeChart();
            }
        },
        mounted () {
            this.initChart();
        },
        methods: {
            initChart () {
                if (util.isNull(this.scatterChart)) {
                    this.scatterChart = this.$echarts.init(document.getElementById('scatterChart'), 'light');
                } else {
                    this.scatterChart.clear();
                }

                // 找出最高排名和最低排名
                let maxRank = -1;
                let minRank = 9999;
                if (this.scatterData.length > 0) {
                    this.scatterData.map(rank => {
                        let ranking = rank[1];
                        if (ranking > maxRank) {
                            maxRank = ranking;
                        }
                        if (ranking < minRank) {
                            minRank = ranking;
                        }
                    });
                } else {
                    minRank = 1;
                    maxRank = 30;
                }

                if (minRank > 1) {
                    minRank -= 1;
                }
                maxRank += 1;

                // 顺便重新校正
                let tmp = [];
                this.scatterData.map(rank => {
                    tmp.push([rank[0] - 1, rank[1] - minRank]);
                });
                this.seriesData2 = tmp;

                // x轴
                this.xAxisData = [];
                for (let i = 1; i <= 31; i++) {
                    this.xAxisData.push(i);
                }

                // y轴
                this.yAxisData = [];
                for (let i = minRank; i <= maxRank; i++) {
                    this.yAxisData.push(i);
                }
                console.log(minRank + ' - ' + maxRank);

                // 色块
                tmp = [];
                for (let i = 0; i < this.yAxisData.length; i++) {
                    let rank = this.yAxisData[i];
                    for (let j = 0; j < this.xAxisData.length; j++) {
                        let day = this.xAxisData[j];
                        if (rank <= 3) {
                            tmp.push([j, i, 0]);
                        } else if (rank <= 6) {
                            if (day <= 3) {
                                tmp.push([j, i, 2]);
                            } else if (day <= 18) {
                                tmp.push([j, i, 1]);
                            } else {
                                tmp.push([j, i, 0]);
                            }
                        } else if (rank <= 9) {
                            if (day <= 9) {
                                tmp.push([j, i, 2]);
                            } else if (day <= 21) {
                                tmp.push([j, i, 1]);
                            } else {
                                tmp.push([j, i, 0]);
                            }
                        } else if (rank <= 12) {
                            if (day <= 12) {
                                tmp.push([j, i, 2]);
                            } else if (day <= 24) {
                                tmp.push([j, i, 1]);
                            } else {
                                tmp.push([j, i, 0]);
                            }
                        } else if (rank <= 15) {
                            if (day <= 15) {
                                tmp.push([j, i, 2]);
                            } else if (day <= 27) {
                                tmp.push([j, i, 1]);
                            } else {
                                tmp.push([j, i, 0]);
                            }
                        } else if (rank <= 18) {
                            if (day <= 18) {
                                tmp.push([j, i, 2]);
                            } else {
                                tmp.push([j, i, 1]);
                            }
                        } else if (rank <= 21) {
                            if (day <= 3) {
                                tmp.push([j, i, 3]);
                            } else if (day <= 21) {
                                tmp.push([j, i, 2]);
                            } else {
                                tmp.push([j, i, 1]);
                            }
                        } else if (rank <= 24) {
                            if (day <= 6) {
                                tmp.push([j, i, 3]);
                            } else if (day <= 24) {
                                tmp.push([j, i, 2]);
                            } else {
                                tmp.push([j, i, 1]);
                            }
                        } else if (rank <= 27) {
                            if (day <= 9) {
                                tmp.push([j, i, 3]);
                            } else if (day <= 27) {
                                tmp.push([j, i, 2]);
                            } else {
                                tmp.push([j, i, 1]);
                            }
                        } else if (rank <= 30) {
                            if (day <= 18) {
                                tmp.push([j, i, 3]);
                            } else {
                                tmp.push([j, i, 2]);
                            }
                        } else {
                            tmp.push([j, i, 4]);
                        }
                    }
                }
                this.seriesData1 = tmp;
            },
            createOption () {
                let option = {
                    // title: {
                    //     left: 'center',
                    //     text: title
                    // },
                    tooltip: {
                        trigger: 'none',
                        axisPointer: {
                            type: 'cross',
                            crossStyle: {
                                color: '#555'
                            }
                        }
                    },
                    animation: true,
                    grid: {
                        top: '20px',
                        left: '50px'
                    },
                    xAxis: {
                        type: 'category',
                        data: this.xAxisData,
                        splitArea: {
                            show: false
                        }
                    },
                    yAxis: {
                        type: 'category',
                        data: this.yAxisData,
                        splitArea: {
                            show: false
                        }
                    },
                    visualMap: {
                        min: 0,
                        max: 4,
                        calculable: true,
                        show: false,
                        orient: 'horizontal',
                        left: 'center',
                        inRange: {
                            color: ['rgba(178,34,34,1.0)', 'rgba(255,140,0,1.0)', 'rgba(255,215,0,1.0)', 'rgba(72,209,204,1.0)', 'rgba(60,179,113,1.0)']
                        }
                    },
                    series: [{
                        name: 'Punch Card',
                        type: 'heatmap',
                        data: this.seriesData1,
                        label: {
                            normal: {
                                show: false
                            }
                        },
                        itemStyle: {
                            borderWidth: 1,
                            borderColor: '#eee'
                        },
                        silent: true
                    }, {
                        data: this.seriesData2,
                        type: 'line',
                        itemStyle: {
                            borderWidth: 0
                        },
                        lineStyle: {
                            color: '#555',
                            width: 3
                        },
                        smooth: true
                    }]
                };
                return option;
            },
            makeChart () {
                this.initChart();
                this.scatterChart.setOption(this.createOption());
            }
        }
    };
</script>

<style scoped>
    .scatterChart {
        height: 100%;
        /*width: 100%;*/
        transition: all 0.5s linear;
    }
</style>
