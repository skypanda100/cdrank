<template>
    <div id='radarChart' class='radarChart'>
    </div>
</template>

<script>
    import util from '../libs/util';

    export default {
        name: 'radar',
        props: {
            radarData: {
                type: Array,
                default: []
            }
        },
        data () {
            return {
                radarChart: null
            };
        },
        watch: {
            'radarData': function (data) {
                this.makeChart();
            }
        },
        mounted () {
            this.initChart();
        },
        methods: {
            initChart () {
                if (util.isNull(this.radarChart)) {
                    this.radarChart = this.$echarts.init(document.getElementById('radarChart'), 'light');
                } else {
                    this.radarChart.clear();
                }
            },
            createOption () {
                let option = {
                    legend: {},
                    tooltip: {},
                    radar: {
                        name: {
                            textStyle: {
                                color: '#fff',
                                backgroundColor: '#999',
                                borderRadius: 3,
                                padding: [3, 5]
                            }
                        },
                        indicator: [
                            {
                                name: '天气',
                                max: 15
                            },
                            {
                                name: '公司',
                                max: 15
                            },
                            {
                                name: '空管',
                                max: 15
                            },
                            {
                                name: '军事',
                                max: 15
                            },
                            {
                                name: '其他',
                                max: 15
                            }
                        ]
                    },
                    series: [
                        {
                            type: 'radar',
                            itemStyle: {
                                normal: {
                                    areaStyle: {
                                        type: 'default'
                                    }
                                }},
                            data: this.radarData
                        }
                    ]
                };
                return option;
            },
            makeChart () {
                this.initChart();
                this.radarChart.setOption(this.createOption());
            }
        }
    };
</script>

<style scoped>
    .radarChart {
        height: 100%;
        width: 100%;
        transition: all 0.5s linear;
    }
</style>
