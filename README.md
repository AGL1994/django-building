django-building
===============
### 开始使用
1. 添加 "building" 到settings的INSTALLED_APPS中::
    ```
    INSTALLED_APPS = [
        ...
        'building',
    ]
    ```
### 功能介绍
一. model序列化
----------
```Python
model_serializer(cls, choices=True, contains=(), excepts=('updated', 'deleted')) 
""" 
model转json 
:param choices: 是否自动转换choices 
:param cls: 需要转的model 
:param contains: 包含的字段 （若有此参数，则只返回次参数包含字段），同时作用于子model与父model
:param excepts: 排除字段，默认排除更新时间与deleted  （若有此参数，则排除此参数内的字段），同时作用于子model与父model
:return: json
""" 
```

#### 实现models转dict 
#### 支持了时间格式转化, foreignKey, choice类型转义 
#### 暂不支持ManyToOne ManyToMany
#### 未保证序列化的执行效率，减少外键带来的SQL查询，需要获取ForeignKey的内容，请使用select_related()方法，若不使用，则会返回ForeignKey的值

#### 代码示例
##### 以下为测试model
    ```Python
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
1. 用法1
    ```Python
    user_wx = UserWx.objects.all()
    user_wx_dict = model_serializer(user_wx)
    return JsonResponse(result_content(status='success', content=user_wx_dict), status=HTTP_200_OK)
    ```
以下为返回数据
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
2. 用法2
    ```
    user_wx = UserWx.objects.select_related('user').all()
    user_wx_dict = model_serializer(user_wx, choices=False, excepts=('password', 'phone'))  # 不显示密码和手机号
    return JsonResponse(result_content(status='success', content=user_wx_dict), status=HTTP_200_OK)
    ```
以下为返回数据
    ```
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

    
