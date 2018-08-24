#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <json-c/json.h>
#include <time.h>

const char *AVIATION_AIRPORT[] = {
        "ZBAA", "ZSPD", "ZGGG", "ZUUU",
        "ZPPP", "ZGSZ", "ZSSS", "ZLXY",
        "ZUCK", "ZSHC", "ZSAM", "ZSNJ",
        "ZGHA", "ZHHH", "ZHCC", "ZSQD",
        "ZWWW", "ZBTJ", "ZJHK"
};
const char *EAST_AIRPORT[] = {
        "ZSPD", "ZSSS", "ZSNJ", "ZSHC",
        "ZSAM", "ZSQD", "ZSFZ", "ZSNT"
};
const char *LOGIN_URL_PTR = "http://fisc.variflight.com/v1/user/login";
const char *LOGIN_POST_PTR = "LoginForm[username]=cdhk&LoginForm[password]=cdhk2017";
const char *RANK_URL_REGEX_PTR = "http://fisc.variflight.com/v1/east/index?token=%s";
const char *RANK_POST_REGEX_PTR = "airport=%s&flightNumber=EU&minNumber=4&startDay=%s&endDay=%s&cancel=1";

typedef struct st_chunk
{
    char *memory;
    size_t size;
}chunk;

static size_t write_memory_callback(void *contents, size_t size, size_t nmemb, void *userp);
int spider_execute(chunk *chk_ptr, const char *url_ptr, const char *post_ptr);
void pick_token(const char *json_ptr, char **token_ptr_ptr);
void pick_rank(const char *json_ptr);
void now_date(char *date_ptr);
time_t make_timet(const char *src_time);
void make_time_by_offset_hour(const char *src_time, char *dst_time, int offset_hour);

int main()
{
    chunk chk;
    char end_date[15] = {0};
    char start_aviation_date[15] = {0};
    char start_east_date[15] = {0};

    // date
    now_date(end_date);
    strncpy(start_aviation_date, end_date, 6);
    strcpy(start_aviation_date + 6, "01000000");
    make_time_by_offset_hour(end_date, start_east_date, -60 * 24);
    strcpy(start_east_date + 6, "01000000");
    strcpy(end_date + 8, "000000");
    printf("%s %s %s\n", end_date, start_aviation_date, start_east_date);

    // login
    chk.memory = malloc(1);
    chk.size = 0;
    char *token_ptr = NULL;
    if(spider_execute(&chk, LOGIN_URL_PTR, LOGIN_POST_PTR) == 0)
    {
        pick_token(chk.memory, &token_ptr);

    }
    free(chk.memory);

    // data
    if(token_ptr != NULL)
    {
        chk.memory = malloc(1);
        chk.size = 0;
        char data_url[1024] = {0};
        sprintf(data_url, RANK_URL_REGEX_PTR, token_ptr);
        char data_post[1024] = {0};
        sprintf(data_post, RANK_POST_REGEX_PTR, "ZSPD", "2018-07-01", "2018-08-20");
        if(spider_execute(&chk, data_url, data_post) == 0)
        {
            pick_rank(chk.memory);
        }
        free(chk.memory);
        free(token_ptr);
    }

    return 0;
}

void now_date(char *date_ptr)
{
    time_t t = time(0);
    strftime(date_ptr, 14, "%Y%m%d%H%M%S", localtime(&t));
//    make_time_by_offset_hour(date_ptr, date_ptr, -24);
}

time_t make_timet(const char *src_time)
{
    struct tm *src_t = NULL;
    time_t src_timet = 0L;

    src_timet = time((time_t *)NULL);
    src_t = localtime(&src_timet);

    char year[5] = {0};
    strncpy(year, src_time, 4);
    src_t->tm_year = atoi(year) - 1900;

    char month[3] = {0};
    strncpy(month, src_time + 4, 2);
    src_t->tm_mon = atoi(month) - 1;

    char day[3] = {0};
    strncpy(day, src_time + 6, 2);
    src_t->tm_mday = atoi(day);

    char hour[3] = {0};
    strncpy(hour, src_time + 8, 2);
    src_t->tm_hour = atoi(hour);

    char minute[3] = {0};
    strncpy(minute, src_time + 10, 2);
    src_t->tm_min = atoi(minute);

    char second[3] = {0};
    strncpy(second, src_time + 12, 2);
    src_t->tm_sec = atoi(second);

    src_timet = mktime(src_t);

    return src_timet;
}

void make_time_by_offset_hour(const char *src_time, char *dst_time, int offset_hour)
{
    time_t src_timet = 0L;
    struct tm *dst_t = NULL;
    time_t dst_timet = 0L;

    src_timet = make_timet(src_time);
    dst_timet = src_timet + offset_hour * 3600L;
    dst_t = localtime(&dst_timet);
    sprintf(dst_time, "%d%02d%02d%02d0000", dst_t->tm_year + 1900, dst_t->tm_mon + 1, dst_t->tm_mday, dst_t->tm_hour);
}

static size_t write_memory_callback(void *contents, size_t size, size_t nmemb, void *userp)
{
    size_t real_size = size * nmemb;
    chunk *mem = (chunk *)userp;

    mem->memory = realloc(mem->memory, mem->size + real_size + 1);
    if(mem->memory == NULL) {
        /* out of memory! */
        printf("not enough memory (realloc returned NULL)\n");
        return 0;
    }

    memcpy(&(mem->memory[mem->size]), contents, real_size);
    mem->size += real_size;
    mem->memory[mem->size] = 0;

    return real_size;
}

int spider_execute(chunk *chk_ptr, const char *url_ptr, const char *post_ptr)
{
    int ret = 0;
    CURL *curl_handle;
    CURLcode res;
//    struct curl_slist *headers_ptr = NULL;

    curl_global_init(CURL_GLOBAL_ALL);
//    headers_ptr = curl_slist_append(headers_ptr, "Content-Type:application/x-www-form-urlencoded; charset=UTF-8");
//    headers_ptr = curl_slist_append(headers_ptr, "Origin:http://fisc.variflight.com");
//    headers_ptr = curl_slist_append(headers_ptr, "Referer:http://fisc.variflight.com/fisc/index.html");
//    headers_ptr = curl_slist_append(headers_ptr, "User-Agent:Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36");

    curl_handle = curl_easy_init();
//    curl_easy_setopt(curl_handle, CURLOPT_HTTPHEADER, headers_ptr);
    curl_easy_setopt(curl_handle, CURLOPT_URL, url_ptr);
    curl_easy_setopt(curl_handle, CURLOPT_POST, 1);
    curl_easy_setopt(curl_handle, CURLOPT_POSTFIELDS, post_ptr);
    curl_easy_setopt(curl_handle, CURLOPT_WRITEFUNCTION, write_memory_callback);
    curl_easy_setopt(curl_handle, CURLOPT_WRITEDATA, (void *)chk_ptr);
    curl_easy_setopt(curl_handle, CURLOPT_VERBOSE, 0);

    res = curl_easy_perform(curl_handle);
    if(res != CURLE_OK)
    {
        fprintf(stderr, "curl_easy_perform() failed: %s\n",
                curl_easy_strerror(res));
        ret = -1;
    }
//    curl_slist_free_all(headers_ptr);
    curl_easy_cleanup(curl_handle);
    curl_global_cleanup();

    return ret;
}

void pick_token(const char *json_ptr, char **token_ptr_ptr)
{
    struct json_object *result_obj_ptr = NULL;
    result_obj_ptr = json_tokener_parse(json_ptr);
    if(result_obj_ptr != NULL)
    {
        struct json_object *message_obj_ptr = NULL;
        json_object_object_get_ex(result_obj_ptr, "message", &message_obj_ptr);
        if(message_obj_ptr != NULL)
        {
            const char *message_ptr = json_object_get_string(message_obj_ptr);
            if(strcmp(message_ptr, "Success") == 0)
            {
                struct json_object *data_obj_ptr = NULL;
                json_object_object_get_ex(result_obj_ptr, "data", &data_obj_ptr);
                if(data_obj_ptr != NULL)
                {
                    const char *data_ptr = json_object_get_string(data_obj_ptr);
                    *token_ptr_ptr = strdup(data_ptr);
                }
            }
        }
    }
    json_object_put(result_obj_ptr);
}

void pick_rank(const char *json_ptr)
{
    struct json_object *result_obj_ptr = NULL;
    result_obj_ptr = json_tokener_parse(json_ptr);
    if(result_obj_ptr != NULL)
    {
        struct json_object *message_obj_ptr = NULL;
        json_object_object_get_ex(result_obj_ptr, "message", &message_obj_ptr);
        if(message_obj_ptr != NULL)
        {
            const char *message_ptr = json_object_get_string(message_obj_ptr);
            if(strcmp(message_ptr, "Success") == 0)
            {
                struct json_object *data_obj_ptr = NULL;
                json_object_object_get_ex(result_obj_ptr, "data", &data_obj_ptr);
                if(data_obj_ptr != NULL)
                {
                    struct json_object_iterator it;
                    struct json_object_iterator it_end;
                    it = json_object_iter_begin(data_obj_ptr);
                    it_end = json_object_iter_end(data_obj_ptr);

                    while (!json_object_iter_equal(&it, &it_end)) {
                        struct json_object *rank_obj_ptr = json_object_iter_peek_value(&it);
                        const char *rank_ptr = json_object_get_string(rank_obj_ptr);
                        printf("%s\n", rank_ptr);
                        json_object_iter_next(&it);
                    }
                }
            }
        }
    }
    json_object_put(result_obj_ptr);
}