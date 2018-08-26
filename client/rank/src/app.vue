<template>
    <div id='main' class='main'>
        <Row>
            <i-col span="8">
                <img width="210px" height="70px"  align="left" src="./images/logo1.jpg">
            </i-col>
            <i-col span="8">
                <h1 style="line-height:70px;text-align: center">
                    成都航空运行控制中心航班预警排名系统
                </h1>
            </i-col>
            <i-col span="8">
                <img width="210px" height="70px" align="right" src="./images/logo2.jpg">
            </i-col>
        </Row>
        <Split v-model='hSplit' class="split">
            <div slot='left' class='list'>
                <Row>
                    <i-col span='3'>
                        <Select
                                v-model='org'
                                placeholder='机构'
                                filterable>
                            <Option v-for='(item, index) in orgs' :value='item' :key='index'>{{ item }}</Option>
                        </Select>
                    </i-col>
                    <i-col span='1'>
                        &nbsp;
                    </i-col>
                    <i-col span='4'>
                        <Select
                                v-model='flight'
                                clearable
                                placeholder='航班号'
                                filterable>
                            <Option v-for='(item, index) in flights' :value='item' :key='index'>{{ item }}</Option>
                        </Select>
                    </i-col>
                    <i-col span='1'>
                        &nbsp;
                    </i-col>
                    <i-col span='4'>
                        <Select
                                v-model='orgAirport'
                                clearable
                                placeholder='起飞机场'
                                filterable>
                            <Option v-for='(item, index) in orgAirports' :value='item' :key='index'>{{ item }}</Option>
                        </Select>
                    </i-col>
                    <i-col span='1'>
                        &nbsp;
                    </i-col>
                    <i-col span='4'>
                        <Select
                                v-model='dstAirport'
                                clearable
                                placeholder='降落机场'
                                filterable>
                            <Option v-for='(item, index) in dstAirports' :value='item' :key='index'>{{ item }}</Option>
                        </Select>
                    </i-col>
                    <i-col span='1'>
                        &nbsp;
                    </i-col>
                    <i-col span='4'>
                        <Button
                                type='primary'
                                long
                                @click='handleSearch'>
                            查询
                        </Button>
                    </i-col>
                </Row>
                <br>
                <Table
                        :columns='rankColumns'
                        :data='rankRows'
                        size='small'
                        height="750"
                        :loading="loading"
                        @on-row-dblclick="handleClick"
                        ref='table'>
                </Table>
            </div>
            <div slot='right' id='chart' class='chart'>
            </div>
        </Split>
    </div>
</template>

<script>
    import {fetchEast, fetchAviation} from './api/rank';
    import util from './libs/util';

    export default {
        data () {
            return {
                hSplit: 0.3,
                eastData: [],
                aviationData: [],
                orgs: ['华东', '总局'],
                org: '华东',
                flights: [],
                flight: '',
                orgAirports: [],
                orgAirport: '',
                dstAirports: [],
                dstAirport: '',
                loading: false,
                rankColumns: [
                    {
                        type: 'index',
                        width: 50,
                        align: 'center'
                    },
                    {
                        'title': '航班号',
                        'key': 'flight',
                        'width': 110,
                        'sortable': true
                    },
                    {
                        'title': '起飞机场',
                        'key': 'orgAirport',
                        'width': 110,
                        'sortable': true
                    },
                    {
                        'title': '降落机场',
                        'key': 'dstAirport',
                        'width': 110,
                        'sortable': true
                    },
                    {
                        'title': '最新排名',
                        'key': 'rank',
                        'width': 110,
                        'sortable': true
                    }
                ],
                rankRows: [],
                rankDatas: [],
                chart: null,
                xAxisData: [],
                yAxisData: [],
                seriesData1: [],
                seriesData2: []
            };
        },
        mounted () {
            this.initChart();
            fetchEast().then(response => {
                this.eastData = response.data;
                this.resetInputFields();
                this.handleSearch();
            });
        },
        beforeDestroy () {
        },
        watch: {
            'org': function (data) {
                if (data === '华东') {
                    fetchEast().then(response => {
                        this.eastData = response.data;
                        this.resetInputFields();
                    });
                } else {
                    fetchAviation().then(response => {
                        this.aviationData = response.data;
                        this.resetInputFields();
                    });
                }
            }
        },
        methods: {
            initChart () {
                if (util.isNull(this.chart)) {
                    this.chart = this.$echarts.init(document.getElementById('chart'), 'light');
                } else {
                    this.chart.clear();
                }

                // 找出最高排名和最低排名
                let maxRank = -1;
                let minRank = 9999;
                if (this.seriesData2.length > 0) {
                    this.seriesData2.map(rank => {
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
                    maxRank = 60;
                }

                if (minRank > 1) {
                    minRank -= 1;
                }
                maxRank += 1;

                // 顺便重新校正
                let tmp = [];
                this.seriesData2.map(rank => {
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
            createOption (title) {
                let option = {
                    title: {
                        left: 'center',
                        text: title
                    },
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
                        containLabel: true
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
            makeChart (title) {
                this.initChart();
                this.chart.setOption(this.createOption(title));
            },
            handleSearch () {
                this.loading = true;
                let tmpRankRows = [];
                let tmpRankDatas = [];
                let jsonData = null;
                if (this.org === '华东') {
                    jsonData = this.eastData;
                } else {
                    jsonData = this.aviationData;
                }

                setTimeout(() => {
                    for (let dateKey in jsonData) {
                        let dateValue = jsonData[dateKey];
                        dateValue.map(rank => {
                            // 航班号
                            let flight = rank.fnum;
                            // 起飞机场
                            let orgAirport = rank.forg;
                            // 降落机场
                            let dstAirport = rank.fdst;
                            // 排名列表
                            let canPush = false;
                            if (util.isNull(this.flight) ||
                                this.flight === '' ||
                                this.flight === flight) {
                                if (util.isNull(this.orgAirport) ||
                                    this.orgAirport === '' ||
                                    this.orgAirport === orgAirport) {
                                    if (util.isNull(this.dstAirport) ||
                                        this.dstAirport === '' ||
                                        this.dstAirport === dstAirport) {
                                        canPush = true;
                                    }
                                }
                            }
                            if (canPush) {
                                tmpRankDatas.push({
                                    date: dateKey,
                                    flight: flight,
                                    orgAirport: orgAirport,
                                    dstAirport: dstAirport,
                                    rank: rank.ranking
                                });
                                canPush = true;
                                for (let rankRow of tmpRankRows) {
                                    if (rankRow.flight === flight &&
                                        rankRow.orgAirport === orgAirport &&
                                        rankRow.dstAirport === dstAirport) {
                                        if (dateKey > rankRow.date) {
                                            rankRow.rank = ('00000' + rank.ranking).slice(-3);
                                        }
                                        canPush = false;
                                    }
                                }
                                if (canPush) {
                                    tmpRankRows.push({
                                        date: dateKey,
                                        flight: flight,
                                        orgAirport: orgAirport,
                                        dstAirport: dstAirport,
                                        rank: ('00000' + rank.ranking).slice(-3)
                                    });
                                }
                            }
                        });
                    }
                    this.rankRows = tmpRankRows;
                    this.rankDatas = tmpRankDatas;
                    this.loading = false;
                    this.seriesData2 = [];
                    this.makeChart('');
                }, 250);
            },
            handleClick (data, index) {
                let title = data.flight + '[' + data.orgAirport + ' - ' + data.dstAirport + ']';
                this.initChart();

                let tmp = [];
                this.rankDatas.map(rank => {
                    if (rank.flight === data.flight) {
                        let ranking = rank.rank;
                        let day = parseInt(rank.date.substr(8), 10);
                        tmp.push([day, ranking]);
                    }
                });
                this.seriesData2 = tmp;
                this.makeChart(title);
            },
            resetInputFields () {
                let jsonData = null;
                let tmpFlights = [];
                let tmpOrgAirports = [];
                let tmpDstAirports = [];

                if (this.org === '华东') {
                    jsonData = this.eastData;
                } else {
                    jsonData = this.aviationData;
                }
                for (let dateKey in jsonData) {
                    let dateValue = jsonData[dateKey];
                    dateValue.map(rank => {
                        // 航班号
                        let flight = rank.fnum;
                        if (!util.oneOf(flight, tmpFlights)) {
                            tmpFlights.push(flight);
                        }

                        // 起飞机场
                        let orgAirport = rank.forg;
                        if (!util.oneOf(orgAirport, tmpOrgAirports)) {
                            tmpOrgAirports.push(orgAirport);
                        }

                        // 降落机场
                        let dstAirport = rank.fdst;
                        if (!util.oneOf(dstAirport, tmpDstAirports)) {
                            tmpDstAirports.push(dstAirport);
                        }
                    });
                }
                this.flights = tmpFlights;
                this.orgAirports = tmpOrgAirports;
                this.dstAirports = tmpDstAirports;

                this.flight = '';
                this.orgAirport = '';
                this.dstAirport = '';
            }
        }
    };
</script>

<style scoped>
    .main {
        /*border: 1px solid #dcdee2;*/
        /*width: 800px;*/
        height: 800px;
    }

    .split {
        border: 1px solid #dcdee2;
    }

    .list {
        padding: 5px;
    }

    .chart {
        width: 1200px;
        height: 800px;
    }
</style>
