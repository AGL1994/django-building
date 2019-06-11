import json
from importlib import import_module

from django.conf import settings
from django.http import JsonResponse
from django.urls import URLResolver, URLPattern


def doc_view(request):
    """
    获取接口文档 GET
    @param
        request string 请求

    @return
        result_code boolean 返回结果
    """
    patterns = get_all_urlpatterns()
    return JsonResponse({'status': 'success', 'content': patterns})


def get_all_urlpatterns():
    urlconf_module = import_module(settings.ROOT_URLCONF)
    patterns = getattr(urlconf_module, 'urlpatterns', urlconf_module)
    urls = all_url(patterns)
    api_doc = []
    for url in urls:
        doc = {'url': url[0], 'api': []}
        function_list = []
        if not hasattr(url[1], 'view_class'):
            function_list.append(url[1])
        else:
            view_class = url[1].view_class
            if hasattr(view_class, 'get'):
                function_list.append(getattr(view_class, 'get'))
            if hasattr(view_class, 'post'):
                function_list.append(getattr(view_class, 'post'))
            if hasattr(view_class, 'put'):
                function_list.append(getattr(view_class, 'put'))
            if hasattr(view_class, 'delete'):
                function_list.append(getattr(view_class, 'delete'))

        for fun in function_list:
            desc = fun.__doc__
            if not desc:
                continue
            desc_list = desc.split('\n')
            parse_urls(desc_list, doc)
        api_doc.append(doc)

    return api_doc


def parse_urls(desc_list, doc):
    descs = desc_list[1].strip().split(' ')
    api_doc = {
        'desc': descs[0],
        'method': descs[1] if len(descs) > 1 else '',
        'params': [],
        'result': []
    }
    for index, desc in enumerate(desc_list[1:]):
        try:
            desc = desc.strip()
            # 去掉单行空格字符串
            if not desc:
                continue

            params = desc.split(' ')
            if params[0] == ':p':
                api_doc['params'].append(
                    {
                        'param': params[1],
                        'type': params[2],
                        'must': params[3],
                        'desc': params[4]
                    }
                )
            elif params[0] == ':r':
                api_doc['result'].append(
                    {
                        'param': params[1],
                        'type': params[2],
                        'must': params[3],
                        'desc': params[4]
                    }
                )
            elif params[0] == ':json':
                return_json = desc_list[index + 2:]
                r = ''.join(return_json)
                if not r:
                    break
                r = r.replace('\'', '\"')
                rj = json.loads(r)
                api_doc['json'] = rj
        except Exception as e:
            print(e)
            print(index, desc)
    doc['api'].append(api_doc)
    #
    # return doc


def all_url(patterns):
    urls = []
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            route = pattern.pattern._route
            urls += resolver(pattern.url_patterns, pre=route)
        elif isinstance(pattern, URLPattern):
            urls.append(
                _url(pattern)
            )
    return urls


def resolver(pattern, pre):
    url = []
    for p in pattern:
        url.append(
            _url(p, pre=pre)
        )
    return url


def _url(pattern, pre=''):
    return '/' + pre + pattern.pattern._route, pattern.callback