from collections import Iterable
import time

from django.db import models


def _model_serializer(cls, choices, contains, excepts, foreign_dict={}):
    model_dict = []
    single = False
    if not isinstance(cls, Iterable):
        cls = (cls,)
        single = True
    for instance in cls:
        model_dict.append(_model_to_dict(instance, choices, contains, excepts, foreign_dict))

    if single:
        model_dict = model_dict[0]
    return model_dict


def model_serializer(cls, choices=True, contains=(), excepts=('updated', 'deleted')):
    """
    model转json
    :param choices: 是否自动转换choices
    :param cls: 需要转的model
    :param contains: 包含的字段 （若有此参数，则只返回次参数包含字段）
    :param excepts: 排除字段，默认排除更新时间与deleted  （若有此参数，则排除此参数内的字段）
    :return:
    实现models转dict
    支持了时间格式转化, foreignKey, choice类型转义

    暂不支持 ManyToMany ManyToOne 等
    """
    try:
        foreign_dict = cls.query.select_related
    except Exception:
        foreign_dict = {}
    return _model_serializer(cls, choices, contains, excepts, foreign_dict)


def _model_to_dict(instance, choices, contains, excepts, foreign_dict):
    """
    model 转 dict
    :param foreign_dict:
    :param contains:
    :param excepts:
    :param instance:
    :return: dict
    """
    field_dict = {}
    foreign_list = foreign_dict.keys() if isinstance(foreign_dict, dict) else ()
    fields = instance._meta.fields
    for field in fields:
        name = field.name
        # 排除不需要的参数
        if contains and (name not in contains):
            continue
        if name in excepts:
            continue

        try:
            if isinstance(field, models.ForeignKey):
                if name in foreign_list:
                    value = getattr(instance, name)
                    foreign_list_child = foreign_dict.get(name)
                    value = _model_serializer(value, choices=choices, contains=contains,
                                                         excepts=excepts, foreign_dict=foreign_list_child)
                else:
                    value = getattr(instance, field.attname)
                    value = value if value else ''
                field_dict[name] = value
                continue

            else:
                value = getattr(instance, name)
                value = value if value else ''
        except Exception as e:
            field_dict[name] = ''
            continue

        if isinstance(field, models.DateTimeField):  # datetime
            field_dict[name] = value.strftime('%Y-%m-%d %H:%M:%S') if value else ''
        elif isinstance(field, models.DateField):  # date
            field_dict[name] = value.strftime('%Y-%m-%d') if value else ''
        else:  # 其他
            # 判断是否有choices
            if choices and hasattr(field, 'choices') and field.choices:
                f = getattr(instance, 'get_{}_display'.format(name))
                field_dict[name] = f()
            else:
                field_dict[name] = value
    return field_dict


def is_int(value):
    try:
        int(value)
        return True
    except Exception:
        return False


def is_float(value):
    try:
        float(value)
        return True
    except Exception:
        return False


def is_date(value):
    try:
        time.strptime(value, "%Y-%m-%d")
        return True
    except:
        return False


def is_datetime(value):
    try:
        time.strptime(value, "%Y-%m-%d %H:%M:%S")
        return True
    except:
        return False