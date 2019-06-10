django-building
===============
1. Add "building" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'building',
    ]

model序列化
----------
1. model_serializer(cls, choices=True, contains=(), excepts=('updated', 'deleted')) <br>
    """ <br>
    model转json <br>
    :param choices: 是否自动转换choices <br>
    :param cls: 需要转的model <br>
    :param contains: 包含的字段 （若有此参数，则只返回次参数包含字段）<br>
    :param excepts: 排除字段，默认排除更新时间与deleted  （若有此参数，则排除此参数内的字段）<br>
    :return: json
    实现models转dict <br>
    支持了时间格式转化, foreignKey, choice类型转义 <br>

    暂不支持 ManyToMany ManyToOne 等 <br>
    """ <br>