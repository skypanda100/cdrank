#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <json-c/json.h>
#include <time.h>
#include <unistd.h>

const char *PATH_PREFIX_PTR = "/usr/share/nginx/html/data";
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
const char *RANK_URL_REGEX_PTR = "http://fisc.variflight.com%s%s";
const char *RANK_POST_REGEX_PTR = "airport=%s&flightNumber=EU&minNumber=4&startDay=%s&endDay=%s&cancel=1";

typedef struct st_chunk
{
    char *memory;
    size_t size;
}chunk;

static size_t write_memory_callback(void *contents, size_t size, size_t nmemb, void *userp);
int spider_execute(chunk *chk_ptr, const char *url_ptr, const char *post_ptr);
void pick_token(const char *json_ptr, char **token_ptr_ptr);
void pick_rank(const char *json_ptr, struct json_object *array_obj_ptr);
void now_date(char *date_ptr);
time_t make_timet(const char *src_time);
void make_time_by_offset_hour(const char *src_time, char *dst_time, int offset_hour);

int main()
{
    daemon(0, 0);
    for(;;) {
        chunk chk;
        char date[15] = {0};
        char start_aviation_date[15] = {0};
        char start_east_date[15] = {0};
        char end_date[15] = {0};
        int east_airport_count = sizeof(EAST_AIRPORT) / sizeof(char *);
        int aviation_airport_count = sizeof(AVIATION_AIRPORT) / sizeof(char *);

        // date
        now_date(date);
        strncpy(end_date, date, 6);
        strcpy(end_date + 6, "01000000");
        strncpy(start_aviation_date, date, 6);
        strcpy(start_aviation_date + 6, "01000000");
        make_time_by_offset_hour(date, start_east_date, -60 * 24);
        strcpy(start_east_date + 6, "01000000");
        strcpy(date + 8, "000000");
//    strcpy(date + 6, "02000000");
        printf("%s %s %s %s\n", date, end_date, start_aviation_date, start_east_date);

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
            char data_url[1024] = {0};
            sprintf(data_url, RANK_URL_REGEX_PTR, "/v1/east/index?token=", token_ptr);
            char rank_start_date[11] = {0};
            char rank_end_date[11] = {0};
            char data_post[1024] = {0};

            // east data
            strncpy(rank_start_date, start_east_date, 4);
            strcat(rank_start_date, "-");
            strncpy(rank_start_date + strlen(rank_start_date), start_east_date + 4, 2);
            strcat(rank_start_date, "-");
            strncpy(rank_start_date + strlen(rank_start_date), start_east_date + 6, 2);

            struct json_object *east_obj_ptr = json_object_new_object();
            while(strcmp(end_date, date) <= 0)
            {
                struct json_object *east_date_array_obj_ptr = json_object_new_array();

                for(int i = 0;i < east_airport_count;i++)
                {
                    chk.memory = malloc(1);
                    chk.size = 0;

                    memset(data_post, 0, sizeof(data_post));
                    memset(rank_end_date, 0, sizeof(rank_end_date));

                    strncpy(rank_end_date, end_date, 4);
                    strcat(rank_end_date, "-");
                    strncpy(rank_end_date + strlen(rank_end_date), end_date + 4, 2);
                    strcat(rank_end_date, "-");
                    strncpy(rank_end_date + strlen(rank_end_date), end_date + 6, 2);

                    sprintf(data_post, RANK_POST_REGEX_PTR, EAST_AIRPORT[i], rank_start_date, rank_end_date);
                    printf("%s\n", data_post);

                    if(spider_execute(&chk, data_url, data_post) == 0)
                    {
                        pick_rank(chk.memory, east_date_array_obj_ptr);
                    }
                    free(chk.memory);
                }
                json_object_object_add(east_obj_ptr, rank_end_date, east_date_array_obj_ptr);

                make_time_by_offset_hour(end_date, end_date, 24);
            }
//        printf("%s\n", json_object_to_json_string(east_obj_ptr));
            char east_path[256] = {0};
            sprintf(east_path, "%s/east.json", PATH_PREFIX_PTR);
            json_object_to_file(east_path, east_obj_ptr);
            json_object_put(east_obj_ptr);

            // avaition data
            memset(data_url, 0, sizeof(data_url));
            sprintf(data_url, RANK_URL_REGEX_PTR, "/v1/aviation/index?token=", token_ptr);
            strncpy(end_date, date, 6);
            strcpy(end_date + 6, "01000000");

            memset(rank_start_date, 0, sizeof(rank_start_date));
            strncpy(rank_start_date, start_aviation_date, 4);
            strcat(rank_start_date, "-");
            strncpy(rank_start_date + strlen(rank_start_date), start_aviation_date + 4, 2);
            strcat(rank_start_date, "-");
            strncpy(rank_start_date + strlen(rank_start_date), start_aviation_date + 6, 2);

            struct json_object *aviation_obj_ptr = json_object_new_object();
            while(strcmp(end_date, date) <= 0)
            {
                struct json_object *aviation_date_array_obj_ptr = json_object_new_array();

                for(int i = 0;i < aviation_airport_count;i++)
                {
                    chk.memory = malloc(1);
                    chk.size = 0;

                    memset(data_post, 0, sizeof(data_post));
                    memset(rank_end_date, 0, sizeof(rank_end_date));

                    strncpy(rank_end_date, end_date, 4);
                    strcat(rank_end_date, "-");
                    strncpy(rank_end_date + strlen(rank_end_date), end_date + 4, 2);
                    strcat(rank_end_date, "-");
                    strncpy(rank_end_date + strlen(rank_end_date), end_date + 6, 2);

                    sprintf(data_post, RANK_POST_REGEX_PTR, AVIATION_AIRPORT[i], rank_start_date, rank_end_date);
                    printf("%s\n", data_post);

                    if(spider_execute(&chk, data_url, data_post) == 0)
                    {
                        pick_rank(chk.memory, aviation_date_array_obj_ptr);
                    }
                    free(chk.memory);
                }
                json_object_object_add(aviation_obj_ptr, rank_end_date, aviation_date_array_obj_ptr);

                make_time_by_offset_hour(end_date, end_date, 24);
            }
//        printf("%s\n", json_object_to_json_string(aviation_obj_ptr));
            char aviation_path[256] = {0};
            sprintf(aviation_path, "%s/aviation.json", PATH_PREFIX_PTR);
            json_object_to_file(aviation_path, aviation_obj_ptr);

            json_object_put(aviation_obj_ptr);

            free(token_ptr);
        }

        sleep(3600 * 2);
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

    curl_global_init(CURL_GLOBAL_ALL);

    curl_handle = curl_easy_init();
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

void pick_rank(const char *json_ptr, struct json_object *array_obj_ptr)
{
//    printf("json_str: %s\n", json_ptr);

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
                    if(json_object_get_type(data_obj_ptr) == json_type_array)
                    {
                        struct array_list *al = json_object_get_array(data_obj_ptr);
                        const int al_len = array_list_length(al);
                        for(int i = 0;i < al_len;i++)
                        {
                            struct json_object *rank_obj_ptr = array_list_get_idx(al, i);
                            json_object_array_add(array_obj_ptr, json_object_get(rank_obj_ptr));
//                            const char *rank_ptr = json_object_get_string(rank_obj_ptr);
//                            printf("%s\n", rank_ptr);
                        }
                    }
                    else
                    {
                        struct json_object_iterator it;
                        struct json_object_iterator it_end;
                        it = json_object_iter_begin(data_obj_ptr);
                        it_end = json_object_iter_end(data_obj_ptr);

                        while (!json_object_iter_equal(&it, &it_end)) {
                            struct json_object *rank_obj_ptr = json_object_iter_peek_value(&it);
                            json_object_array_add(array_obj_ptr, json_object_get(rank_obj_ptr));
                            json_object_iter_next(&it);
//                            const char *rank_ptr = json_object_get_string(rank_obj_ptr);
//                            printf("%s\n", rank_ptr);
                        }
                    }

                }
            }
        }
    }
    json_object_put(result_obj_ptr);
}