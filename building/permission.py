# import json
#
# from django.core.cache import cache
# from django.db.models import Q
# from django.forms import model_to_dict
# from django.conf import settings
#
# from base.db_variables import PERMISSION_MENU, PERMISSION_BUTTON, SCHOOL_ROLE_STUDENT, SCHOOL_ROLE_PARENT
# from base.models import RolePermission, Permission, Menu, SchoolUserRole
# from base.utils import model_serializer
#
#
# def get_role_menu(role):
#     """
#     获取角色菜单
#     :param role:
#     :return:
#     """
#     menu_json = cache.get('role_menu_{}'.format(role))
#     if not menu_json:
#         first_menu = find_first_menu(role)
#         menu = find_second_menu(first_menu)
#         cache.set('role_menu_{}'.format(role), json.dumps(menu), timeout=None)
#     else:
#         menu = json.loads(menu_json)
#     return menu
#
#
# def get_role_menu_permission(role):
#     """
#     获取角色菜单与权限
#     :param role:
#     :return:
#     """
#     menu_permission_json = cache.get('role_menu_permission_{}'.format(role))
#     if not menu_permission_json:
#         first_menu = find_first_menu(role)
#         menu_permission = find_second_menu_permission(first_menu)
#         cache.set('role_menu_permission_{}'.format(role), json.dumps(menu_permission), timeout=None)
#     else:
#         menu_permission = json.loads(menu_permission_json)
#     return menu_permission
#
#
# def get_role_permission(role):
#     """
#     角色所有权限
#     :param role:
#     :return:
#     """
#     role_permission_json = cache.get('role_permission_{}'.format(role))
#     if not role_permission_json:
#         role_permission_list = list(
#             RolePermission.objects.values_list('permission_id', flat=True).filter(role_id=role, deleted=0))
#         role_permission = list(Permission.objects.values_list('code', flat=True).filter(id__in=role_permission_list,
#                                                                                         code__isnull=False))
#         role_permission_json = json.dumps(role_permission)
#         cache.set('role_permission_{}'.format(role), role_permission_json, timeout=None)
#     else:
#         role_permission = json.loads(role_permission_json)
#
#     return role_permission
#
#
# def set_school_role_info(school_id, token, role_id):
#     """
#     设置学校角色信息
#     :param role_id:
#     :param school_id:
#     :param token:
#     :return:
#     """
#     cache.set(token + '_school', school_id, settings.USER_SESSION_TIME_OUT)
#     cache.set(token + '_role', role_id, school_id, settings.USER_SESSION_TIME_OUT)
#
#
# def choose_school(role_id, school_id, token, user_id):
#     """
#     选择学校
#     :return:
#     """
#     # 信息合法
#     menus = get_role_menu(role_id)
#     permissions = get_role_permission(role_id)
#
#     schools = get_user_school(user_id)
#     # 去掉已选择的学校
#     schools = [school for school in schools if str(school['school_id']) != str(school_id)
#                or str(school['role_id']) != str(role_id)]
#
#     result_data = {
#         'menus': menus,
#         'permissions': permissions,
#         'other_school': schools
#     }
#
#     set_school_role_info(school_id, token, role_id)
#     return result_data
#
#
# def get_user_school(user_id):
#     """
#     获取用户所有的学校信息
#     :param user_id:
#     :return:
#     """
#     school_info = cache.get('{}_school_list'.format(user_id))
#     if not school_info:
#         school_user_role = SchoolUserRole.objects.select_related('school_user', 'school_user__school', 'role').filter(
#             ~Q(role__temp=SCHOOL_ROLE_STUDENT), ~Q(role__temp=SCHOOL_ROLE_PARENT),
#             school_user__user_id=user_id, school_user__school__deleted=0, deleted=0,
#             school_user__user__deleted=0, school_user__deleted=0)
#
#         school_info = [{'school_id': sur.school_user.school_id, 'school': sur.school_user.school.title,
#                         'role': sur.role.title, 'role_id': sur.role_id} for sur in school_user_role]
#         cache.set('{}_school_list'.format(user_id), school_info, settings.USER_SESSION_TIME_OUT)
#
#     return school_info
#
#
# def find_first_menu(role):
#     """
#     一级菜单
#     :param role:
#     :return:
#     """
#     role_permission_list = list(
#         RolePermission.objects.values_list('permission_id', flat=True).filter(role_id=role, deleted=0))
#     permission_model_list = Permission.objects.filter(id__in=role_permission_list).select_related('menu').order_by('menu__index')
#
#     menu = []
#     for permission in permission_model_list:
#         # 找出菜单
#         if permission.type == PERMISSION_MENU:
#             if permission.menu.pid_id == -1:  # 一级菜单
#                 menu.append(model_to_dict(permission.menu))
#     return menu
#
#
# def find_second_menu(menus):
#     """
#     二级菜单
#     :param menus:
#     :return:
#     """
#     menus_b = menus
#     for index, menu in enumerate(menus):
#         m = Menu.objects.filter(pid_id=menu['id'], deleted=0)
#         menus_b[index]['sub'] = model_serializer(m, choices=False)
#         # menus_b[index]['sub'] = model_to_dict(m)
#
#     return menus_b
#
#
# def find_second_menu_permission(menus):
#     """
#     二级菜单(附带菜单下的权限)
#     :param menus:
#     :return:
#     """
#     menus_b = menus
#     for index, menu in enumerate(menus):
#         second_menu = Menu.objects.filter(pid_id=menu['id'], deleted=0)
#         second_menu = model_serializer(second_menu, choices=False)
#         # second_menu = model_to_dict(second_menu)
#
#         second_menu_b = second_menu
#         for ind, sm in enumerate(second_menu):
#             permission = Permission.objects.filter(menu_id=sm['id'], deleted=0).first()
#             second_menu_b[ind]['permission_id'] = permission.id
#
#             permission_list = Permission.objects.filter(pid_id=permission.id, deleted=0, type=PERMISSION_BUTTON)
#             permission_list = model_serializer(permission_list, choices=False)
#             # permission_list = model_to_dict(permission_list)
#             second_menu_b[ind]['permission'] = permission_list
#
#         menus_b[index]['sub'] = second_menu_b
#
#     return menus_b