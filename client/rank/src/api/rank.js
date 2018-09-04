import {service} from '@/libs/request';

export function fetchEast () {
    return service({
        method: 'get',
        url: '/data/east.json'
    });
}

export function fetchAviation () {
    return service({
        method: 'get',
        // url: '/data/aviation.json'
        url: '/data/aviation_rank_list.json'
    });
}

export function fetchReason () {
    return service({
        method: 'get',
        url: '/data/UnnormalReason.json'
    });
}
