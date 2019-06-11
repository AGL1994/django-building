django-building
===============
### 开始使用
1. 安装::
```
pip install django-building
```
2. 添加 "building" 到settings的INSTALLED_APPS中::
```
    INSTALLED_APPS = [
        ...
        'building',
    ]
```
### 功能列表
    1. model序列化
    2. 快捷查询分页功能
    3. 日志
    4. 自动化文档
    5. 权限（文档待更新）
### 功能介绍
一. model序列化
----------
公司项目最开始使用的非前后端分离的方式，由于业务需求页面完全重做并采用前后端分离的方式，项目迎来了一次重构。最开始选用技术的时候看重了drf，但是由于项目本身已经完成，只需要改动部分业务需求与接口返回，drf的序列化需要对每个model写一个serializers，对于我们来说工作量有点大了（项目有近100个model）。故自己封装了一个序列化功能，以下为相关示例。如果查询数据量很大，不推荐此方法。因为方法使用了反射、循环与递归（特别是需要查询外键值或外键的外键值时），性能上显得不佳。
```Python
model_serializer(cls, choices=True, contains=(), excepts=('updated', 'deleted')) 
""" 
model转json 
:param choices: 是否自动转换choices 
:param cls: 需要转的model 
:param contains: 包含的字段 （若有此参数，则只返回次参数包含字段），同时作用于子model与父model
:param excepts: 排除字段，默认排除更新时间与deleted  （若有此参数，则排除此参数内的字段），同时作用于子model与父model
:return: list(dict)
""" 
```

###### 实现models转dict 
###### 支持了时间格式转化, foreignKey, choice类型转义 
###### 暂不支持ManyToOne ManyToMany
###### 未保证序列化的执行效率，减少外键带来的SQL查询，需要获取ForeignKey的内容，请使用select_related()方法，若不使用，则会返回ForeignKey的值

#### 代码示例
##### 以下为测试model
```
class User(AbstractUser):
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name="电话号码")
    name = models.CharField(max_length=45, blank=True, null=True, verbose_name="姓名")
    sex = models.IntegerField(blank=True, null=True, choices=((1, "男"), (2, '女')), default=1)
    birthday = models.DateField(blank=True, null=True, verbose_name="出生日期")
    avatar = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name="用户头像")
    status = models.SmallIntegerField(default=1, choices=USER_STATUS, verbose_name="状态")
    created = models.DateTimeField(verbose_name=u"创建时间", editable=False, auto_now_add=True)
    updated = models.DateTimeField(verbose_name=u"修改时间", editable=False, auto_now=True)
    deleted = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'tb_user'
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

class UserWx(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    openid = models.CharField(max_length=50, verbose_name='openid')
    nickname = models.CharField(max_length=255, verbose_name='用户昵称')
    sex = models.IntegerField(choices=USER_SEX, verbose_name='性别')
    province = models.CharField(max_length=255, verbose_name='省份')
    city = models.CharField(max_length=255, verbose_name='城市')
    country = models.CharField(max_length=255, verbose_name='国家')
    head_img_url = models.CharField(max_length=500, verbose_name='用户头像url')
    privilege = models.CharField(max_length=1000, verbose_name='用户特权信息')
    created = models.DateTimeField(verbose_name=u"创建时间", editable=False, auto_now_add=True)
    updated = models.DateTimeField(verbose_name=u"修改时间", editable=False, auto_now=True)
    deleted = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = '用户微信信息'
        db_table = 'tb_user_wx'
```
### model_serializer使用
#### 用法1
```Python
    from building.status import result_content, HTTP_200_OK
    user_wx = UserWx.objects.all()
    user_wx_dict = model_serializer(user_wx)
    return JsonResponse(result_content(status='success', content=user_wx_dict), status=HTTP_200_OK)
```
#### 返回1
```Json
{
    "status": "success",
    "msg": "",
    "content": [
        {
            "id": 1,
            "user": 1,  // 未使用select_related()，返回的字段值
            "openid": "test123456",
            "nickname": "测试微信昵称",
            "sex": "男", // 默认会转换choice的值
            "province": "四川",
            "city": "成都",
            "country": "中国",
            "head_img_url": "image",
            "privilege": "1",
            "created": "2019-06-10 15:50:18"
        }
    ]
}
```
#### 用法2
```Python
    from building.status import result_content, HTTP_200_OK
    user_wx = UserWx.objects.select_related('user').all()
    user_wx_dict = model_serializer(user_wx, choices=False, excepts=('password', 'phone'))  # 不显示密码和手机号
    return JsonResponse(result_content(status='success', content=user_wx_dict), status=HTTP_200_OK)
```
#### 返回2
```Json
{
    "status": "success",
    "msg": "",
    "content": [
        {
            "id": 1,
            "user": { // 使用了select_related(), 返回了user的详细信息
                "id": 1,
                "last_login": "2019-05-07 18:22:43",
                "is_superuser": true,
                "username": "admin",
                "first_name": "",
                "last_name": "",
                "email": "45612345@qq.com",
                "is_staff": true,
                "is_active": true,
                "date_joined": "2018-06-08 16:24:54",
                "name": "李小龙",
                "sex": 1, // 使用choices=False, 阻止自动传换值
                "birthday": "2018-11-19",
                "avatar": "",
                "status": 1,
                "created": "2018-06-08 16:24:54",
                "updated": "2018-06-08 16:24:54",
                "deleted": ""
            },
            "openid": "test123456",
            "nickname": "测试微信昵称",
            "sex": 1,
            "province": "四川",
            "city": "成都",
            "country": "中国",
            "head_img_url": "image",
            "privilege": "1",
            "created": "2019-06-10 15:50:18",
            "updated": "2019-06-10 15:50:24",
            "deleted": ""
        }
    ]
}
```
二. 快捷查询分页
----------
在实际的项目中，我们通常会有许许多多的查询功能，尤其是在后台管理系统中，会有大量的表格与条件查询。我们需要对大量的查询条件做数据验证与查询映射，烦不胜烦。所以，针对这种重复性的工作，博主封装了以下方法。主要思路，将前台查询条件的name值直接命名为filter()所需要的查询条件。<br>
##### 装饰器参数说明
```
def request_aider(filter_list=(), choices=True, contains=(), excepts=('updated', 'deleted')):
    """
    过去过滤的查询条件，自动分页与序列化
    :param choices: 同 model_serializer
    :param foreign: 同 model_serializer
    :param contains: 同 model_serializer
    :param excepts: 同 model_serializer
    :param filter_list: 过滤查询条件请求
    :return:
    """
```
#### 快捷分页查询功能通过装饰器实现
```Python
@request_aider(excepts=('phone', ))
def user_list_view(request, params):

    self_query = {
        'deleted': 0,
        'user__deleted': 0
    }
    user_wx = UserWx.objects.select_related('user').filter(**self_query, **params)
    return user_wx  # 直接返回查询结果即可
```
#### 请求参数
```
int__user__sex: 2
user__name: '李小龙'
user__nickname__contains: '测试'
nun: 10 // 分页数据，每页显示数据，默认为10
page: 1 // 分页数据，当前页码，默认为1
```
##### 参数说明：
    1. 前缀为数据类型，目前支持 int__, float__, date__, datetime__, string__(默认，字符串可不写)
    2. 后部分为model查询条件
    3. num, page 可不填
    4. filter_list作用，以上可知，我们直接采用前台参数的name值作为数据查询条件，某些参数并不会作为查询条件，比如分页数据(num, page)，获取安全验证(csrfmiddlewaretoken)，我们可使用filter_list 来排除它们。（默认排除了 num, page, csrfmiddlewaretoken三个字段）
##### 返回数据
```Json
{
    "status": "success",
    "msg": "",
    "content": {
        "num": 2, // 当前每页显示数量
        "page": 1, // 当前页码
        "total_page": 2, // 总页码
        "has_next": true, // 是否有上一页
        "has_prev": false, // 是否有下一页
        "total": 3, // 总条数
        "data": [
            {
                "id": 2,
                "user": {
                    "id": 56,
                    "password": "pbkdf2_sha256$100000$OzZ0A14PTn6P$fAYCOCUJyiK5y6puLVRQ47ouphWV/xCQHv6s2jTBVD4=",
                    "last_login": "",
                    "is_superuser": "",
                    "username": "",
                    "first_name": "",
                    "last_name": "",
                    "email": "",
                    "is_staff": "",
                    "is_active": true,
                    "date_joined": "2018-07-17 13:36:11",
                    "name": "廖辉",
                    "sex": "女",
                    "birthday": "1990-01-01",
                    "avatar": "",
                    "status": "正常",
                    "created": "2018-07-17 13:36:11",
                    "updated": "2018-07-17 13:36:11",
                    "deleted": ""
                },
                "openid": "testffd",
                "nickname": "测试微信昵称2",
                "sex": "男",
                "province": "四川",
                "city": "成都",
                "country": "中国",
                "head_img_url": "image",
                "privilege": "1",
                "created": "2019-06-10 15:50:18",
                "updated": "2019-06-10 15:50:24",
                "deleted": ""
            },
            {
                "id": 4,
                "user": {
                    "id": 69,
                    "password": "pbkdf2_sha256$100000$PxN3kCTj8O7O$PkiQJNhhJysILZJgLzoMUZGjD6vLD9P6v+vArUJ2h6o=",
                    "last_login": "",
                    "is_superuser": "",
                    "username": "",
                    "first_name": "",
                    "last_name": "",
                    "email": "",
                    "is_staff": "",
                    "is_active": true,
                    "date_joined": "2018-07-17 13:55:12",
                    "name": "柠檬",
                    "sex": "女",
                    "birthday": "2014-08-08",
                    "avatar": "",
                    "status": "正常",
                    "created": "2018-07-17 13:55:12",
                    "updated": "2018-07-17 13:55:12",
                    "deleted": ""
                },
                "openid": "testfbb",
                "nickname": "测试微信昵称4",
                "sex": "男",
                "province": "四川",
                "city": "成都",
                "country": "中国",
                "head_img_url": "image",
                "privilege": "1",
                "created": "2019-06-10 15:50:18",
                "updated": "2019-06-10 15:50:24",
                "deleted": ""
            }
        ]
    }
}
```
###### @request_aider()集成了 查询、序列化、分页功能，另分装了单独的装饰来分别实现上述功能
###### @query_aider(filter_list=()) 查询
###### @page_aider 分页功能

三. 日志功能
--------------
日志功能延用了django的日志管理，仅仅是支持了阿里云日志服务，使用方法和django自带日志区别不大。如果日志没有这方面需求的，建议使用django自带的日志。
##### django日志配置
```
# 日志路径
BASE_LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(BASE_LOG_DIR):
    os.makedirs(BASE_LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
       'standard': {
            'format': '%(message)s'}  #日志格式
    },
    'filters': {
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'request_handler': {
            'level':'INFO',
            'class':'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_LOG_DIR, 'request.log'),
            'backupCount': 5,
            'formatter':'standard',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['request_handler', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'request': {
            'handlers': ['request_handler', 'console'],
            'level': 'INFO',
            'propagate': True
        }
    }
}
```
##### 阿里云相关配置
在setting.py文件中配置相关参数
```Python
END_POINT = ''  # 阿里云日志服务入口
ACCESS_KEY_ID = ''  # key_Id
ACCESS_KEY = ''  # key
PROJECT = ''  # 日志project
LOG_TYPE = LOCAL_LOG  # 日志服务开关，LOCAL_LOG(只使用本地日志), SERVER_LOG(只使用阿里云日志), BOTH_LOG(同时使用本地日志与阿里云日志)
```
##### 使用方式
```Python
from building.build_log import Log
log = Log('request')
log.info('这是info信息')
log.error()
log.warning()
log.debug()
# 下方为日志打印信息
# time:2019-06-10 03:13:12 file:academic_affairs.views function:put lineno:131 log_type:info 【message:这是info信息】
```
日志打印的时间、文件、方法、行号、类型目前不可配置。

四、自动化文档
-----------
根据注释来自动生成文档（由于项目采用前后端分离的方式，文档内容只返回了相关数据，页面会在以后上传）
##### 使用方式
    接口名称 请求方法
    :p 参数名称 参数类型 是否必填 参数说明
    :r 返回参数名称 参数类型 是否必填 参数说明
    :json 返回数据示例
```Python
def get(self, request, school_id, params, data_permission=None):
    """
    教室列表 GET
    :p title__contains string 否 教室名称查询
    :p int__max__lte int 否 教室最大人数小于
    :p int__max__gte int 否 教室最大人数大于于
    :p num int 否 每页显示数量
    :p page int 否 当前页码
    :r num int 是 每页显示套数
    :r page int 是 当前页码
    :r total_page int 是 总页数
    :r has_next boolean 是 是否有下一页
    :r has_prev boolean 是 是否有上一页
    :r total int 是 数据总条数
    :r data list 是 数据
    :r id int 是 教室id
    :r title string 是 教室名称
    :r status string 是 教室状态
    :r remark string 是 教室备注
    :r created datetime 是 教室创建时间
    :json
    {
        "status": "success",
        "msg": "",
        "content": {
            "num": 10,
            "page": 1,
            "total_page": 1,
            "has_next": false,
            "has_prev": false,
            "total": 2,
            "data": [
                {
                    "id": 10,
                    "title": "知行",
                    "max": 10,
                    "status": "可用",
                    "remark": "这是第一个教室",
                    "created": "2019-06-05 04:58:46"
                },
                {
                    "id": 11,
                    "title": "问天",
                    "max": 100,
                    "status": "可用",
                    "remark": "这是第一个100人的大教室",
                    "created": "2019-06-05 05:09:56"
                }
            ]
        }
    }
    """
```
##### 接口返回数据示例
```Json
{
    "url": "/affairs/classroom",
    "api": [
        {
            "desc": "教室列表",  // 接口名称
            "method": "GET",  // 请求方法
            "params": [
                {
                    "param": "title__contains",  // 参数 title__contains
                    "type": "string",  // 参数类型
                    "must": "否",  // 是否必填
                    "desc": "教室名称查询"  // 参数描述
                },
                {
                    "param": "int__max__lte",
                    "type": "int",
                    "must": "否",
                    "desc": "教室最大人数小于"
                },
                {
                    "param": "int__max__gte",
                    "type": "int",
                    "must": "否",
                    "desc": "教室最大人数大于于"
                },
                {
                    "param": "num",
                    "type": "int",
                    "must": "否",
                    "desc": "每页显示数量"
                },
                {
                    "param": "page",
                    "type": "int",
                    "must": "否",
                    "desc": "当前页码"
                }
            ],
            "result": [
                {
                    "param": "num",
                    "type": "int",
                    "must": "是",
                    "desc": "每页显示套数"
                },
                {
                    "param": "page",
                    "type": "int",
                    "must": "是",
                    "desc": "当前页码"
                },
                {
                    "param": "total_page",
                    "type": "int",
                    "must": "是",
                    "desc": "总页数"
                },
                {
                    "param": "has_next",
                    "type": "boolean",
                    "must": "是",
                    "desc": "是否有下一页"
                },
                {
                    "param": "has_prev",
                    "type": "boolean",
                    "must": "是",
                    "desc": "是否有上一页"
                },
                {
                    "param": "total",
                    "type": "int",
                    "must": "是",
                    "desc": "数据总条数"
                },
                {
                    "param": "data",
                    "type": "list",
                    "must": "是",
                    "desc": "数据"
                },
                {
                    "param": "id",
                    "type": "int",
                    "must": "是",
                    "desc": "教室id"
                },
                {
                    "param": "title",
                    "type": "string",
                    "must": "是",
                    "desc": "教室名称"
                },
                {
                    "param": "status",
                    "type": "string",
                    "must": "是",
                    "desc": "教室状态"
                },
                {
                    "param": "remark",
                    "type": "string",
                    "must": "是",
                    "desc": "教室备注"
                },
                {
                    "param": "created",
                    "type": "datetime",
                    "must": "是",
                    "desc": "教室创建时间"
                }
            ],
            "json": {
                "status": "success",
                "msg": "",
                "content": {
                    "num": 10,
                    "page": 1,
                    "total_page": 1,
                    "has_next": false,
                    "has_prev": false,
                    "total": 2,
                    "data": [
                        {
                            "id": 10,
                            "title": "知行",
                            "max": 10,
                            "status": "可用",
                            "remark": "这是第一个教室",
                            "created": "2019-06-05 04:58:46"
                        },
                        {
                            "id": 11,
                            "title": "问天",
                            "max": 100,
                            "status": "可用",
                            "remark": "这是第一个100人的大教室",
                            "created": "2019-06-05 05:09:56"
                        }
                    ]
                }
            }
        },
        {
            "desc": "添加教室",
            "method": "POST",
            "params": [
                {
                    "param": "title",
                    "type": "string",
                    "must": "是",
                    "desc": "教室名称"
                },
                {
                    "param": "max",
                    "type": "int",
                    "must": "是",
                    "desc": "教室最大人数"
                },
                {
                    "param": "status",
                    "type": "int",
                    "must": "是",
                    "desc": "教室状态"
                },
                {
                    "param": "remark",
                    "type": "string",
                    "must": "否",
                    "desc": "教室备注信息"
                }
            ],
            "result": []
        },
        {
            "desc": "修改教室信息",
            "method": "PUT",
            "params": [
                {
                    "param": "classroom_id",
                    "type": "int",
                    "must": "是",
                    "desc": "教室id"
                },
                {
                    "param": "title",
                    "type": "string",
                    "must": "是",
                    "desc": "教室名称"
                },
                {
                    "param": "max",
                    "type": "int",
                    "must": "是",
                    "desc": "教室最大人数"
                },
                {
                    "param": "status",
                    "type": "int",
                    "must": "是",
                    "desc": "教室状态"
                },
                {
                    "param": "remark",
                    "type": "string",
                    "must": "否",
                    "desc": "教室备注信息"
                }
            ],
            "result": []
        },
        {
            "desc": "删除教室",
            "method": "DELETE",
            "params": [
                {
                    "param": "classroom_id",
                    "type": "int",
                    "must": "是",
                    "desc": "教室id"
                }
            ],
            "result": []
        }
    ]
},
```
##### 页面渲染截图
暂无图片

五. 权限系统
待更新
    
