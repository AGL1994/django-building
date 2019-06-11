from functools import wraps

from django.core.handlers.wsgi import WSGIRequest as Request
from django.views.decorators.http import require_http_methods
from pure_pagination import Paginator
from django.http import JsonResponse
from django.http.request import QueryDict

from building.serializers import model_serializer
from building.status import result_content, HTTP_200_OK
from building.utils import is_int, is_float, is_date
# from user.service import get_role_permission

require_GET = require_http_methods(["GET"])
require_PUT = require_http_methods(["PUT"])
require_POST = require_http_methods(["POST"])
require_DELETE = require_http_methods(["DELETE"])


def get_request(args):
    """
    获取request
    :param args:
    :return:
    """
    request = None
    if isinstance(args[0], Request):
        request = args[0]
    elif isinstance(args[1], Request):
        request = args[1]

    return request


# def permission(value):
#     """
#     权限控制
#     :param value:
#     :param func:
#     :return:
#     """
#
#     def permission_function(func):
#
#         @wraps(func)
#         def permission_handler(*args, **kwargs):
#             request = get_request(args)
#             try:
#                 token = request.META['HTTP_TOKEN']
#                 role_id = cache.get(token + '_role')
#                 if not role_id:
#                     raise Exception('登录过期')
#                 role_permission = get_role_permission(role_id)
#                 if value in role_permission:
#                     return func(*args, **kwargs)
#                 else:
#                     return JsonResponse(result_content(status='fail', msg='权限不足'), status=HTTP_401_UNAUTHORIZED)
#             except Exception as e:
#                 print(e)
#                 return JsonResponse(result_content(status='fail', msg='登录过期'), status=HTTP_401_UNAUTHORIZED)
#
#         return permission_handler
#
#     return permission_function


def request_aider(filter_list=(), choices=True, contains=(), excepts=('updated', 'deleted')):
    """
    过去过滤的查询条件，自动分页与序列化
    :param choices:
    :param foreign:
    :param contains:
    :param excepts:
    :param filter_list:
    :return:
    """

    def all_params(func):

        @wraps(func)
        def _do(*args, **kwargs):
            # 获取request
            # request = [arg for arg in args if isinstance(arg, Request)]
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            params = get_filter_dict(request, filter_list)
            result = func(*args, **kwargs, params=params)
            num = request.GET.get('num', 10)
            page = request.GET.get('page', 1)
            num = num if num else 10
            page = page if page else 1
            query_page = get_query_page(result, int(num), int(page),
                                        choices=choices, contains=contains, excepts=excepts)
            return JsonResponse(result_content(status='success', content=query_page), status=HTTP_200_OK)

        return _do

    return all_params


def query_aider(filter_list=()):
    """
    查询条件（仅包含查询条件 不做分页和序列化）
    :param filter_list:
    :return:
    """
    def all_params(func):

        @wraps(func)
        def _do(*args, **kwargs):
            # 获取request
            # request = [arg for arg in args if isinstance(arg, Request)]
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            params = get_filter_dict(request, filter_list)
            func(*args, **kwargs, params=params)
        return _do

    return all_params


def page_aider(func):
    """
    自动分页
    :return:
    """
    @wraps(func)
    def _do(*args, **kwargs):
        # 获取request
        # request = [arg for arg in args if isinstance(arg, Request)]
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        result = func(*args, **kwargs)
        num = request.GET.get('num', 10)
        page = request.GET.get('page', 1)
        num = num if num else 10
        page = page if page else 1
        query_page = get_query_page(result, int(num), int(page))
        return JsonResponse(result_content(status='success', content=query_page), status=HTTP_200_OK)

    return _do


def get_query_page(result, num, page, choices=True, contains=(), excepts=('updated', 'deleted')):
    """
    获取分页数据
    :param foreign:
    :param choices:
    :param contains:
    :param excepts:
    :param num:
    :param page:
    :param result:
    :return:
    """
    p = Paginator(result, num)
    if p.num_pages < page:
        page = p.num_pages
    page_query = p.page(page)

    total = page_query.paginator.count
    result = {
        'num': num,
        'page': page,
        'total_page': total // num if total % num == 0 else total // num + 1,
        'has_next': page_query.has_next(),
        'has_prev': page_query.has_previous(),
        'total': total,
        'data': model_serializer(page_query.object_list, choices=choices,
                                 contains=contains, excepts=excepts)
    }
    return result


def get_params(request):
    """
    获取各个请求的参数
    :param request:
    :return:
    """
    if request.method == 'GET':
        params = request.GET
    elif request.method == 'POST':
        params = request.POST
    else:
        params = QueryDict(request.body)
    return params


def get_filter_dict(request, excepts):
    """
    获取过滤条件
    :param excepts: 需要排除的参数
    :param request:
    :return:
    """
    new_params = {}
    params = get_params(request)
    if params:
        # 去除空的参数
        params = {index: param for index, param in params.items() if param}
        excepts = ('page', 'num', 'csrfmiddlewaretoken') + excepts

        # 去掉需要过滤的参数
        all_key = params.keys()
        for key in excepts:
            if key in all_key:
                params.pop(key)

        for key, value in params.items():
            if key.startswith('int__'):
                if is_int(value):
                    new_params[key[5:]] = value
            elif key.startswith('float__'):
                if is_float(value):
                    new_params[key[7:]] = value
            elif key.startswith('date__'):
                if is_date(value):
                    new_params[key[6:]] = value
            elif key.startswith('datetime__'):
                if is_date(value):
                    new_params[key[10:]] = value
            else:
                new_params[key] = value

    return new_params
