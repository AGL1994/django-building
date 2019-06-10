django-building
===============
### 开始使用
1. Add "building" to your INSTALLED_APPS setting like this::
    ```
    INSTALLED_APPS = [
        ...
        'building',
    ]
    ```
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
    """ <br>

    ### 实现models转dict <br>
    ### 支持了时间格式转化, foreignKey, choice类型转义 <br>
    ### 暂不支持ManyToOne ManyToMany
    ### 未保证序列化的执行效率，减少外键带来的SQL查询，需要获取ForeignKey的内容，请使用select_related()方法，若不使用，则会返回ForeignKey的值

    ### 代码示例
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
            #managed = True
            db_table = 'tb_user'
            verbose_name = "用户信息"
            verbose_name_plural = verbose_name
    ```

    