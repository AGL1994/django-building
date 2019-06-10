from django.db import models

# 资源类型
PERMISSION_MENU, PERMISSION_BUTTON = 1, 2
PERMISSION_SOURCE_TYPE = (
    (PERMISSION_MENU, '菜单'),
    (PERMISSION_BUTTON, '按钮'),
)


class Role(models.Model):
    title = models.CharField(max_length=255, verbose_name="角色")
    remark = models.CharField(max_length=1000, verbose_name="备注", blank=True, null=True, default=None)
    created = models.DateTimeField(verbose_name=u"创建时间", editable=False, auto_now_add=True)
    updated = models.DateTimeField(verbose_name=u"修改时间", editable=False, auto_now=True)
    deleted = models.IntegerField(default=0)

    class Meta:
        db_table = "tb_role"
        verbose_name = "角色"
        verbose_name_plural = verbose_name


class Menu(models.Model):
    pid = models.ForeignKey('self', verbose_name='父菜单', default=-1, on_delete=models.DO_NOTHING, db_constraint=False)
    title = models.CharField(max_length=50, verbose_name='名称')
    index = models.IntegerField(default=3, verbose_name='菜单排列顺序')
    icon = models.CharField(max_length=100, verbose_name='icon', null=True, blank=True)
    url = models.CharField(max_length=100, verbose_name='url', null=True, blank=True)
    created = models.DateTimeField(verbose_name=u"创建时间", editable=False, auto_now_add=True)
    updated = models.DateTimeField(verbose_name=u"修改时间", editable=False, auto_now=True)
    deleted = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'tb_menu'
        verbose_name = '菜单'


class Permission(models.Model):
    """
    权限表
    """
    pid = models.ForeignKey('self', verbose_name='父权限', default=-1, on_delete=models.DO_NOTHING, db_constraint=False)
    menu = models.ForeignKey(Menu, verbose_name='菜单', default=-1, on_delete=models.CASCADE, db_constraint=False)
    title = models.CharField(max_length=100, verbose_name='功能名称')
    code = models.CharField(max_length=50, verbose_name='权限代码', null=True, blank=True)
    type = models.IntegerField(choices=PERMISSION_SOURCE_TYPE, default=PERMISSION_BUTTON, verbose_name='类型（标注页面提现出来的类型）')
    created = models.DateTimeField(verbose_name=u"创建时间", editable=False, auto_now_add=True)
    updated = models.DateTimeField(verbose_name=u"修改时间", editable=False, auto_now=True)
    deleted = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'tb_permission'
        verbose_name = '权限'


class RolePermission(models.Model):
    """
    角色权限表
    """
    role = models.ForeignKey(Role, verbose_name='角色', on_delete=models.CASCADE, default=None)
    permission = models.ForeignKey(Permission, verbose_name='权限', on_delete=models.CASCADE, default=None)
    created = models.DateTimeField(verbose_name=u"创建时间", editable=False, auto_now_add=True)
    updated = models.DateTimeField(verbose_name=u"修改时间", editable=False, auto_now=True)
    deleted = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'tb_role_permission'
        verbose_name = '角色权限表'
