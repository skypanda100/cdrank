import axios from 'axios';
import env from '../../build/env';
import { Message } from 'iview';

const service = axios.create({
    baseURL: env.host,
    timeout: 60000,
    responseType: 'json'
});

service.interceptors.request.use(config => {
    // config.headers['X-Token'] = getToken(); // 让每个请求携带token-- ['X-Token']为自定义key 请根据实际情况自行修改
    return config;
}, error => {
    Promise.reject(error);
});

service.interceptors.response.use(
    response => response,
    error => {
        Message.error({
            content: error.message,
            duration: 5
        });
        return Promise.reject(error);
    }
);

export {service};
