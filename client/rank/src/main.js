import Vue from 'vue';
import iView from 'iview';
import App from './app.vue';
import 'iview/dist/styles/iview.css';

import echarts from 'echarts';
Vue.prototype.$echarts = echarts;

Vue.use(iView);

new Vue({
    el: '#app',
    render: h => h(App)
});
